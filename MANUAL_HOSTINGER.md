# Manual de subida a Contabo VPS

Este documento resume el proceso para subir la tienda completa a un VPS de Contabo, dejar pagos funcionando, seguimiento por cuenta y acceso administrativo seguro.

## 1. Preparar el servidor

Usa un VPS con Ubuntu. El flujo recomendado es:

1. Crear el VPS en Contabo.
2. Apuntar el dominio principal al VPS con un registro `A`.
3. Entrar por SSH al servidor.
4. Instalar dependencias del sistema:
   - `git`
   - `python3`
   - `python3-venv`
   - `python3-pip`
   - `nginx`
   - `certbot`
   - `python3-certbot-nginx`

## 2. Subir el proyecto

Clona el repositorio en el servidor, por ejemplo en:

```bash
/var/www/vinektech
```

Luego:

1. Crear entorno virtual.
2. Instalar dependencias del proyecto.
3. Crear el archivo `.env` con las variables de producción.
4. Ejecutar migraciones.
5. Ejecutar `collectstatic`.

## 3. Variables de entorno necesarias

Configura al menos estas variables:

- `DJANGO_DEBUG=False`
- `DJANGO_SECRET_KEY=...`
- `DJANGO_ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com`
- `DATABASE_URL=...` o credenciales PostgreSQL
- `STRIPE_PUBLIC_KEY=...`
- `STRIPE_SECRET_KEY=...`
- `STRIPE_WEBHOOK_SECRET=...`
- `EMAIL_HOST=...`
- `EMAIL_PORT=...`
- `EMAIL_HOST_USER=...`
- `EMAIL_HOST_PASSWORD=...`
- `DEFAULT_FROM_EMAIL=...`
- `DJANGO_ADMIN_ALLOWED_IPS=...` si quieres restringir admin por IP

## 4. Base de datos

Se recomienda PostgreSQL.

Pasos:

1. Crear la base de datos.
2. Asignar usuario y contraseña.
3. Guardar la URL en `DATABASE_URL`.
4. Ejecutar:

```bash
python manage.py migrate
```

## 5. Archivos estáticos y media

Ejecutar:

```bash
python manage.py collectstatic --noinput
```

Asegura que Nginx sirva:

- `/static/`
- `/media/`

## 6. Gunicorn y systemd

Usa Gunicorn como servidor WSGI.

Ejemplo de servicio:

```ini
[Unit]
Description=ViNEK Tech Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/vinektech
EnvironmentFile=/var/www/vinektech/.env
ExecStart=/var/www/vinektech/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

## 7. Nginx

Configura un sitio que:

1. Escuche en `80` y `443`.
2. Redirija a HTTPS.
3. Sirva estáticos y media.
4. Reenvíe el tráfico a Gunicorn.

## 8. SSL

Pide certificado con Certbot:

```bash
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

## 9. Pagos

### Stripe

1. Crear cuenta Stripe.
2. Obtener llaves de producción.
3. Configurar webhook en Stripe hacia:

```text
https://tu-dominio.com/orders/stripe-webhook/
```

4. Activar el evento:
   - `checkout.session.completed`

### Flujo de pago

- El cliente crea la orden.
- Stripe Checkout toma el pago.
- El webhook marca el pedido como pagado.
- El seguimiento se refleja en la cuenta del usuario.

## 10. Seguimiento por cuenta

El tracking ya no depende de número de orden + correo.

El cliente:

1. Inicia sesión.
2. Entra a Seguimiento.
3. Ve sus pedidos directamente.
4. Selecciona uno para ver estado, pago y guía.

Estados visuales:

- `Pending`
- `Paid`
- `Shipped`

## 11. Admin seguro

### Usuario admin

Hay un comando para rotar contraseña del admin:

```bash
python manage.py rotate_admin_password --username Rubi
```

Eso imprime una contraseña nueva fuerte.

### Restricción por IP

Si configuras:

```text
DJANGO_ADMIN_ALLOWED_IPS=tu.ip.publica
```

El panel `/admin/` quedará restringido por IP.

## 12. Actualización incremental

Si solo vas a actualizar código, usa:

```bash
bash scripts/deploy_update.sh /var/www/vinektech main
```

Eso hace:

1. `git pull`
2. instala dependencias
3. ejecuta migraciones
4. ejecuta `collectstatic`
5. reinicia servicio

## 13. Archivos clave del proyecto

- [scripts/deploy_hostinger.sh](scripts/deploy_hostinger.sh)
- [scripts/deploy_update.sh](scripts/deploy_update.sh)
- [orders/views.py](orders/views.py)
- [templates/orders/tracking.html](templates/orders/tracking.html)
- [config/settings.py](config/settings.py)
- [accounts/middleware.py](accounts/middleware.py)
- [accounts/management/commands/rotate_admin_password.py](accounts/management/commands/rotate_admin_password.py)

## 14. Checklist final antes de publicar

1. Revisar que el dominio apunte al VPS.
2. Confirmar SSL activo.
3. Probar login normal.
4. Probar checkout con Stripe de prueba.
5. Probar webhook Stripe.
6. Confirmar tracking con usuario autenticado.
7. Confirmar panel admin funcionando.
8. Revisar imágenes del catálogo y detalle.

## 15. Datos que debes tener a mano

1. IP del VPS.
2. Usuario SSH.
3. Puerto SSH.
4. Repositorio Git.
5. Variables de entorno.
6. Llaves Stripe.
7. SMTP de correo.
8. Dominio final.

## 16. Script de arranque para Contabo

Si quieres automatizar la primera instalación en Contabo, usa:

```bash
bash scripts/contabo_setup.sh --repo https://github.com/tu-usuario/tu-repo.git --branch main --domain vinektech.com --email admin@vinektech.com
```

Ese script deja listo:

1. Paquetes del sistema.
2. Entorno virtual.
3. Instalación de dependencias.
4. Servicio Gunicorn.
5. Nginx.
6. SSL con Certbot.

