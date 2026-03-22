from decimal import Decimal
from django.conf import settings

from store.models import Product

CART_SESSION_KEY = 'vinek_cart'


def get_cart(request):
    return request.session.setdefault(CART_SESSION_KEY, {})


def cart_items(request):
    cart = get_cart(request)
    product_ids = [int(pk) for pk in cart.keys()]
    products = Product.objects.filter(id__in=product_ids, active=True)
    products_map = {product.id: product for product in products}

    items = []
    subtotal = Decimal('0')
    sensitive_items = False

    for product_id, quantity in cart.items():
        product = products_map.get(int(product_id))
        if not product:
            continue
        qty = int(quantity)
        price_dop = product.price_dop_value
        line_total = price_dop * qty
        subtotal += line_total
        sensitive_items = sensitive_items or product.declaration_required
        items.append(
            {
                'product': product,
                'quantity': qty,
                'unit_price': price_dop,
                'line_total': line_total,
            }
        )

    shipping = Decimal('0') if subtotal >= Decimal('5000') else Decimal('250')
    total = subtotal + shipping
    return items, subtotal, shipping, total, sensitive_items