import json
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Product


class Command(BaseCommand):
    help = 'Carga productos desde products.json (fixture de Django)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='products.json',
            help='Ruta al archivo products.json',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Eliminar todos los productos antes de cargar',
        )

    def handle(self, *args, **options):
        json_file = options['file']
        clear = options['clear']

        if clear:
            self.stdout.write('Eliminando productos existentes...')
            try:
                # Eliminar solo productos sin órdenes asociadas
                Product.objects.filter(orderitem__isnull=True).delete()
                Category.objects.all().delete()
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'No se pudieron eliminar todos los productos: {e}'))

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {json_file}'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Error decodificando JSON en: {json_file}'))
            return

        # Primero cargar categorías
        categories_map = {}
        for item in data:
            if item.get('model') == 'store.category':
                pk = item.get('pk')
                fields = item.get('fields', {})
                cat, created = Category.objects.update_or_create(
                    pk=pk,
                    defaults={
                        'name': fields.get('name'),
                        'slug': fields.get('slug'),
                    }
                )
                categories_map[pk] = cat
                self.stdout.write(f"{'Created' if created else 'Updated'} category: {cat.name}")

        # Luego cargar productos
        for item in data:
            if item.get('model') == 'store.product':
                pk = item.get('pk')
                fields = item.get('fields', {})
                
                category_id = fields.get('category')
                category = categories_map.get(category_id)
                
                # Convertir precio a Decimal
                try:
                    price = Decimal(str(fields.get('price', '0')))
                except:
                    price = Decimal('0')

                prod, created = Product.objects.update_or_create(
                    pk=pk,
                    defaults={
                        'name': fields.get('name'),
                        'slug': fields.get('slug'),
                        'description': fields.get('description', ''),
                        'price': price,
                        'stock_quantity': fields.get('stock', 0),
                        'category': category,
                        'tier': fields.get('tier', 'entry'),
                        'is_sensitive': fields.get('requires_declaration', False),
                        'phase': fields.get('phase', 1),
                        'is_active': fields.get('active', True),
                    }
                )
                
                if created:
                    self.stdout.write(f"[+] Created: {prod.name} - ${price}")
                else:
                    self.stdout.write(f"[*] Updated: {prod.name} - ${price}")

        total_products = Product.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'\n[OK] Load completed. Total products: {total_products}'
        ))
