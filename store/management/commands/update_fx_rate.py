from decimal import Decimal

from django.core.management.base import BaseCommand

from store.pricing import fetch_usd_dop_rate, recalculate_prices


class Command(BaseCommand):
    help = 'Obtiene tasa USD->DOP desde API y recalcula precios DOP.'

    def add_arguments(self, parser):
        parser.add_argument('--rate', type=float, help='Forzar tasa manual.')

    def handle(self, *args, **options):
        rate = Decimal(str(options['rate'])) if options.get('rate') else fetch_usd_dop_rate()
        updated = recalculate_prices(rate)
        self.stdout.write(self.style.SUCCESS(f'Tasa aplicada: {rate}. Productos actualizados: {updated}.'))
