"""Desktop plugin bundles (kanban, hermes-bots + canonical groups) and the web dashboard -> vi."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from surface_desktop import REPO, WORK, translate_leaves, tree_from
from tsgen import Raw, emit_value

PLUGINS = REPO / "apps" / "desktop" / "src" / "plugins"
REGISTER_DOC = "/** Registered via `ctx.i18n.register` at plugin load (disposer tracked). */\n"


def load(name: str) -> list[dict]:
    return json.load(open(WORK / f"{name}-en.json", encoding="utf-8"))


def insert_before_register(path: Path, decl: str, map_old: str, map_new: str) -> None:
    src = path.read_text(encoding="utf-8")
    if "\nconst vi: " in src:
        src = re.sub(r"\nconst vi: [\s\S]*?\n}\n\n(?=/\*\* Registered via)", "\n", src)
    assert REGISTER_DOC in src, path
    src = src.replace(REGISTER_DOC, decl + "\n\n" + REGISTER_DOC, 1)
    if map_new not in src:
        assert map_old in src, (path, map_old)
        src = src.replace(map_old, map_new, 1)
    path.write_text(src, encoding="utf-8")


def kanban(unresolved: dict) -> None:
    leaves = load("kanban")
    values, bad = translate_leaves("kanban", leaves)
    unresolved.update({f"kanban:{k}": v for k, v in bad.items()})
    body = emit_value(tree_from(leaves, values), 0)
    insert_before_register(PLUGINS / "kanban" / "i18n.ts", f"const vi: KanbanMessages = {body}",
                           "{ en, ja, zh, 'zh-hant': zhHant }", "{ en, ja, zh, 'zh-hant': zhHant, vi }")


def canonical(unresolved: dict) -> None:
    leaves = load("canonical")
    values, bad = translate_leaves("canonical", leaves)
    unresolved.update({f"canonical:{k}": v for k, v in bad.items()})
    body = emit_value(tree_from(leaves, values), 1)
    path = PLUGINS / "hermes-bots" / "canonical-group-locales.ts"
    src = path.read_text(encoding="utf-8")
    src = re.sub(r",\n  vi: \{[\s\S]*?\n  \}(?=\n\} satisfies)", "", src)
    tail = "\n} satisfies Record<string, CanonicalGroupMessages>"
    assert tail in src
    src = src.replace("\n  }" + tail, "\n  },\n  vi: " + body + tail, 1)
    path.write_text(src, encoding="utf-8")


def bots(unresolved: dict) -> None:
    leaves = load("bots")
    values, bad = translate_leaves("bots", leaves, skip_top={"canonical"})
    unresolved.update({f"bots:{k}": v for k, v in bad.items()})
    tree = tree_from(leaves, values, overrides={"canonical": Raw("CANONICAL_GROUP_LOCALES.vi")})
    body = emit_value(tree, 0)
    insert_before_register(PLUGINS / "hermes-bots" / "i18n.ts", f"const vi: BotsMessages = {body}",
                           "  'zh-hant': zhHant,\n", "  'zh-hant': zhHant,\n  vi,\n")


def web(unresolved: dict) -> None:
    leaves = load("web")
    values, bad = translate_leaves("web", leaves)
    unresolved.update({f"web:{k}": v for k, v in bad.items()})
    body = emit_value(tree_from(leaves, values), 0)
    out = REPO / "web" / "src" / "i18n" / "vi.ts"
    out.write_text('import type { Translations } from "./types";\n\nexport const vi: Translations = ' + body + ";\n",
                   encoding="utf-8")


def main() -> None:
    unresolved: dict = {}
    targets = sys.argv[1:] or ["canonical", "kanban", "bots", "web"]
    for name in targets:
        {"kanban": kanban, "canonical": canonical, "bots": bots, "web": web}[name](unresolved)
        print(f"{name}: done", flush=True)
    (WORK / "reports").mkdir(parents=True, exist_ok=True)
    (WORK / "reports" / "plugins-unresolved.json").write_text(json.dumps(unresolved, ensure_ascii=False, indent=1),
                                                       encoding="utf-8")
    print(f"unresolved: {len(unresolved)}")


if __name__ == "__main__":
    main()
