"""TUI catalog (ui-tui/src/i18n/en.ts, dumped to tui-en.json) -> locales/vi.tui.yaml."""

from __future__ import annotations

import glob
import json
import os
from pathlib import Path

import yaml

from checks import check_text, fix_case
from engine import translate
from yamlout import emit_flat

REPO = Path(os.environ.get("HERMES_REPO") or Path(__file__).resolve().parents[2])
WORK = Path(__file__).resolve().parent / ".work"
LOCALES = REPO / "locales"
HEADER = [
    "Hermes TUI (ui-tui) strings — Tiếng Việt",
    "Flat dotted keys; every key from locales/_keys.tui.json. Function-valued en entries use",
    "positional {0}, {1} placeholders.",
]


def main() -> None:
    leaves = json.load(open(WORK / "tui-en.json", encoding="utf-8"))
    en: dict[str, str] = {}
    sources: dict[str, str] = {}
    for leaf in leaves:
        if leaf["kind"] == "function":
            en[leaf["path"]] = leaf["template"]
            sources[leaf["path"]] = leaf["source"]
        else:
            en[leaf["path"]] = leaf["value"]

    packs = []
    for f in sorted(glob.glob(str(LOCALES / "*.tui.yaml"))):
        if os.path.basename(f) != "vi.tui.yaml":
            packs.append(yaml.safe_load(open(f, encoding="utf-8")) or {})
    keep = {k for k, v in en.items() if sum(1 for p in packs if p.get(k) == v) >= 11}
    print(f"tui: {len(en)} keys, {len(keep)} kept in English", flush=True)

    items = []
    for k, v in en.items():
        if k in keep:
            continue
        note = None
        if k in sources:
            note = ("Rendered output of a function; {0}, {1}… are its arguments in order — keep each one. "
                    f"Function source: {sources[k][:600]}")
        items.append({"id": k, "key": k, "en": v, "kind": "text", "note": note})

    done, unresolved = translate("tui", items, lambda item, vi: check_text(item["en"], vi),
                                 workers=int(os.environ.get("WORKERS", "6")))
    values = {k: (en[k] if k in keep else fix_case(en[k], done.get(k, en[k]))) for k in en}
    out = LOCALES / "vi.tui.yaml"
    out.write_text(emit_flat(values, HEADER), encoding="utf-8")
    (WORK / "reports").mkdir(parents=True, exist_ok=True)
    (WORK / "reports" / "tui-unresolved.json").write_text(json.dumps(
        {k: {"en": en[k], "vi": done.get(k), "problem": p} for k, p in unresolved.items()},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out} ({len(values)} keys); unresolved: {len(unresolved)}")


if __name__ == "__main__":
    main()
