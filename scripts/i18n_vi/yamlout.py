"""Emit locale YAML in the house style: nested 2-space mapping, every value double-quoted."""

from __future__ import annotations

import re

_SAFE_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
_BOOLISH = {"y", "n", "yes", "no", "on", "off", "true", "false", "null", "~"}


def dq(value: str) -> str:
    out = []
    for ch in value:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\t":
            out.append("\\t")
        elif ch == "\r":
            out.append("\\r")
        elif ord(ch) < 0x20 or ch in "  ﻿":
            out.append(f"\\u{ord(ch):04x}")
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def key(k: str) -> str:
    return k if _SAFE_KEY.match(k) and k.lower() not in _BOOLISH else dq(k)


def emit_nested(tree: dict, values: dict[str, str], prefix: str = "", indent: int = 0) -> list[str]:
    """Mirror `tree` (the English nesting/order) with leaf values looked up by dotted path."""
    lines: list[str] = []
    pad = " " * indent
    for k, v in tree.items():
        path = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            lines.append(f"{pad}{key(str(k))}:")
            lines.extend(emit_nested(v, values, path, indent + 2))
        else:
            lines.append(f"{pad}{key(str(k))}: {dq(values[path])}")
    return lines


def emit_flat(values: dict[str, str], header: list[str]) -> str:
    lines = [f"# {line}" if line else "#" for line in header]
    lines.append("")
    lines.extend(f"{key(k)}: {dq(values[k])}" for k in sorted(values))
    return "\n".join(lines) + "\n"
