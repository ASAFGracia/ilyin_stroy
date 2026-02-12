#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_PLIST="$APP_ROOT/deploy/launchd/com.ilyin-stroy.telegram-bot.plist"
TARGET_PLIST="$HOME/Library/LaunchAgents/com.ilyin-stroy.telegram-bot.plist"
UID_NUM="$(id -u)"
TARGET="gui/${UID_NUM}/com.ilyin-stroy.telegram-bot"

if [[ ! -f "$SOURCE_PLIST" ]]; then
  echo "Template plist not found: $SOURCE_PLIST" >&2
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents"
cp "$SOURCE_PLIST" "$TARGET_PLIST"

launchctl bootout "$TARGET" >/dev/null 2>&1 || true
launchctl bootstrap "gui/${UID_NUM}" "$TARGET_PLIST"
launchctl kickstart -k "$TARGET"

echo "Installed and started: $TARGET"
