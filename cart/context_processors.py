from .utils import cart_items


def cart_summary(request):
    items, subtotal, shipping, total, _ = cart_items(request)
    total_qty = sum(item['quantity'] for item in items)
    return {
        'cart_count': total_qty,
        'cart_subtotal': subtotal,
        'cart_total': total,
        'cart_shipping': shipping,
    }
