"""Minimal OpenAI-compatible client for the CLIProxyAPI endpoint (gpt-6-luna).

Endpoint and token come from VI_I18N_BASE_URL / VI_I18N_API_KEY, falling back to the
Codex CLI provider configured in ~/.codex/config.toml. The token is never printed.
"""

from __future__ import annotations

import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

MODEL = os.environ.get("VI_I18N_MODEL", "gpt-6-luna")


def _codex_provider() -> tuple[str, str]:
    cfg = (Path.home() / ".codex" / "config.toml").read_text(encoding="utf-8")
    base = re.search(r'\[model_providers\.codex_local_access\][^\[]*?base_url\s*=\s*"([^"]+)"', cfg, re.DOTALL)
    tok = re.search(r'experimental_bearer_token\s*=\s*"([^"]+)"', cfg)
    if not base or not tok:
        raise RuntimeError("CLIProxy provider not found in ~/.codex/config.toml; set VI_I18N_BASE_URL/VI_I18N_API_KEY")
    return base.group(1), tok.group(1)


def endpoint() -> tuple[str, str]:
    base = os.environ.get("VI_I18N_BASE_URL")
    key = os.environ.get("VI_I18N_API_KEY")
    if base and key:
        return base.rstrip("/"), key
    return _codex_provider()


class LLMError(RuntimeError):
    pass


def chat(messages: list[dict], *, json_mode: bool = True, reasoning_effort: str | None = "medium",
         timeout: int = 600, retries: int = 6) -> tuple[str, dict]:
    """One chat completion; returns (content, usage). Retries transport errors and 429/5xx."""
    base, key = endpoint()
    body: dict = {"model": MODEL, "messages": messages}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    if reasoning_effort:
        body["reasoning_effort"] = reasoning_effort
    data = json.dumps(body).encode()
    last: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(f"{base}/chat/completions", data=data,
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read())
            content = payload["choices"][0]["message"].get("content") or ""
            if not content.strip():
                raise LLMError("empty completion")
            return content, payload.get("usage") or {}
        except urllib.error.HTTPError as exc:
            detail = exc.read()[:300].decode(errors="replace")
            last = LLMError(f"HTTP {exc.code}: {detail}")
            if exc.code not in (408, 409, 425, 429, 500, 502, 503, 504, 520, 522, 524):
                raise last from exc
        except (urllib.error.URLError, TimeoutError, ConnectionError, LLMError, KeyError, json.JSONDecodeError) as exc:
            last = exc
        time.sleep(min(60, (2 ** attempt) * 2 + random.random() * 3))
    raise LLMError(f"giving up after {retries} attempts: {last}")


def parse_json_object(content: str) -> dict:
    """The model is asked for a bare JSON object; tolerate code fences or stray prose."""
    text = content.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


def ping() -> None:
    """Exit non-zero unless the endpoint answers and offers MODEL (run before any work starts)."""
    base, key = endpoint()
    req = urllib.request.Request(f"{base}/models", headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        ids = {model.get("id") for model in json.loads(resp.read()).get("data", [])}
    if MODEL not in ids:
        sys.exit(f"{MODEL} is not offered by {base}")
    print(f"ok: {MODEL} at {base}")


if __name__ == "__main__":
    if sys.argv[1:] != ["--ping"]:
        sys.exit("usage: python llm.py --ping")
    ping()
