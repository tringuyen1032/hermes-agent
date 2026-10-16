"""Emit nested TypeScript object literals from catalog leaves (Prettier normalizes layout afterwards)."""

from __future__ import annotations

import json
import re

_IDENT = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")


class Raw(str):
    """A value emitted verbatim (function source, identifier reference)."""


def ts_string(value: str) -> str:
    out = []
    for ch in value:
        if ch == "\\":
            out.append("\\\\")
        elif ch == "'":
            out.append("\\'")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif ch in "  " or ord(ch) < 0x20:
            out.append(f"\\u{ord(ch):04x}")
        else:
            out.append(ch)
    return "'" + "".join(out) + "'"


def ts_key(key: str) -> str:
    return key if _IDENT.match(key) else ts_string(key)


def build_tree(entries: list[tuple[list[str], object]]) -> dict:
    """[(segs, value)] -> nested dict preserving first-seen order."""
    root: dict = {}
    for segs, value in entries:
        node = root
        for seg in segs[:-1]:
            node = node.setdefault(seg, {})
        node[segs[-1]] = value
    return root


def emit_value(value, indent: int) -> str:
    pad = "  " * indent
    if isinstance(value, Raw):
        return str(value)
    if isinstance(value, str):
        return ts_string(value)
    if isinstance(value, list):
        return "[" + ", ".join(emit_value(v, indent + 1) for v in value) + "]"
    if isinstance(value, dict):
        if not value:
            return "{}"
        inner = ",\n".join(f"{pad}  {ts_key(k)}: {emit_value(v, indent + 1)}" for k, v in value.items())
        return "{\n" + inner + "\n" + pad + "}"
    return json.dumps(value)
