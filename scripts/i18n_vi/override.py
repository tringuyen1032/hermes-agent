"""Pin a reviewed translation into a surface cache, so regeneration keeps it.

Usage: python override.py <cache-surface> <id> <vietnamese>      (e.g. desktop-text firstRun.intro.plan "…")
       python override.py <cache-surface> --file edits.json      ({id: vietnamese, ...})
The entry must already exist (it carries the English source the cache is keyed on).
"""

from __future__ import annotations

import json
import sys

from engine import Cache


def main() -> None:
    surface = sys.argv[1]
    if sys.argv[2] == "--file":
        edits = json.load(open(sys.argv[3], encoding="utf-8"))
    else:
        edits = {sys.argv[2]: sys.argv[3]}
    cache = Cache(surface)
    missing = [k for k in edits if k not in cache.data]
    if missing:
        sys.exit(f"not in cache/{surface}.json: {missing}")
    for key, vi in edits.items():
        cache.data[key]["vi"] = vi
    cache.save()
    print(f"{surface}: pinned {len(edits)} translation(s)")


if __name__ == "__main__":
    main()
