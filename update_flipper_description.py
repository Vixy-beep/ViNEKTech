#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from store.models import Product

flipper = Product.objects.get(slug='flipper-zero')
flipper.description = 'El gadget que los gobiernos no quieren que tengas. RFID, NFC, IR, Sub-GHz... todo en un dispositivo del tamaño de tu mano. El Flipper Zero es el multi-tool portátil definitivo para investigadores de seguridad. Lee/emula/interrumpe RFID, NFC, protocolos IR, Sub-GHz. Análisis de hardware sin límites.'
flipper.description_es = flipper.description
flipper.save()

print('✅ Descripción de Flipper Zero actualizada')
print(f'   Description length: {len(flipper.description)} chars')
