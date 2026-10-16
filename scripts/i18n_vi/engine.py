"""Batch translation engine: cache → batch → LLM → validate → retry with feedback.

An item is {"id", "en", "kind": "text"|"code", "key"?, "note"?}. A surface supplies a validator
`(item, vi) -> (fixed_vi, error|None)`; errors are fed back to the model on retry. Results are
cached per surface (keyed by id, invalidated when the English source changes), so a rerun only
translates new or changed strings.
"""

from __future__ import annotations

import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable

from llm import chat, parse_json_object
from prompts import system_prompt

CACHE_DIR = Path(__file__).resolve().parent / "cache"

Validator = Callable[[dict, str], "tuple[str, str | None]"]


class Cache:
    def __init__(self, surface: str):
        CACHE_DIR.mkdir(exist_ok=True)
        self.path = CACHE_DIR / f"{surface}.json"
        self.data: dict[str, dict] = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}
        self.lock = threading.Lock()

    @staticmethod
    def _note(item: dict) -> str | None:
        return item.get("base_note", item.get("note"))

    def get(self, item: dict) -> str | None:
        hit = self.data.get(item["id"])
        return hit["vi"] if hit and hit.get("en") == item["en"] and hit.get("note") == self._note(item) else None

    def put(self, item: dict, vi: str) -> None:
        with self.lock:
            self.data[item["id"]] = {"en": item["en"], "note": self._note(item), "vi": vi}

    def save(self) -> None:
        with self.lock:
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
            tmp.replace(self.path)


def _batches(items: list[dict], max_items: int, max_chars: int) -> list[list[dict]]:
    out, cur, size = [], [], 0
    for item in items:
        n = len(item["en"]) + len(item.get("note") or "") + 40
        if cur and (len(cur) >= max_items or size + n > max_chars):
            out.append(cur)
            cur, size = [], 0
        cur.append(item)
        size += n
    if cur:
        out.append(cur)
    return out


def _request(batch: list[dict], kind: str) -> dict[str, str]:
    payload = {"items": [{k: v for k, v in it.items() if k in ("id", "en", "key", "note") and v} for it in batch]}
    content, _usage = chat([
        {"role": "system", "content": system_prompt(kind)},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ])
    result = parse_json_object(content)
    table = result.get("t", result)
    return {str(k): v for k, v in table.items() if isinstance(v, str)}


def translate(surface: str, items: list[dict], validate: Validator, *, workers: int = 6,
              max_items: int = 50, max_chars: int = 6000, rounds: int = 4,
              batch_validate: Callable[[list[tuple[dict, str]]], list[tuple[str, str | None]]] | None = None,
              ) -> tuple[dict[str, str], dict[str, str]]:
    """Translate `items`; returns ({id: vi}, {id: last_error}) — the second map lists items that never
    passed validation (their best attempt is still returned in the first map when one exists)."""
    cache = Cache(surface)
    done: dict[str, str] = {}
    todo: list[dict] = []
    for item in items:
        hit = cache.get(item)
        if hit is not None:
            done[item["id"]] = hit
        else:
            todo.append(item)
    print(f"[{surface}] {len(items)} items: {len(done)} cached, {len(todo)} to translate", flush=True)

    failures: dict[str, str] = {}
    best: dict[str, str] = {}
    lock = threading.Lock()
    started = time.time()

    for round_no in range(rounds):
        if not todo:
            break
        by_kind: dict[str, list[dict]] = {}
        for item in todo:
            by_kind.setdefault(item["kind"], []).append(item)
        shrink = 2 ** round_no  # retries go out in smaller batches so feedback stays focused
        jobs = [(kind, b) for kind, group in by_kind.items()
                for b in _batches(group, max(1, max_items // shrink), max(1500, max_chars // shrink))]
        retry: list[dict] = []
        finished = 0

        def run(job):
            kind, batch = job
            try:
                return batch, _request(batch, kind), None
            except Exception as exc:  # transport/parse failure: whole batch retries
                return batch, {}, str(exc)

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(run, job) for job in jobs]
            for future in as_completed(futures):
                batch, table, error = future.result()
                pending: list[tuple[dict, str]] = []
                for item in batch:
                    vi = table.get(item["id"])
                    if vi is None:
                        with lock:
                            failures[item["id"]] = error or "missing from model output"
                        retry.append(item)
                    else:
                        pending.append((item, vi))
                verdicts = (batch_validate(pending) if batch_validate and pending
                            else [validate(item, vi) for item, vi in pending])
                for (item, _vi), (fixed, problem) in zip(pending, verdicts):
                    if problem:
                        with lock:
                            failures[item["id"]] = problem
                            best[item["id"]] = fixed
                        retry.append({**item, "feedback": problem})
                    else:
                        with lock:
                            done[item["id"]] = fixed
                            failures.pop(item["id"], None)
                        cache.put(item, fixed)
                finished += 1
                if finished % 10 == 0 or finished == len(jobs):
                    cache.save()
                    print(f"[{surface}] round {round_no + 1}: {finished}/{len(jobs)} batches, "
                          f"{len(done)}/{len(items)} done, {len(retry)} to retry, "
                          f"{time.time() - started:.0f}s", flush=True)
        cache.save()
        # Carry validator feedback into the next attempt's note.
        todo = []
        for item in retry:
            feedback = item.pop("feedback", None)
            base_note = item.get("base_note", item.get("note"))
            note = base_note
            if feedback:
                note = ((base_note + " ") if base_note else "") + f"PREVIOUS ATTEMPT REJECTED: {feedback}"
            todo.append({**item, "base_note": base_note, "note": note})

    unresolved = {item["id"]: failures.get(item["id"], "unknown") for item in todo}
    for item_id, vi in best.items():
        done.setdefault(item_id, vi)
    print(f"[{surface}] finished: {len(done)}/{len(items)} translated, {len(unresolved)} unresolved", file=sys.stderr)
    return done, unresolved
