#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/Users/server/projects/ilyin_stroy"
GUNICORN_LABEL="com.ilyin-stroy.gunicorn"
GUNICORN_PLIST="$HOME/Library/LaunchAgents/${GUNICORN_LABEL}.plist"
NGINX_LABEL="com.ilyin-stroy.nginx"
NGINX_PLIST="$HOME/Library/LaunchAgents/${NGINX_LABEL}.plist"
CLOUDFLARED_LABEL="com.ilyin-stroy.cloudflared"
CLOUDFLARED_PLIST="$HOME/Library/LaunchAgents/${CLOUDFLARED_LABEL}.plist"
NGINX_PORT="8081"
GUNICORN_PORT="8000"

is_port_listening() {
  local port="$1"
  lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
}

ensure_gunicorn() {
  local uid
  uid="$(id -u)"

  if is_port_listening "$GUNICORN_PORT"; then
    return 0
  fi

  if launchctl print "gui/${uid}/${GUNICORN_LABEL}" >/dev/null 2>&1; then
    launchctl kickstart -k "gui/${uid}/${GUNICORN_LABEL}" >/dev/null 2>&1 || true
  elif [ -f "$GUNICORN_PLIST" ]; then
    launchctl bootstrap "gui/${uid}" "$GUNICORN_PLIST" >/dev/null 2>&1 || true
    launchctl kickstart -k "gui/${uid}/${GUNICORN_LABEL}" >/dev/null 2>&1 || true
  fi
}

ensure_nginx() {
  local uid
  uid="$(id -u)"

  if is_port_listening "$NGINX_PORT"; then
    return 0
  fi

  if launchctl print "gui/${uid}/${NGINX_LABEL}" >/dev/null 2>&1; then
    launchctl kickstart -k "gui/${uid}/${NGINX_LABEL}" >/dev/null 2>&1 || true
  elif [ -f "$NGINX_PLIST" ]; then
    launchctl bootstrap "gui/${uid}" "$NGINX_PLIST" >/dev/null 2>&1 || true
    launchctl kickstart -k "gui/${uid}/${NGINX_LABEL}" >/dev/null 2>&1 || true
  fi
}

is_cloudflared_running() {
  pgrep -f "cloudflared.*tunnel run mastersvarki" >/dev/null 2>&1
}

ensure_cloudflared() {
  local uid
  uid="$(id -u)"

  if is_cloudflared_running; then
    return 0
  fi

  if launchctl print "gui/${uid}/${CLOUDFLARED_LABEL}" >/dev/null 2>&1; then
    launchctl kickstart -k "gui/${uid}/${CLOUDFLARED_LABEL}" >/dev/null 2>&1 || true
  elif [ -f "$CLOUDFLARED_PLIST" ]; then
    launchctl bootstrap "gui/${uid}" "$CLOUDFLARED_PLIST" >/dev/null 2>&1 || true
    launchctl kickstart -k "gui/${uid}/${CLOUDFLARED_LABEL}" >/dev/null 2>&1 || true
  fi
}

cd "$PROJECT_ROOT"
ensure_gunicorn
ensure_nginx
ensure_cloudflared
