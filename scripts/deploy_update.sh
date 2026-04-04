#!/usr/bin/env bash
set -euo pipefail

# Incremental deploy/update for Hostinger VPS
# Usage:
#   sudo bash scripts/deploy_update.sh /var/www/vinektech main

APP_DIR="${1:-/var/www/vinektech}"
BRANCH="${2:-main}"
SERVICE_NAME="vinektech"

if [[ ! -d "$APP_DIR" ]]; then
  echo "ERROR: APP_DIR does not exist: $APP_DIR"
  exit 1
fi

cd "$APP_DIR"

echo "[1/7] Pull latest code..."
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

echo "[2/7] Ensure virtualenv exists..."
if [[ ! -x "$APP_DIR/.venv/bin/python" ]]; then
  python3 -m venv "$APP_DIR/.venv"
fi

echo "[3/7] Install/update dependencies..."
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"
"$APP_DIR/.venv/bin/pip" install gunicorn

echo "[4/7] Load environment..."
if [[ -f "$APP_DIR/.env" ]]; then
  set -a
  source "$APP_DIR/.env"
  set +a
else
  echo "WARNING: .env not found at $APP_DIR/.env"
fi

echo "[5/7] Run migrations..."
"$APP_DIR/.venv/bin/python" manage.py migrate --noinput

echo "[6/7] Collect static files..."
"$APP_DIR/.venv/bin/python" manage.py collectstatic --noinput

echo "[7/7] Restart services..."
systemctl restart "$SERVICE_NAME"
systemctl reload nginx

echo "Deploy update completed."
echo "Check app logs: journalctl -u $SERVICE_NAME -f"
