#!/usr/bin/env bash
# Re-sync the Vietnamese (vi) catalogs, e.g. after merging upstream.
#
#   scripts/i18n_vi/update.sh
#
# Dumps every English catalog, translates only new or changed strings (cache/ is the translation
# memory, so reviewed wording survives), regenerates the vi files and formats them. Needs the
# repo-root `npm ci`, plus `node` and `uv` on PATH. Endpoint: VI_I18N_BASE_URL + VI_I18N_API_KEY
# (any OpenAI-compatible server, e.g. CLIProxyAPI); without them the Codex CLI provider in
# ~/.codex/config.toml is used. Model: VI_I18N_MODEL (default gpt-6-luna). Parallelism: WORKERS.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd "$here/../.." && pwd)"
work="$here/.work"
desktop=apps/desktop
mkdir -p "$work"
cd "$repo"

npx tsx --tsconfig "$desktop/tsconfig.json" "$here/dump.mts" "$desktop/src/i18n/en.ts" en "$work/desktop-en.json"
npx tsx --tsconfig ui-tui/tsconfig.json "$here/dump-tui.mts" "$repo" "$work/tui-en.json"

# Plugin and web catalogs import UI modules, so they are bundled first (Vite env, asset stubs).
bundle_dump() { VI_I18N_BUNDLE_DIR="$1" node "$here/bundle-dump.mjs" "$repo" "${@:2}"; }
bundle_dump "$desktop/node_modules/.cache/vi-i18n" "$desktop/tsconfig.json" \
  "$desktop/src/plugins/kanban/i18n.ts" KANBAN_LOCALES.en "$work/kanban-en.json"
bundle_dump "$desktop/node_modules/.cache/vi-i18n" "$desktop/tsconfig.json" \
  "$desktop/src/plugins/hermes-bots/i18n.ts" BOTS_LOCALES.en "$work/bots-en.json"
bundle_dump "$desktop/node_modules/.cache/vi-i18n" "$desktop/tsconfig.json" \
  "$desktop/src/plugins/hermes-bots/canonical-group-locales.ts" CANONICAL_GROUP_LOCALES.en "$work/canonical-en.json"
bundle_dump node_modules/.cache/vi-i18n web/tsconfig.app.json web/src/i18n/en.ts en "$work/web-en.json"
rm -rf "$desktop/node_modules/.cache/vi-i18n" node_modules/.cache/vi-i18n

py() { uv run --no-project --quiet --with pyyaml python "$@"; }
(
  cd "$here"
  py surface_core.py
  py surface_tui.py
  py surface_desktop.py
  py surface_plugins.py
  py revalidate.py --dry
)

npx prettier --write "$desktop/src/i18n/vi.ts" "$desktop/src/i18n/intro-vi.ts" \
  "$desktop/src/plugins/kanban/i18n.ts" "$desktop/src/plugins/hermes-bots/i18n.ts" \
  "$desktop/src/plugins/hermes-bots/canonical-group-locales.ts" >/dev/null
(cd "$desktop" && npx eslint --fix src/i18n/vi.ts src/i18n/intro-vi.ts >/dev/null)

# web/ locale files follow Prettier's defaults (double quotes, semicolons), not the root .prettierrc.
tmp="$(mktemp -d)"
cp web/src/i18n/vi.ts "$tmp/vi.ts"
(cd "$tmp" && "$repo/node_modules/.bin/prettier" --no-config --no-editorconfig --trailing-comma all --print-width 80 vi.ts >vi.fmt.ts)
cp "$tmp/vi.fmt.ts" web/src/i18n/vi.ts
rm -rf "$tmp"

echo "i18n_vi: done. Strings that never passed validation are listed in $work/reports/."
