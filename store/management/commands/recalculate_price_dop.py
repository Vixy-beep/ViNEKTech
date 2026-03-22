from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand

from store.pricing import recalculate_prices


class Command(BaseCommand):
    help = 'Recalcula price_dop para todos los productos segun la tasa USD_TO_DOP_RATE o una tasa manual.'

    def add_arguments(self, parser):
        parser.add_argument('--rate', type=float, help='Tasa USD a DOP. Ejemplo: 61.8')

    def handle(self, *args, **options):
        rate = Decimal(str(options.get('rate') or settings.USD_TO_DOP_RATE))
        updated = recalculate_prices(rate)

        self.stdout.write(self.style.SUCCESS(f'price_dop recalculado para {updated} productos con tasa {rate}.'))
