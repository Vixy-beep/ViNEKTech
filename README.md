# ViNEK TECH E-commerce

Tienda online estilo tecnologia/ciberseguridad con identidad visual cyber (purpura + azul + verde neon), desarrollada con Django.

## Stack

- Python + Django
- Django REST Framework (base lista para APIs)
- SQLite local (PostgreSQL listo por variables de entorno)

## Inicio rapido

1. Crear y activar entorno virtual.
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Copiar variables:

```bash
copy .env.example .env
```

4. Migrar y sembrar catalogo:

```bash
python manage.py migrate
python manage.py seed_catalog
```

5. Crear admin:

```bash
python manage.py createsuperuser
```

6. Ejecutar:

```bash
python manage.py runserver
```

## Funcionalidades incluidas

- Homepage premium cyber responsive + newsletter
- Catalogo con busqueda, filtros, orden y paginacion
- Product detail con SEO metadata y JSON-LD
- Carrito por sesion (sin login)
- Checkout funcional con zonas de envio y cupones
- Guardado de IP y user-agent al aceptar declaracion
- Perfil de usuario y historial de pedidos
- Tracking de pedidos por numero y email
- Paginas legales: terminos, privacidad, uso responsable
- `robots.txt` y `sitemap.xml` dinamicos
- API de productos (`/api/products/`)
- Admin para productos, categorias, imagenes, perfiles y ordenes
- CI basico con GitHub Actions
- Arquitectura de catalogo estilo Shopify (brands, collections, variants)
- Automatizacion diaria de tasa USD->DOP y reporte operativo

## Cupones de demo

- `VINEK10` (10% off)
- `RD500` (descuento fijo RD$500)

## Tracking cliente

- URL: `/orders/tracking/`
- Datos requeridos: numero de orden + email de compra

## Operacion de precios (dropshipping)

- Sincronizar costos/margenes desde CSV:

```bash
python manage.py sync_pricing_csv --file vinektech_pricing.csv --rate 62 --apply-suggested-usd --mark-high-margin
```

- Recalcular precios DOP por tasa de cambio:

```bash
python manage.py recalculate_price_dop --rate 62
```

- Obtener tasa automatica y recalcular:

```bash
python manage.py update_fx_rate
```

- Ejecutar rutina diaria (pricing + reporte):

```bash
python manage.py daily_ops_report
```

## Demo Deployment (mostrar a terceros)

Opciones listas en el repo:

- `Procfile` para Railway/Render
- `Dockerfile` para contenedor
- `render.yaml` para despliegue rapido en Render
- Workflow nocturno: `.github/workflows/nightly-ops.yml`

Pasos demo recomendados en Render:

1. Conectar repositorio.
2. Crear servicio usando `render.yaml`.
3. Configurar `DJANGO_SECRET_KEY` en variables.
4. Cargar `products.json` y `vinektech_pricing.csv` en deploy o ejecutar comandos post-deploy.
5. Validar homepage, catalogo y checkout.

Este setup es para demo/mostrable. Para lanzamiento oficial se ajustan seguridad estricta, pasarela de pago real, storage S3/R2 y observabilidad.

## Variables importantes

Revisar `.env.example`:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `POSTGRES_*`
- `STRIPE_PUBLIC_KEY`
- `STRIPE_SECRET_KEY`
- `EMAIL_*`

## Dominio

Preparado para despliegue en `vinektech.com` y `www.vinektech.com` al configurar variables de produccion.
