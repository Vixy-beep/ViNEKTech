from deep_translator import GoogleTranslator
from django.core.management.base import BaseCommand

from store.models import Product


class Command(BaseCommand):
    help = 'Autotraduce nombre/descripcion entre EN y ES segun contenido existente.'

    def add_arguments(self, parser):
        parser.add_argument('--source', type=str, choices=['en', 'es', 'auto'], default='auto')
        parser.add_argument('--limit', type=int, default=0)

    def handle(self, *args, **options):
        source = options['source']
        limit = options['limit']

        qs = Product.objects.all().order_by('id')
        if limit and limit > 0:
            qs = qs[:limit]

        updated = 0
        failed_remote = 0
        en_to_es = GoogleTranslator(source='auto' if source == 'auto' else source, target='es')
        es_to_en = GoogleTranslator(source='auto' if source == 'auto' else source, target='en')

        for product in qs:
            changed = False

            if not product.name_en:
                product.name_en = product.name
                changed = True
            if not product.description_en:
                product.description_en = product.description
                changed = True

            if not product.name_es and product.name_en:
                try:
                    product.name_es = en_to_es.translate(product.name_en)
                except Exception:
                    failed_remote += 1
                    product.name_es = product.name_en
                changed = True
            if not product.description_es and product.description_en:
                try:
                    product.description_es = en_to_es.translate(product.description_en)
                except Exception:
                    failed_remote += 1
                    product.description_es = product.description_en
                changed = True

            if not product.short_description_es and product.short_description_en:
                try:
                    product.short_description_es = en_to_es.translate(product.short_description_en)
                except Exception:
                    failed_remote += 1
                    product.short_description_es = product.short_description_en
                changed = True
            if not product.short_description_en and product.short_description_es:
                try:
                    product.short_description_en = es_to_en.translate(product.short_description_es)
                except Exception:
                    failed_remote += 1
                    product.short_description_en = product.short_description_es
                changed = True

            if changed:
                product.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Productos traducidos/actualizados: {updated}'))
        if failed_remote:
            self.stdout.write(self.style.WARNING(f'Traducciones remotas no disponibles en {failed_remote} intentos, se aplico fallback local.'))
