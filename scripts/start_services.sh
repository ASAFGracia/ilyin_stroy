#!/usr/bin/env bash
set -euo pipefail

UID_NUM="$(id -u)"
LABELS=(
  "com.ilyin-stroy.gunicorn"
  "com.ilyin-stroy.nginx"
  "com.ilyin-stroy.cloudflared"
  "com.ilyin-stroy.watchdog"
)

start_agent() {
  local label="$1"
  local target="gui/${UID_NUM}/${label}"
  local plist="$HOME/Library/LaunchAgents/${label}.plist"

  if launchctl print "$target" >/dev/null 2>&1; then
    launchctl kickstart -k "$target" >/dev/null 2>&1 || true
  elif [[ -f "$plist" ]]; then
    launchctl bootstrap "gui/${UID_NUM}" "$plist" >/dev/null 2>&1 || true
    launchctl kickstart -k "$target" >/dev/null 2>&1 || true
  else
    echo "[warn] plist not found for ${label}: ${plist}"
  fi
}

for label in "${LABELS[@]}"; do
  start_agent "$label"
done

sleep 1

for label in "${LABELS[@]}"; do
  target="gui/${UID_NUM}/${label}"
  state="$(launchctl print "$target" 2>/dev/null | awk -F'= ' '/state =/{print $2; exit}' || true)"
  echo "${label}: ${state:-unknown}"
done

if curl -fsS http://127.0.0.1:8081/ >/dev/null 2>&1; then
  echo "Local health check: OK (http://127.0.0.1:8081/)"
else
  echo "Local health check: FAILED"
  exit 1
fi
