from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone

from store.models import DailyOpsReport, Product
from store.pricing import fetch_usd_dop_rate, recalculate_prices


class Command(BaseCommand):
    help = 'Ejecuta rutina diaria: tasa FX, recalculo de precios y reporte de margenes.'

    def handle(self, *args, **options):
        rate = fetch_usd_dop_rate()
        updated = recalculate_prices(rate)

        high_margin_products = Product.objects.filter(margin_pct__gte=120, active=True).order_by('-margin_pct')
        top_slugs = ', '.join(high_margin_products.values_list('slug', flat=True)[:10])

        report, _ = DailyOpsReport.objects.update_or_create(
            report_date=timezone.localdate(),
            defaults={
                'exchange_rate': rate,
                'products_updated': updated,
                'high_margin_count': high_margin_products.count(),
                'notes': f'Top margen: {top_slugs}',
            },
        )

        message = (
            f'Reporte diario ViNEK TECH\n'
            f'Fecha: {report.report_date}\n'
            f'Tasa USD->DOP: {report.exchange_rate}\n'
            f'Productos actualizados: {report.products_updated}\n'
            f'Productos de margen >= 120%: {report.high_margin_count}\n'
            f'Top slugs: {top_slugs}\n'
        )

        recipients = [email.strip() for email in getattr(settings, 'REPORT_EMAIL_TO', '').split(',') if email.strip()]
        if recipients:
            send_mail('ViNEK TECH - Daily Ops Report', message, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=True)

        self.stdout.write(self.style.SUCCESS('Reporte diario generado correctamente.'))
