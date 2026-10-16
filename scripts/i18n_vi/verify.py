"""Offline parity checks for the vi catalogs: the contracts upstream's pytest pins, without the
project environment. vi.yaml mirrors en.yaml (keys, {placeholders}, no literal backslash-n) and
vi.tui.yaml mirrors locales/_keys.tui.json. Exits 1 with the drift listed."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

LOCALES = Path(__file__).resolve().parents[2] / "locales"
PLACEHOLDER = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def flatten(node: dict, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in node.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            out.update(flatten(value, path))
        else:
            out[path] = value
    return out


def load(name: str):
    return yaml.safe_load((LOCALES / name).read_text(encoding="utf-8")) or {}


def main() -> None:
    problems: list[str] = []
    en, vi = flatten(load("en.yaml")), flatten(load("vi.yaml"))
    problems += [f"vi.yaml missing {key}" for key in sorted(en.keys() - vi.keys())]
    problems += [f"vi.yaml has extra {key}" for key in sorted(vi.keys() - en.keys())]
    for key, text in en.items():
        if key in vi and set(PLACEHOLDER.findall(text)) != set(PLACEHOLDER.findall(vi[key])):
            problems.append(f"vi.yaml {key}: placeholders differ from English")
    problems += [f"vi.yaml {key}: literal \\n" for key, text in vi.items() if "\\n" in text]

    tui_keys = set(json.loads((LOCALES / "_keys.tui.json").read_text(encoding="utf-8")))
    tui = set(load("vi.tui.yaml"))
    problems += [f"vi.tui.yaml missing {key}" for key in sorted(tui_keys - tui)]
    problems += [f"vi.tui.yaml has extra {key}" for key in sorted(tui - tui_keys)]

    for line in problems[:50]:
        print(line)
    if problems:
        sys.exit(f"{len(problems)} problem(s)")
    print(f"ok: vi.yaml {len(vi)} keys, vi.tui.yaml {len(tui)} keys")


if __name__ == "__main__":
    main()
