import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from store.models import Product


class Command(BaseCommand):
    help = 'Sincroniza pricing desde CSV (costos, margenes y precio sugerido).'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='vinektech_pricing.csv')
        parser.add_argument('--rate', type=float, help='Tasa USD->DOP para recalculo.')
        parser.add_argument('--apply-suggested-usd', action='store_true', help='Aplicar suggested_price_usd al campo price.')
        parser.add_argument('--mark-high-margin', action='store_true', help='Marcar como destacados productos con margen >= 120%%.')

    def _to_decimal(self, value):
        if value is None or value == '':
            return Decimal('0')
        return Decimal(str(value).strip())

    def handle(self, *args, **options):
        csv_path = Path(options['file'])
        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f'No existe el archivo: {csv_path}'))
            return

        rate = Decimal(str(options.get('rate') or settings.USD_TO_DOP_RATE))
        updated = 0
        missing = []

        with csv_path.open(newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                slug = row.get('slug', '').strip()
                if not slug:
                    continue
                product = Product.objects.filter(slug=slug).first()
                if not product:
                    missing.append(slug)
                    continue

                product.cost_usd = self._to_decimal(row.get('cost_usd'))
                product.import_cost_usd = self._to_decimal(row.get('import_cost_usd'))
                product.total_cost_usd = self._to_decimal(row.get('total_cost_usd'))
                product.suggested_price_usd = self._to_decimal(row.get('suggested_price_usd'))
                product.margin_pct = self._to_decimal(row.get('margin_pct'))
                product.last_exchange_rate = rate

                tier = (row.get('tier') or '').strip().lower()
                if tier in {'entry', 'mid', 'pro'}:
                    product.tier = tier

                phase_value = (row.get('phase') or '').strip()
                if phase_value.isdigit():
                    product.phase = int(phase_value)

                if options.get('apply_suggested_usd') and product.suggested_price_usd > 0:
                    product.price = product.suggested_price_usd

                product.price_dop = (product.price * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                if options.get('mark_high_margin'):
                    product.is_featured = product.margin_pct >= Decimal('120')
                    product.is_bestseller = product.margin_pct >= Decimal('100')

                product.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Productos actualizados: {updated}'))
        if missing:
            self.stdout.write(self.style.WARNING(f'Slugs no encontrados ({len(missing)}): {", ".join(missing[:10])}'))
