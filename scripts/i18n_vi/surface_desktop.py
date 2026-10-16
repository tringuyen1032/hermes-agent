"""Desktop catalog (apps/desktop/src/i18n/en.ts, dumped to desktop-en.json) -> vi.ts + intro-vi.ts.

Also exposes `translate_leaves()` / `node_validator()` for the plugin and web catalogs, which use the
same leaf format.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

from checks import check_text, fix_case
from engine import translate
from tsgen import Raw, build_tree, emit_value

REPO = Path(os.environ.get("HERMES_REPO") or Path(__file__).resolve().parents[2])
WORK = Path(__file__).resolve().parent / ".work"
I18N = REPO / "apps" / "desktop" / "src" / "i18n"
NODE = os.environ.get("NODE_BIN", "node")
WORKERS = int(os.environ.get("WORKERS", "6"))

# Arguments that are identifiers, not display text (catalog-completeness.test.ts IDENTIFIER_ARGS).
IDENTIFIER_ARGS = {"settings.toolsets.webCapabilitySelectedMessage": [1]}

PREFIX_NOTES = {
    "settings.fieldLabels.": "Label of a settings field (short noun phrase).",
    "settings.fieldDescriptions.": "Help text shown under a settings field.",
    "appTour.": "Step of the guided app tour.",
    "keybinds.actions.": "Name of an action in the keyboard-shortcuts list (short, verb-first).",
    "tips.": "Tip card shown in the app.",
}


def note_for(path: str) -> str | None:
    return next((n for p, n in PREFIX_NOTES.items() if path.startswith(p)), None)


def node_validator(identifier_args: dict[str, list[int]] | None = None):
    identifier_args = identifier_args or {}

    def run(pending):
        payload = [{"id": item["id"], "en": item["en"], "vi": vi,
                    "identifierArgs": identifier_args.get(item["id"], [])} for item, vi in pending]
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp, "in.json"), Path(tmp, "out.json")
            src.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            proc = subprocess.run([NODE, str(Path(__file__).with_name("validate-fns.mjs")), str(REPO), str(src), str(dst)],
                                  capture_output=True, text=True, check=False)
            if proc.returncode != 0 or not dst.exists():
                print(f"validator crashed: {proc.stderr[-400:]}", flush=True)
                return [(vi, "could not be validated — return a simpler valid arrow function") for _item, vi in pending]
            results = {r["id"]: r for r in json.loads(dst.read_text(encoding="utf-8"))}
        return [(results[item["id"]]["fixed"], results[item["id"]]["problem"]) for item, _vi in pending]

    return run


def translate_leaves(surface: str, leaves: list[dict], *, skip_top: set[str] = frozenset(),
                     identifier_args: dict[str, list[int]] | None = None):
    """Translate string/array/function leaves. Returns ({path: value}, unresolved) where value is a
    str, a list[str] or a Raw function source, keyed by the JSON-encoded segment list."""
    text_items, code_items = [], []
    for leaf in leaves:
        segs = leaf["segs"]
        if segs[0] in skip_top:
            continue
        path = ".".join(segs)
        if leaf["kind"] == "string":
            if leaf["value"].strip():
                text_items.append({"id": path, "key": path, "en": leaf["value"], "kind": "text", "note": note_for(path)})
        elif leaf["kind"] == "array":
            for i, element in enumerate(leaf["value"]):
                text_items.append({"id": f"{path}#{i}", "key": path, "en": element, "kind": "text",
                                   "note": "One entry of a rotating list (e.g. composer placeholder)."})
        elif leaf["kind"] == "function":
            code_items.append({"id": path, "key": path, "en": leaf["source"], "kind": "code"})

    text_done, text_bad = translate(f"{surface}-text", text_items, lambda item, vi: check_text(item["en"], vi),
                                    workers=WORKERS)
    code_done, code_bad = translate(f"{surface}-code", code_items, None, workers=WORKERS, max_items=30,
                                    max_chars=5000, batch_validate=node_validator(identifier_args))

    values: dict[str, object] = {}
    for leaf in leaves:
        segs = leaf["segs"]
        if segs[0] in skip_top:
            continue
        key = json.dumps(segs, ensure_ascii=False)
        path = ".".join(segs)
        if leaf["kind"] == "string":
            values[key] = fix_case(leaf["value"], text_done.get(path, leaf["value"])) if leaf["value"].strip() else leaf["value"]
        elif leaf["kind"] == "array":
            values[key] = [fix_case(e, text_done.get(f"{path}#{i}", e)) for i, e in enumerate(leaf["value"])]
        elif leaf["kind"] == "function":
            values[key] = Raw(code_done.get(path, leaf["source"]))
        else:
            values[key] = leaf["value"]
    return values, {**text_bad, **code_bad}


def tree_from(leaves: list[dict], values: dict[str, object], *, overrides: dict[str, object] | None = None,
              skip_top: set[str] = frozenset()) -> dict:
    entries, seen_override = [], set()
    for leaf in leaves:
        segs = leaf["segs"]
        if overrides and segs[0] in overrides:
            if segs[0] not in seen_override:
                entries.append(([segs[0]], overrides[segs[0]]))
                seen_override.add(segs[0])
            continue
        if segs[0] in skip_top:
            continue
        entries.append((segs, values[json.dumps(segs, ensure_ascii=False)]))
    return build_tree(entries)


INTRO_NOTES = {
    "helpful": "Voice: warm, helpful assistant.",
    "concise": "Voice: terse and minimal.",
    "technical": "Voice: precise, technical, engineer-to-engineer.",
    "creative": "Voice: playful and imaginative.",
    "teacher": "Voice: patient teacher who explains.",
    "kawaii": "Voice: cute kawaii style; keep emoticons/kaomoji; cute Vietnamese tone.",
    "catgirl": "Voice: playful catgirl; keep 'nya'-style cat sounds (e.g. 'meo~', 'nya~') and emoticons.",
    "pirate": "Voice: pirate speak — render it as a fun Vietnamese pirate voice (thuyền trưởng, kho báu, ahoy…).",
    "shakespeare": "Voice: Shakespearean/archaic — use elegant, old-fashioned literary Vietnamese.",
    "surfer": "Voice: laid-back surfer slang — relaxed, chill Vietnamese.",
    "noir": "Voice: hard-boiled film-noir detective narration.",
    "uwu": "Voice: uwu-speak, very cute; keep emoticons like uwu, owo, >w<.",
    "philosopher": "Voice: reflective philosopher.",
    "hype": "Voice: high-energy hype; keep the ALL-CAPS emphasis on the same kind of words.",
    "none": "Voice: neutral, plain and polite.",
}

CUSTOM_EN = [
    "Send the task, file, or rough idea. I'll use your configured voice and keep the work grounded in this repo.",
    "Bring the context or the stuck part. I'll adapt to your configured personality.",
    "Send the problem, file, or idea. I'll follow the personality you've configured.",
    "Drop the task here. I'll keep the work grounded in the repo.",
    "Give me the context and I'll answer in {label} mode.",
]


def intro() -> None:
    rows = [json.loads(line) for line in (REPO / "apps/desktop/src/components/chat/intro-copy.jsonl")
            .read_text(encoding="utf-8").splitlines() if line.strip()]
    order: dict[str, list[str]] = {}
    for row in rows:
        order.setdefault(row["personality"], []).append(row["body"])
    items = []
    for personality, bodies in order.items():
        for i, body in enumerate(bodies):
            items.append({"id": f"stock.{personality}.{i}", "key": f"intro.{personality}", "en": body, "kind": "text",
                          "note": "Empty-chat greeting from the agent Hermes. " + INTRO_NOTES.get(personality, "")})
    for i, body in enumerate(CUSTOM_EN):
        items.append({"id": f"custom.{i}", "key": "intro.custom", "en": body, "kind": "text",
                      "note": "Empty-chat greeting for a user-defined personality; {label} is its name."})
    done, bad = translate("desktop-intro", items, lambda item, vi: check_text(item["en"], vi), workers=WORKERS)
    lines = ["import type { Translations } from './types'", "",
             "/** Display-only translations, in the stock JSONL's per-personality rotation order. */",
             "export const introVi: Translations['intro'] = {", "  stock: {"]
    for personality, bodies in order.items():
        vals = [done.get(f"stock.{personality}.{i}", b) for i, b in enumerate(bodies)]
        lines.append(f"    {personality}: {emit_value(vals, 2)},")
    lines.append("  },")
    custom = [done.get(f"custom.{i}", b) for i, b in enumerate(CUSTOM_EN)]
    rendered = []
    for text in custom:
        if "{label}" in text:
            rendered.append("`" + text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
                            .replace("{label}", "${label}") + "`")
        else:
            rendered.append(emit_value(text, 2))
    lines.append("  custom: label => [" + ", ".join(rendered) + "]")
    lines.append("}")
    (I18N / "intro-vi.ts").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote intro-vi.ts; unresolved: {len(bad)}")


def main() -> None:
    leaves = json.load(open(WORK / "desktop-en.json", encoding="utf-8"))
    values, unresolved = translate_leaves("desktop", leaves, skip_top={"intro"}, identifier_args=IDENTIFIER_ARGS)
    tree = tree_from(leaves, values, overrides={"intro": Raw("introVi")})
    body = emit_value(tree, 0)
    header = [
        "// Tiếng Việt (vi) desktop catalog — a complete overlay over English, so every key is",
        "// translated here; a key added to en.ts later falls back to English until this file catches up.",
        "import { defineLocale, type TranslationOverrides } from './define-locale'",
        "import { introVi } from './intro-vi'",
        "",
    ]
    text = "\n".join(header) + f"\nexport const viOverrides = {body} satisfies TranslationOverrides\n\n" \
        "export const vi = defineLocale(viOverrides)\n"
    (I18N / "vi.ts").write_text(text, encoding="utf-8")
    (WORK / "reports").mkdir(parents=True, exist_ok=True)
    (WORK / "reports" / "desktop-unresolved.json").write_text(json.dumps(unresolved, ensure_ascii=False, indent=1),
                                                       encoding="utf-8")
    print(f"wrote vi.ts; unresolved: {len(unresolved)}")
    intro()


if __name__ == "__main__":
    main()
