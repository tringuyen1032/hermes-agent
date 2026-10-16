"""Python core catalog: locales/en.yaml -> locales/vi.yaml."""

from __future__ import annotations

import glob
import json
import os
import re
import sys
from pathlib import Path

import yaml

from checks import check_text, fix_case
from engine import translate
from yamlout import emit_nested

REPO = Path(os.environ.get("HERMES_REPO") or Path(__file__).resolve().parents[2])
WORK = Path(__file__).resolve().parent / ".work"
LOCALES = REPO / "locales"

# Typed-answer lists: English words stay first (they always match anyway), Vietnamese synonyms follow,
# with and without diacritics. Matching is case-insensitive on comma-separated words.
HAND = {
    "approval.choose_long": "      [o] một lần  |  [s] phiên này  |  [a] luôn luôn  |  [d] từ chối",
    "approval.choose_short": "      [o] một lần  |  [s] phiên này  |  [d] từ chối",
    "approval.prompt_long": "      Lựa chọn [o/s/a/D]: ",
    "approval.prompt_short": "      Lựa chọn [o/s/D]: ",
    "approval.choose_smart_deny": "      [o] một lần  |  [d] từ chối",
    "approval.prompt_smart_deny": "      Lựa chọn [o/D]: ",
    "approval.smart_deny_once_inputs": "o,once,một lần,mot lan",
    "approval.smart_deny_deny_inputs": "d,deny,từ chối,tu choi,không,khong",
    "approval.inputs.approve": "approve,yes,ok,okay,confirm,y,đồng ý,dong y,có,co,duyệt,duyet,cho phép,cho phep,xác nhận,xac nhan",
    "approval.inputs.deny": "deny,no,reject,cancel,n,từ chối,tu choi,không,khong,hủy,huy",
    "approval.inputs.always": "always,approve always,always approve,luôn luôn,luon luon,luôn cho phép,luon cho phep",
    "approval.inputs.session": "session,approve session,session approve,phiên này,phien nay,cho phép phiên này,cho phep phien nay",
    "approval.inputs.confirm_once": "approve,approve once,once,yes,ok,confirm,đồng ý,dong y,một lần,mot lan,có,co,xác nhận,xac nhan",
    "approval.inputs.confirm_always": "always,always approve,remember,luôn luôn,luon luon,ghi nhớ,ghi nho",
    "approval.inputs.confirm_cancel": "cancel,nevermind,no,deny,hủy,huy,thôi,thoi,không,khong,từ chối,tu choi",
}

SECTION_NOTES = {
    "tips.": "A one-line tip shown at startup in the CLI/TUI.",
    "slash.": "Short description of a slash command, shown in the command menu (command names are not translated).",
    "explainer.": "Explanatory help text.",
}


def flatten(node, prefix=""):
    out = {}
    for k, v in node.items():
        path = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.update(flatten(v, path))
        else:
            out[path] = v
    return out


def keep_english_keys(en: dict[str, str]) -> set[str]:
    """Keys every bundled locale (or ≥11 of 16) leaves in English: format-only strings, identifiers and
    the model-facing kanban wake prompt. Translating those would change what the agent reads."""
    others = []
    for f in sorted(glob.glob(str(LOCALES / "*.yaml"))):
        name = os.path.basename(f)
        if name.startswith("_") or name in ("en.yaml", "vi.yaml") or ".tui." in name:
            continue
        others.append(flatten(yaml.safe_load(open(f, encoding="utf-8"))))
    keep = set()
    for k, v in en.items():
        same = sum(1 for o in others if o.get(k) == v)
        letters = re.sub(r"\{[^}]*\}|`[^`]*`|[^A-Za-z]", "", v)
        if same >= 11 or not letters:
            keep.add(k)
    keep.update(k for k in en if k.startswith("gateway.kanban.wake."))
    return keep


def main() -> None:
    tree = yaml.safe_load(open(LOCALES / "en.yaml", encoding="utf-8"))
    en = flatten(tree)
    keep = keep_english_keys(en)
    print(f"core: {len(en)} keys, {len(keep)} kept in English, {len(HAND)} hand-written", flush=True)

    items = []
    for k, v in en.items():
        if k in keep or k in HAND:
            continue
        note = next((n for p, n in SECTION_NOTES.items() if k.startswith(p)), None)
        items.append({"id": k, "key": k, "en": v, "kind": "text", "note": note})

    def validate(item, vi):
        return check_text(item["en"], vi)

    done, unresolved = translate("core", items, validate, workers=int(os.environ.get("WORKERS", "6")))
    values = {k: (HAND.get(k) or (en[k] if k in keep else fix_case(en[k], done.get(k, en[k])))) for k in en}
    out = REPO / "locales" / "vi.yaml"
    out.write_text("\n".join(emit_nested(tree, values)) + "\n", encoding="utf-8")
    (WORK / "reports").mkdir(parents=True, exist_ok=True)
    (WORK / "reports" / "core-unresolved.json").write_text(json.dumps(
        {k: {"en": en[k], "vi": done.get(k), "problem": p} for k, p in unresolved.items()},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out} ({len(values)} keys); unresolved: {len(unresolved)}")
    if unresolved:
        sys.exit(0)


if __name__ == "__main__":
    main()
