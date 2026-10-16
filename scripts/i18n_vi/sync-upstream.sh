#!/usr/bin/env bash
# Scheduled upstream sync for the Vietnamese fork (launchd runs it daily; see launchd.sh).
#
#   scripts/i18n_vi/sync-upstream.sh [--build] [--no-push]
#
# When upstream/main has new commits: merge them, translate new or changed strings (update.sh),
# verify the vi catalogs, then record everything as ONE merge commit and push the branch. It only
# starts on a clean checkout of the branch, and any failure resets the checkout to where the run
# started, logs the reason to .work/sync.log and posts a macOS notification. --build also rebuilds
# the macOS app (each commit build is a separate "Hermes Agent <sha>" app).
set -euo pipefail
unset ELECTRON_RUN_AS_NODE

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd "$here/../.." && pwd)"
work="$here/.work"
log="$work/sync.log"
branch="${HERMES_VI_BRANCH:-feat/vi-vn-localization}"
upstream="${HERMES_VI_UPSTREAM:-upstream}"
fork="${HERMES_VI_FORK:-origin}"
build=0
push=1
for arg in "$@"; do
  case "$arg" in
    --build) build=1 ;;
    --no-push) push=0 ;;
    *) echo "sync-upstream: unknown argument $arg" >&2; exit 2 ;;
  esac
done
mkdir -p "$work"

# Hermes-managed toolchains win over PATH: node that satisfies engine-strict, uv, Python >= 3.11.
newest() { { ls -d $1 2>/dev/null || true; } | sort -V | tail -1; }
for dir in "$(newest "$HOME/.hermes/tools/python-*/bin")" "$(newest "$HOME/.hermes/tools/uv-*")" \
           "$(newest "$HOME/.hermes/tools/node-*/bin")"; do
  if [ -n "$dir" ]; then PATH="$dir:$PATH"; fi
done
export PATH

say() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$log"; }
notify() { osascript -e "display notification \"${1//\"/}\" with title \"Hermes vi sync\"" >/dev/null 2>&1 || true; }
stop() { say "STOPPED: $1"; notify "Dừng: $1"; exit 1; }
py() { (cd "$here" && uv run --no-project --quiet --with pyyaml python "$@"); }

lock="$work/sync.lock"
if ! mkdir "$lock" 2>/dev/null; then
  if kill -0 "$(cat "$lock/pid" 2>/dev/null)" 2>/dev/null; then
    say "another sync is running; skipping"
    exit 0
  fi
  rm -rf "$lock"
  mkdir "$lock"
fi
echo $$ >"$lock/pid"
trap 'rm -rf "$lock"' EXIT

cd "$repo"
say "== sync start ($branch)"
current="$(git symbolic-ref --quiet --short HEAD || echo detached)"
[ "$current" = "$branch" ] || stop "checkout is on $current, not $branch"
[ -z "$(git status --porcelain --untracked-files=no)" ] || stop "checkout has uncommitted changes"

git fetch --quiet "$upstream" main >>"$log" 2>&1 || stop "cannot fetch $upstream"
git fetch --quiet "$fork" "$branch" >>"$log" 2>&1 || stop "cannot fetch $fork"
behind="$(git rev-list --count "HEAD..$upstream/main")"
if [ "$behind" = 0 ]; then
  unpushed="$(git rev-list --count "$fork/$branch..HEAD")"
  if [ "$push" = 1 ] && [ "$unpushed" != 0 ]; then
    git push --quiet "$fork" "$branch" >>"$log" 2>&1 || stop "push failed"
    say "pushed $unpushed waiting commit(s)"
  fi
  say "up to date with $upstream/main"
  exit 0
fi

py llm.py --ping >>"$log" 2>&1 || stop "translation endpoint unreachable (Tailscale / CLIProxyAPI?), retrying next run"

start="$(git rev-parse HEAD)"
target="$(git rev-parse --short "$upstream/main")"
deps_changed=0
rollback() {
  say "FAILED: $1; resetting to ${start:0:10}"
  git merge --abort >/dev/null 2>&1 || true
  git reset --quiet --hard "$start"
  if [ "$deps_changed" = 1 ]; then npm ci --no-audit --no-fund >>"$log" 2>&1 || true; fi
  notify "Đồng bộ thất bại: $1"
  exit 1
}

say "merging $behind upstream commit(s) up to $target"
if ! git merge --quiet --no-commit --no-ff "$upstream/main" >>"$log" 2>&1; then
  # Our side of these files is only the vi block surface_plugins.py inserts: take upstream's copy,
  # update.sh below inserts vi again.
  for file in $(git diff --name-only --diff-filter=U); do
    case "$file" in
      apps/desktop/src/plugins/kanban/i18n.ts | apps/desktop/src/plugins/hermes-bots/i18n.ts | \
        apps/desktop/src/plugins/hermes-bots/canonical-group-locales.ts)
        git checkout --theirs -- "$file" && git add -- "$file" ;;
    esac
  done
  conflicts="$(git diff --name-only --diff-filter=U | tr '\n' ' ')"
  [ -z "$conflicts" ] || rollback "merge conflicts in $conflicts"
fi
git rev-parse -q --verify MERGE_HEAD >/dev/null || rollback "the merge did not start (see $log)"

if ! git diff --quiet "$start" -- package-lock.json; then
  deps_changed=1
  say "package-lock.json changed: npm ci"
  npm ci --no-audit --no-fund >>"$log" 2>&1 || rollback "npm ci failed"
fi

say "translating new or changed strings"
run_log="$work/update-last.log"
WORKERS="${WORKERS:-6}" "$here/update.sh" >"$run_log" 2>&1 || { cat "$run_log" >>"$log"; rollback "update.sh failed"; }
cat "$run_log" >>"$log"
translated="$(awk '/^\[[a-z-]+\] [0-9]+ items: / {sum += $(NF-2)} END {print sum + 0}' "$run_log")"
unresolved="$(awk '/finished: .* unresolved$/ {sum += $(NF-1)} END {print sum + 0}' "$run_log")"

say "verifying"
generated=(locales/vi.yaml locales/vi.tui.yaml apps/desktop/src/i18n/vi.ts apps/desktop/src/i18n/intro-vi.ts
  apps/desktop/src/plugins/kanban/i18n.ts apps/desktop/src/plugins/hermes-bots/i18n.ts
  apps/desktop/src/plugins/hermes-bots/canonical-group-locales.ts web/src/i18n/vi.ts)
(cd apps/desktop && npx tsc -p . --noEmit) >>"$log" 2>&1 || rollback "desktop typecheck failed"
(cd web && npx tsc -p tsconfig.app.json --noEmit) >>"$log" 2>&1 || rollback "web typecheck failed"
(cd apps/desktop && npx vitest run --project ui src/i18n src/plugins/kanban) >>"$log" 2>&1 ||
  rollback "desktop i18n tests failed"
(cd apps/desktop && npx eslint src/i18n/vi.ts src/i18n/intro-vi.ts src/plugins/kanban/i18n.ts \
  src/plugins/hermes-bots/i18n.ts src/plugins/hermes-bots/canonical-group-locales.ts) >>"$log" 2>&1 ||
  rollback "lint errors in the generated catalogs"
py verify.py >>"$log" 2>&1 || rollback "vi catalogs drifted from English"

git add -- "${generated[@]}" scripts/i18n_vi/cache
leftover="$(git diff --name-only | tr '\n' ' ')"
[ -z "$leftover" ] || rollback "unexpected changes outside the vi catalogs: $leftover"
# The merged upstream code is upstream's to lint; our generated files were linted above, so the
# pre-commit hook would only re-lint hundreds of upstream files.
LEFTHOOK=0 git commit --quiet -m "Merge upstream main ($target) and sync vi translations" \
  -m "Merged $behind upstream commit(s); $translated new or changed string(s) translated, $unresolved left for review." \
  >>"$log" 2>&1 || rollback "commit failed"
say "committed $(git rev-parse --short HEAD): $behind upstream commit(s), $translated string(s) translated, $unresolved to review"

if [ "$push" = 1 ]; then
  if git push --quiet "$fork" "$branch" >>"$log" 2>&1; then
    say "pushed to $fork/$branch"
  else
    say "push failed; the commit stays local and the next run pushes it"
    notify "Push thất bại; lần chạy sau sẽ thử lại"
    exit 1
  fi
fi

message="Đã gộp $behind commit upstream, dịch $translated chuỗi"
if [ "$unresolved" != 0 ]; then message="$message, $unresolved chuỗi cần xem lại"; fi

if [ "$build" = 1 ]; then
  say "building the macOS app"
  scripts/build-bundle.sh >>"$log" 2>&1 || stop "app build failed (the sync itself succeeded)"
  app="$(basename "$(ls -d apps/desktop/release/mac-arm64/*.app | head -1)")"
  say "built $app"
  message="$message. Đã build $app"
fi
notify "$message"
say "== sync done"
