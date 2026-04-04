#!/usr/bin/env bash
set -euo pipefail

# Hostinger VPS deployment script for Django + Gunicorn + Nginx + SSL
# Usage:
#   sudo bash scripts/deploy_hostinger.sh \
#     --domain vinektech.com \
#     --repo https://github.com/your-user/vinektech.git \
#     --branch main

DOMAIN=""
REPO_URL=""
BRANCH="main"
APP_DIR="/var/www/vinektech"
APP_USER="www-data"
PYTHON_BIN="python3"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain) DOMAIN="$2"; shift 2 ;;
    --repo) REPO_URL="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "$DOMAIN" || -z "$REPO_URL" ]]; then
  echo "Missing required args --domain and --repo"
  exit 1
fi

echo "[1/9] Installing system packages..."
apt update
apt install -y git nginx certbot python3-certbot-nginx python3-venv python3-pip

echo "[2/9] Cloning/Updating app..."
mkdir -p "$APP_DIR"
if [[ ! -d "$APP_DIR/.git" ]]; then
  git clone -b "$BRANCH" "$REPO_URL" "$APP_DIR"
else
  git -C "$APP_DIR" fetch origin
  git -C "$APP_DIR" checkout "$BRANCH"
  git -C "$APP_DIR" pull origin "$BRANCH"
fi

echo "[3/9] Creating virtualenv and installing deps..."
$PYTHON_BIN -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"
"$APP_DIR/.venv/bin/pip" install gunicorn

if [[ ! -f "$APP_DIR/.env" ]]; then
  echo "[4/9] Creating .env from .env.example"
  cp "$APP_DIR/.env.example" "$APP_DIR/.env"
  sed -i "s/DJANGO_DEBUG=.*/DJANGO_DEBUG=False/" "$APP_DIR/.env" || true
  echo "Edit $APP_DIR/.env and set Stripe/DB/hosts before continuing."
fi

echo "[5/9] Running migrations and collectstatic..."
cd "$APP_DIR"
set -a
source "$APP_DIR/.env"
set +a
"$APP_DIR/.venv/bin/python" manage.py migrate --noinput
"$APP_DIR/.venv/bin/python" manage.py collectstatic --noinput

echo "[6/9] Creating systemd service..."
cat >/etc/systemd/system/vinektech.service <<EOF
[Unit]
Description=ViNEK Tech Django App
After=network.target

[Service]
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable vinektech
systemctl restart vinektech

echo "[7/9] Configuring Nginx..."
cat >/etc/nginx/sites-available/vinektech <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 20M;

    location /static/ {
        alias $APP_DIR/staticfiles/;
    }

    location /media/ {
        alias $APP_DIR/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/vinektech /etc/nginx/sites-enabled/vinektech
nginx -t
systemctl reload nginx

echo "[8/9] Issuing SSL cert with certbot..."
certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos -m "admin@$DOMAIN" --redirect || true

echo "[9/9] Done."
echo "Check service: systemctl status vinektech"
echo "Check logs: journalctl -u vinektech -f"
