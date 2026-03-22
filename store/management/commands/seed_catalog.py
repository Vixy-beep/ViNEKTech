from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from orders.models import Coupon
from store.models import Category, Product


class Command(BaseCommand):
    help = 'Carga un catalogo inicial de ViNEK TECH.'

    def handle(self, *args, **options):
        categories = {
            'Networking': Category.objects.get_or_create(name='Networking', slug='networking')[0],
            'Pentest': Category.objects.get_or_create(name='Pentest', slug='pentest')[0],
            'Lab Gear': Category.objects.get_or_create(name='Lab Gear', slug='lab-gear')[0],
            'Smart Devices': Category.objects.get_or_create(name='Smart Devices', slug='smart-devices')[0],
        }

        products = [
            ('Flipper Zero Multi-Tool', 'Pentest', Decimal('17499.00'), 'pro', True),
            ('WiFi Pineapple Mark VII', 'Pentest', Decimal('22999.00'), 'pro', True),
            ('Raspberry Pi 5 Security Kit', 'Lab Gear', Decimal('9499.00'), 'mid', False),
            ('Proxmark3 Easy RFID Suite', 'Pentest', Decimal('10499.00'), 'mid', True),
            ('GL.iNet Secure Travel Router', 'Networking', Decimal('6399.00'), 'entry', False),
            ('Ubiquiti WiFi 6 Access Point', 'Networking', Decimal('8999.00'), 'mid', False),
            ('Mini NVR Cyber Cam Shield', 'Smart Devices', Decimal('5699.00'), 'entry', False),
            ('USB Rubber Ducky Deluxe', 'Pentest', Decimal('6899.00'), 'entry', True),
            ('YubiKey 5 NFC', 'Smart Devices', Decimal('4799.00'), 'entry', False),
        ]

        for name, category_name, price, tier, sensitive in products:
            Product.objects.update_or_create(
                slug=slugify(name),
                defaults={
                    'name': name,
                    'short_description': f'{name} listo para despliegue tecnico.',
                    'description': f'{name} para entornos de seguridad y laboratorios tecnicos.',
                    'category': categories[category_name],
                    'price': price,
                    'compare_at_price': price + Decimal('1500.00'),
                    'stock_quantity': 25,
                    'tier': tier,
                    'is_sensitive': sensitive,
                    'is_featured': True,
                    'is_bestseller': tier in {'mid', 'pro'},
                    'is_active': True,
                    'use_case_declaration': 'Solo para uso legal y autorizado.' if sensitive else '',
                },
            )

        Coupon.objects.update_or_create(
            code='VINEK10',
            defaults={
                'description': 'Descuento de lanzamiento',
                'discount_percent': 10,
                'active': True,
            },
        )
        Coupon.objects.update_or_create(
            code='RD500',
            defaults={
                'description': 'Descuento fijo en compras mayores de RD$8,000',
                'discount_fixed': Decimal('500.00'),
                'active': True,
            },
        )

        self.stdout.write(self.style.SUCCESS('Catalogo inicial cargado correctamente.'))
