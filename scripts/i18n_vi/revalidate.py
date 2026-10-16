"""Re-run the function validator over cached translations; evict failures so they get re-translated.

Usage: python revalidate.py [--dry] [surface ...]     (default surfaces: desktop kanban bots web)
"""

from __future__ import annotations

import json
import sys

from engine import Cache
from surface_desktop import IDENTIFIER_ARGS, node_validator


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--dry"]
    dry = "--dry" in sys.argv
    for surface in args or ["desktop", "kanban", "bots", "web"]:
        cache = Cache(f"{surface}-code")
        pending = [({"id": k, "en": v["en"]}, v["vi"]) for k, v in cache.data.items()]
        verdicts = node_validator(IDENTIFIER_ARGS)(pending) if pending else []
        bad = {item["id"]: problem for (item, _), (_, problem) in zip(pending, verdicts) if problem}
        print(f"{surface}-code: {len(pending)} cached, {len(bad)} failing")
        for key, problem in bad.items():
            print(f"  {key}: {problem[:260]}")
            if not dry:
                del cache.data[key]
        if not dry:
            cache.save()


if __name__ == "__main__":
    main()
