from django.shortcuts import get_object_or_404, redirect, render

from store.models import Product

from .utils import CART_SESSION_KEY, cart_items, get_cart


def cart_detail(request):
	items, subtotal, shipping, total, _ = cart_items(request)
	return render(
		request,
		'cart/detail.html',
		{
			'items': items,
			'subtotal': subtotal,
			'shipping': shipping,
			'total': total,
		},
	)


def cart_add(request, product_id):
	product = get_object_or_404(Product, pk=product_id, active=True)
	cart = get_cart(request)
	current_qty = int(cart.get(str(product.id), 0))
	cart[str(product.id)] = min(current_qty + 1, product.available_stock)
	request.session.modified = True
	return redirect('cart:detail')


def cart_update(request, product_id):
	product = get_object_or_404(Product, pk=product_id, active=True)
	cart = get_cart(request)
	quantity = int(request.POST.get('quantity', 1))
	if quantity <= 0:
		cart.pop(str(product.id), None)
	else:
		cart[str(product.id)] = min(quantity, product.available_stock)
	request.session.modified = True
	return redirect('cart:detail')


def cart_remove(request, product_id):
	cart = get_cart(request)
	cart.pop(str(product_id), None)
	request.session.modified = True
	return redirect('cart:detail')


def cart_clear(request):
	request.session[CART_SESSION_KEY] = {}
	request.session.modified = True
	return redirect('cart:detail')

# Create your views here.
