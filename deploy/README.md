# Mastersvarki deployment (macOS + launchd + gunicorn + nginx + cloudflared)

## Current runtime model

- `gunicorn` serves Django on `127.0.0.1:8000`
- `nginx` proxies on `127.0.0.1:8081` and serves `/static/` + `/media/`
- `cloudflared` publishes `mastersvarki.com` to the nginx origin
- `launchd` keeps all services alive and restarts them on login/reboot/network changes
- PostgreSQL runs locally (`postgresql@16`) and stores users/profiles/orders/articles

> Note: launchd labels use legacy names (`com.ilyin-stroy.*`) to keep compatibility with existing local setup.

## One-time setup on this server

1. Install dependencies:

```bash
brew install nginx cloudflared postgresql@16
brew services start postgresql@16
```

2. Create local PostgreSQL DB/user (example):

```bash
/opt/homebrew/opt/postgresql@16/bin/psql -d postgres -c "CREATE ROLE mastersvarki WITH LOGIN PASSWORD 'change-me';"
/opt/homebrew/opt/postgresql@16/bin/createdb -O mastersvarki mastersvarki_db
```

3. Prepare environment:

```bash
cd /Users/server/projects/ilyin_stroy
cp .env.example .env.local
# edit .env.local (POSTGRES_*, email creds, OWNER_EMAIL, AUTH_CODE_* limits)
```

4. Install Python dependencies and run migrations:

```bash
./venv/bin/pip install -r gen/requirements.txt
set -a; source .env.local; set +a
./venv/bin/python gen/manage.py migrate --noinput
./venv/bin/python gen/manage.py collectstatic --noinput
```

5. Ensure launch agents are loaded:

```bash
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.ilyin-stroy.gunicorn.plist"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.ilyin-stroy.nginx.plist"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.ilyin-stroy.cloudflared.plist"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.ilyin-stroy.watchdog.plist"
```

## Manual update from Git (recommended)

Use the executable script in repo root:

```bash
./scripts/update_from_git.sh
```

What it does:

- pulls latest code from `main`
- installs dependencies
- runs `migrate` and `collectstatic`
- runs `check`
- restarts gunicorn/nginx/cloudflared/watchdog launchd jobs
- performs local health check (`http://127.0.0.1:8081/`)

For local testing without `git pull`:

```bash
SKIP_GIT=1 ./scripts/update_from_git.sh
```

## Optional GitHub auto-deploy

The workflow `.github/workflows/deploy.yml` connects via SSH and executes `./scripts/update_from_git.sh`.
Required secrets:

- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_PORT`
- `DEPLOY_SSH_KEY`
- `DEPLOY_APP_DIR` (optional, defaults to `/Users/server/projects/ilyin_stroy`)

## Why reconnecting Wi-Fi / reboot keeps the site alive

- `launchd` jobs use `RunAtLoad=true` and `KeepAlive=true`
- `cloudflared` and watchdog are network-aware
- watchdog script checks and restarts gunicorn/nginx/cloudflared periodically
- PostgreSQL runs as `brew services` launch agent and auto-starts on login

### If launch agents were created earlier

If your old plist files still contain `KeepAlive` as a dictionary with `SuccessfulExit=false`,
replace it with `KeepAlive=true` and reload jobs:

```bash
for f in "$HOME/Library/LaunchAgents/com.ilyin-stroy.gunicorn.plist" \
         "$HOME/Library/LaunchAgents/com.ilyin-stroy.nginx.plist" \
         "$HOME/Library/LaunchAgents/com.ilyin-stroy.cloudflared.plist"; do
  perl -0pi -e 's#<key>KeepAlive</key>\s*<dict>\s*<key>SuccessfulExit</key>\s*<false/>\s*<key>NetworkState</key>\s*<true/>\s*</dict>#<key>KeepAlive</key>\n    <true/>#s' "$f"
done
uid="$(id -u)"
for label in com.ilyin-stroy.gunicorn com.ilyin-stroy.nginx com.ilyin-stroy.cloudflared; do
  launchctl kickstart -k "gui/${uid}/${label}"
done
```
