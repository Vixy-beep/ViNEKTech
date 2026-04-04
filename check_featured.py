import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from store.models import Product

flipper = Product.objects.filter(slug='flipper-zero').first()
anti_spy = Product.objects.filter(slug='anti-spy-detector').first()

print(f"Flipper Zero featured: {flipper.is_featured if flipper else 'NO EXISTE'}")
print(f"Anti Spy featured: {anti_spy.is_featured if anti_spy else 'NO EXISTE'}")

# Listar todos los featured
all_featured = Product.objects.filter(is_featured=True, active=True).order_by('created_at')
print(f"\nProductos featured ({all_featured.count()}):")
for p in all_featured:
    print(f"  - {p.slug}: {p.name}")
