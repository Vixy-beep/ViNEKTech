from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

FREE_SHIPPING_THRESHOLD = Decimal('5000')

SHIPPING_ZONES = {
    'santo_domingo': {'label': 'Santo Domingo', 'rate': Decimal('200'), 'eta_days': 14},
    'interior': {'label': 'Interior del pais', 'rate': Decimal('350'), 'eta_days': 14},
    'international': {'label': 'Internacional', 'rate': Decimal('1200'), 'eta_days': 21},
}


def calculate_shipping(subtotal, zone_key):
    if subtotal >= FREE_SHIPPING_THRESHOLD:
        return Decimal('0')
    zone = SHIPPING_ZONES.get(zone_key, SHIPPING_ZONES['santo_domingo'])
    return zone['rate']


def estimate_delivery(zone_key):
    zone = SHIPPING_ZONES.get(zone_key, SHIPPING_ZONES['santo_domingo'])
    return timezone.localdate() + timedelta(days=zone['eta_days'])
