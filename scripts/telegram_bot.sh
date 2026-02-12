#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_DIR="$APP_ROOT/gen"
VENV_DIR="${VENV_DIR:-$APP_ROOT/venv}"
ENV_FILE="${ENV_FILE:-$APP_ROOT/.env.local}"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

cd "$APP_ROOT"

exec "$VENV_DIR/bin/python" "$PROJECT_DIR/manage.py" run_telegram_bot \
  --poll-timeout "${TELEGRAM_BOT_POLL_TIMEOUT:-25}" \
  --sleep "${TELEGRAM_BOT_POLL_INTERVAL:-1.5}"
