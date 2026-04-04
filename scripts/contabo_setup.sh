#!/usr/bin/env bash
set -euo pipefail

# Contabo VPS setup for ViNEK TECH (Ubuntu)
# Usage:
#   sudo bash scripts/contabo_setup.sh \
#     --repo https://github.com/your-user/vinektech.git \
#     --branch main \
#     --domain vinektech.com \
#     --email admin@vinektech.com
#
# Optional flags:
#   --app-user vinektech
#   --app-dir /var/www/vinektech
#   --no-postgres   (if you will manage DB elsewhere)

REPO_URL=""
BRANCH="master"
DOMAIN=""
EMAIL=""
APP_USER="vinektech"
APP_DIR="/var/www/vinektech"
INSTALL_POSTGRES=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO_URL="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    --domain) DOMAIN="$2"; shift 2 ;;
    --email) EMAIL="$2"; shift 2 ;;
    --app-user) APP_USER="$2"; shift 2 ;;
    --app-dir) APP_DIR="$2"; shift 2 ;;
    --no-postgres) INSTALL_POSTGRES=0; shift 1 ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$REPO_URL" || -z "$DOMAIN" || -z "$EMAIL" ]]; then
  echo "Missing required args. Provide --repo, --domain and --email."
  exit 1
fi

echo "[1/10] Updating system packages..."
apt update
apt install -y git nginx python3 python3-venv python3-pip certbot python3-certbot-nginx

if [[ "$INSTALL_POSTGRES" -eq 1 ]]; then
  echo "[2/10] Installing PostgreSQL..."
  apt install -y postgresql postgresql-contrib
  
  echo "  Starting PostgreSQL..."
  systemctl start postgresql
  systemctl enable postgresql
  
  # Wait for PostgreSQL to be ready
  sleep 3
  
  echo "  Configuring PostgreSQL to listen on TCP..."
  sudo -u postgres psql -c "ALTER SYSTEM SET listen_addresses = '*';"
  
  # Configure pg_hba.conf to allow localhost connections
  PG_HBA=$(sudo -u postgres psql -t -c "SHOW hba_file;")
  if ! grep -q "host.*vinektech.*127.0.0.1" "$PG_HBA"; then
    echo "host    vinektech    vinektech    127.0.0.1/32    md5" | sudo tee -a "$PG_HBA" > /dev/null
  fi
  
  echo "  Generating secure database password..."
  DB_PASSWORD=$(openssl rand -base64 16)
  
  echo "  Creating database and user..."
  sudo -u postgres psql << PSQL_EOF
CREATE USER vinektech WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE vinektech OWNER vinektech;
GRANT ALL PRIVILEGES ON DATABASE vinektech TO vinektech;
PSQL_EOF
  
  echo "  Restarting PostgreSQL with new config..."
  systemctl restart postgresql
  sleep 2
  
  echo "  ✓ PostgreSQL setup complete. DB password will be in .env"
else
  DB_PASSWORD="change-me-manually"
fi

echo "[3/10] Creating system user if needed..."
if ! id "$APP_USER" >/dev/null 2>&1; then
  useradd -m -d "/home/$APP_USER" -s /bin/bash "$APP_USER"
fi

mkdir -p "$APP_DIR"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

echo "[4/10] Cloning/updating repository..."
if [[ ! -d "$APP_DIR/.git" ]]; then
  sudo -u "$APP_USER" git clone -b "$BRANCH" "$REPO_URL" "$APP_DIR"
else
  sudo -u "$APP_USER" git -C "$APP_DIR" fetch origin
  sudo -u "$APP_USER" git -C "$APP_DIR" checkout "$BRANCH"
  sudo -u "$APP_USER" git -C "$APP_DIR" pull origin "$BRANCH"
fi

chown -R "$APP_USER:$APP_USER" "$APP_DIR"

echo "[5/10] Creating virtual environment..."
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/.venv"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install gunicorn

echo "[6/10] Preparing .env file if missing..."
if [[ ! -f "$APP_DIR/.env" ]]; then
  DJANGO_SECRET_KEY=$(openssl rand -base64 32)
  cat > "$APP_DIR/.env" <<EOF
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
DJANGO_ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
DJANGO_CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
DATABASE_URL=postgresql://vinektech:$DB_PASSWORD@127.0.0.1:5432/vinektech
DEFAULT_FROM_EMAIL=noreply@$DOMAIN
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=user@example.com
EMAIL_HOST_PASSWORD=change-me
EMAIL_USE_TLS=True
STRIPE_PUBLIC_KEY=pk_live_change_me
STRIPE_SECRET_KEY=sk_live_change_me
STRIPE_WEBHOOK_SECRET=whsec_change_me
DJANGO_ADMIN_ALLOWED_IPS=
EOF
  chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
  chmod 600 "$APP_DIR/.env"
  echo "✓ Created .env with secure DB credentials. Review other placeholders before going live."
fi

echo "[7/10] Running migrations and collectstatic..."
set -a
source "$APP_DIR/.env"
set +a
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" migrate --noinput
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" collectstatic --noinput

echo "[8/10] Configuring Gunicorn service..."
cat > /etc/systemd/system/vinektech.service <<EOF
[Unit]
Description=ViNEK TECH Django App
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

echo "[9/10] Configuring Nginx..."
cat > /etc/nginx/sites-available/vinektech <<EOF
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

echo "[10/10] Issuing SSL certificate..."
certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos -m "$EMAIL" --redirect || true

echo "Done."
echo "Next steps:"
echo "1) Fill real values in $APP_DIR/.env"
echo "2) Re-run if needed with systemctl restart vinektech && systemctl reload nginx"
echo "3) Set Stripe webhook later when you finish payment config"
