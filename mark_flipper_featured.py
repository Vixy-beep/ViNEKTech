#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from store.models import Product

# Asegurar que Flipper Zero esté featured y sea el primero
flipper = Product.objects.get(slug='flipper-zero')
print(f"Antes - is_featured: {flipper.is_featured}")

flipper.is_featured = True
flipper.save()

print(f"Después - is_featured: {flipper.is_featured}")
print(f"Price: ${flipper.price} USD")
print("✅ Flipper Zero marcado como FEATURED")
