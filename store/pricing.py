from decimal import Decimal, ROUND_HALF_UP
import json
from urllib.request import urlopen

from django.conf import settings

from .models import Product


def fetch_usd_dop_rate():
    default_rate = Decimal(str(getattr(settings, 'USD_TO_DOP_RATE', '62')))
    urls = [
        'https://open.er-api.com/v6/latest/USD',
        'https://api.exchangerate.host/latest?base=USD&symbols=DOP',
    ]

    for url in urls:
        try:
            with urlopen(url, timeout=8) as response:
                payload = json.loads(response.read().decode('utf-8'))
                rates = payload.get('rates', {})
                dop = rates.get('DOP')
                if dop:
                    return Decimal(str(dop)).quantize(Decimal('0.01'))
        except Exception:
            continue

    return default_rate


def recalculate_prices(rate):
    updated = 0
    for product in Product.objects.all():
        product.price_dop = (product.price * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        product.last_exchange_rate = rate
        product.save(update_fields=['price_dop', 'last_exchange_rate', 'updated_at'])
        for variant in product.variants.all():
            base_price = variant.price if variant.price is not None else product.price
            variant.price_dop = (base_price * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            variant.save(update_fields=['price_dop'])
        updated += 1
    return updated
