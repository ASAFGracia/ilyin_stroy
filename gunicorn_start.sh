#!/bin/bash

set -euo pipefail

cd /Users/server/projects/ilyin_stroy/gen
source ../venv/bin/activate

exec gunicorn gen.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 2 \
  --timeout 120
