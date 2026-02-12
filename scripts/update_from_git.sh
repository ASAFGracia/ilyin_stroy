#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$APP_ROOT/venv}"
PROJECT_DIR="$APP_ROOT/gen"
BRANCH="${BRANCH:-main}"
ENV_FILE="${ENV_FILE:-$APP_ROOT/.env.local}"
SKIP_GIT="${SKIP_GIT:-0}"

load_env() {
  if [[ -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
  fi
}

restart_agent() {
  local label="$1"
  local uid
  uid="$(id -u)"
  local target="gui/${uid}/${label}"
  local plist="$HOME/Library/LaunchAgents/${label}.plist"

  if launchctl print "$target" >/dev/null 2>&1; then
    launchctl kickstart -k "$target"
    return 0
  fi

  if [[ -f "$plist" ]]; then
    launchctl bootstrap "gui/${uid}" "$plist" >/dev/null 2>&1 || true
    launchctl kickstart -k "$target" >/dev/null 2>&1 || true
  fi
}

cd "$APP_ROOT"
load_env

if [[ "$SKIP_GIT" != "1" ]]; then
  git fetch origin "$BRANCH"
  git checkout "$BRANCH"
  git pull --ff-only origin "$BRANCH"
fi

"$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
"$VENV_DIR/bin/python" "$PROJECT_DIR/manage.py" migrate --noinput
"$VENV_DIR/bin/python" "$PROJECT_DIR/manage.py" collectstatic --noinput
"$VENV_DIR/bin/python" "$PROJECT_DIR/manage.py" check

restart_agent "com.ilyin-stroy.gunicorn"
restart_agent "com.ilyin-stroy.nginx"
restart_agent "com.ilyin-stroy.cloudflared"
restart_agent "com.ilyin-stroy.watchdog"

curl -fsS http://127.0.0.1:8081/ >/dev/null

echo "Update complete: code pulled, migrations applied, static collected, services restarted."
