#!/usr/bin/env bash
# Manage the LaunchAgent that runs sync-upstream.sh every day for this checkout.
#
#   scripts/i18n_vi/launchd.sh install [HH:MM] [sync flags, e.g. --build]   (default 09:00)
#   scripts/i18n_vi/launchd.sh status | run | uninstall
#
# launchd rather than cron: a run missed while the Mac sleeps happens on wake instead of being
# skipped. Output lands in .work/launchd.log; each run's summary in .work/sync.log.
set -euo pipefail

label="io.github.tringuyen1032.hermes-vi-sync"
plist="$HOME/Library/LaunchAgents/$label.plist"
domain="gui/$(id -u)"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
work="$here/.work"

xml() { sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' <<<"$1"; }

install() {
  local time="09:00"
  if [[ "${1:-}" =~ ^[0-9]{1,2}:[0-9]{2}$ ]]; then
    time="$1"
    shift
  fi
  local hour=$((10#${time%%:*})) minute=$((10#${time##*:}))
  local args="    <string>/bin/bash</string>
    <string>$(xml "$here/sync-upstream.sh")</string>"
  for flag in "$@"; do
    args="$args
    <string>$(xml "$flag")</string>"
  done
  mkdir -p "$work" "$(dirname "$plist")"
  cat >"$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$label</string>
  <key>ProgramArguments</key>
  <array>
$args
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>$hour</integer>
    <key>Minute</key>
    <integer>$minute</integer>
  </dict>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
  <key>ProcessType</key>
  <string>Background</string>
  <key>LowPriorityIO</key>
  <true/>
  <key>StandardOutPath</key>
  <string>$(xml "$work/launchd.log")</string>
  <key>StandardErrorPath</key>
  <string>$(xml "$work/launchd.log")</string>
</dict>
</plist>
EOF
  plutil -lint "$plist" >/dev/null
  launchctl bootout "$domain/$label" 2>/dev/null || true
  launchctl bootstrap "$domain" "$plist"
  printf 'installed: daily at %02d:%02d -> %s\n' "$hour" "$minute" "$plist"
}

case "${1:-}" in
  install) shift; install "$@" ;;
  run) launchctl kickstart "$domain/$label" && echo "started; follow $work/sync.log" ;;
  status)
    launchctl print "$domain/$label" | grep -E '^\s*(state|last exit code|runs) =' || echo "not loaded"
    tail -n 8 "$work/sync.log" 2>/dev/null || true
    ;;
  uninstall)
    launchctl bootout "$domain/$label" 2>/dev/null || true
    rm -f "$plist"
    echo "removed $label"
    ;;
  *) sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'; exit 2 ;;
esac
