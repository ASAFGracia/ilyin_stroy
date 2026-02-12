#!/usr/bin/env bash
set -euo pipefail

UID_NUM="$(id -u)"
LABELS=(
  "com.ilyin-stroy.gunicorn"
  "com.ilyin-stroy.nginx"
  "com.ilyin-stroy.cloudflared"
  "com.ilyin-stroy.watchdog"
)

for label in "${LABELS[@]}"; do
  target="gui/${UID_NUM}/${label}"
  echo "===== ${label}"
  launchctl print "$target" 2>/dev/null | rg "state =|pid =|last exit code" -n || echo "not loaded"
  echo

done

echo "HTTP checks:"
for url in "http://127.0.0.1:8081/" "https://mastersvarki.com/"; do
  code="$(curl -k -s -o /dev/null -w '%{http_code}' "$url" || true)"
  echo "${code} ${url}"
done
