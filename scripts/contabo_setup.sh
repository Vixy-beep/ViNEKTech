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
  
  echo "  Starting PostgreSQL service..."
  systemctl restart postgresql
  systemctl enable postgresql
  
  # Wait longer for PostgreSQL to start
  echo "  Waiting for PostgreSQL to be ready..."
  for i in {1..30}; do
    if sudo -u postgres psql -c "SELECT 1" >/dev/null 2>&1; then
      echo "  ✓ PostgreSQL is ready"
      break
    fi
    echo "    Attempt $i/30..."
    sleep 1
  done
  
  echo "  Configuring PostgreSQL to listen on TCP..."
  sudo -u postgres psql -c "ALTER SYSTEM SET listen_addresses = 'localhost';" >/dev/null 2>&1 || true
  
  echo "  Restarting PostgreSQL with new config..."
  systemctl restart postgresql
  sleep 5
  
  # Verify PostgreSQL is running and responsive
  if ! sudo -u postgres psql -c "SELECT 1" >/dev/null 2>&1; then
    echo "  ✗ PostgreSQL failed to start. Checking logs..."
    journalctl -u postgresql -n 20
    exit 1
  fi
  
  echo "  Generating secure database password..."
  DB_PASSWORD=$(openssl rand -base64 16)
  
  echo "  Creating database and user..."
  sudo -u postgres psql << PSQL_EOF
CREATE USER vinektech WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE vinektech OWNER vinektech;
GRANT ALL PRIVILEGES ON DATABASE vinektech TO vinektech;
PSQL_EOF
  
  if [[ $? -eq 0 ]]; then
    echo "  ✓ PostgreSQL setup complete"
  else
    echo "  ✗ Failed to create database/user"
    exit 1
  fi
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

# Retry migrations with exponential backoff - but don't block the entire setup
MIGRATE_RETRIES=10
RETRY_COUNT=0
MIGRATE_SUCCESS=0

until [[ $RETRY_COUNT -ge $MIGRATE_RETRIES ]]; do
  if sudo -u "$APP_USER" "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" migrate --noinput 2>&1 | grep -q "No migrations to apply"; then
    echo "✓ Migrations completed successfully (no pending migrations)"
    MIGRATE_SUCCESS=1
    break
  elif sudo -u "$APP_USER" "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" migrate --noinput >/dev/null 2>&1; then
    echo "✓ Migrations completed successfully"
    MIGRATE_SUCCESS=1
    break
  else
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [[ $RETRY_COUNT -lt $MIGRATE_RETRIES ]]; then
      WAIT_TIME=$((2 ** (RETRY_COUNT - 1)))
      echo "  Migrations failed, retrying in ${WAIT_TIME}s (attempt $RETRY_COUNT/$MIGRATE_RETRIES)..."
      sleep $WAIT_TIME
    fi
  fi
done

if [[ $MIGRATE_SUCCESS -eq 0 ]]; then
  echo "⚠ Migrations failed after $MIGRATE_RETRIES attempts"
  echo "  You can retry manually later with:"
  echo "  cd $APP_DIR && source .env && ./.venv/bin/python manage.py migrate"
fi

sudo -u "$APP_USER" "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" collectstatic --noinput 2>&1 | tail -5

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

echo ""
echo "======================================="
echo "  Setup completed (with caveats)"
echo "======================================="
echo ""
echo "NEXT STEPS:"
echo ""
echo "1) Fill real values in $APP_DIR/.env"
echo "   - EMAIL credentials (SMTP)"
echo "   - Stripe keys (STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET)"
echo "   - DJANGO_SECRET_KEY (already auto-generated)"
echo ""
echo "2) If migrations failed, run them manually:"
echo "   cd $APP_DIR"
echo "   source .env"
echo "   ./.venv/bin/python manage.py migrate"
echo ""
echo "3) Then restart the application:"
echo "   systemctl restart vinektech && systemctl reload nginx"
echo ""
echo "4) Test by visiting: https://$DOMAIN"
echo ""
echo "======================================="
