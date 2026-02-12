#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/ilyin_stroy}"
PROJECT_DIR="$APP_DIR/gen"
VENV_DIR="${VENV_DIR:-$APP_DIR/venv}"
BRANCH="${BRANCH:-main}"
SERVICE_NAME="${SERVICE_NAME:-ilyin-stroy.service}"

cd "$APP_DIR"
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

"$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
"$VENV_DIR/bin/python" "$PROJECT_DIR/manage.py" migrate --noinput
"$VENV_DIR/bin/python" "$PROJECT_DIR/manage.py" collectstatic --noinput

sudo systemctl restart "$SERVICE_NAME"
sudo systemctl reload nginx
