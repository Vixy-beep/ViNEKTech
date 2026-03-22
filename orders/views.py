from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from decimal import Decimal

from cart.utils import CART_SESSION_KEY, cart_items

from .forms import CheckoutForm
from .models import Coupon, Order, OrderItem
from .shipping import SHIPPING_ZONES, calculate_shipping, estimate_delivery


def checkout(request):
	items, subtotal, _, _, sensitive_items = cart_items(request)
	if not items:
		return redirect('cart:detail')

	initial = {}
	if request.user.is_authenticated and hasattr(request.user, 'profile'):
		profile = request.user.profile
		initial = {
			'full_name': profile.full_name,
			'email': request.user.email,
			'phone': profile.phone,
			'shipping_address': profile.address,
			'city': profile.city,
			'country': profile.country,
			'shipping_zone': 'santo_domingo',
		}

	if request.method == 'POST':
		form = CheckoutForm(request.POST, requires_declaration=sensitive_items)
		if form.is_valid():
			zone = form.cleaned_data['shipping_zone']
			shipping = calculate_shipping(subtotal, zone)
			discount_amount = Decimal('0')
			coupon_code = form.cleaned_data.get('coupon_code', '').strip().upper()
			coupon = None
			if coupon_code:
				coupon = Coupon.objects.filter(code=coupon_code, active=True).first()
				if coupon:
					if coupon.discount_percent:
						discount_amount += (subtotal * Decimal(coupon.discount_percent) / Decimal('100')).quantize(Decimal('0.01'))
					if coupon.discount_fixed:
						discount_amount += coupon.discount_fixed
					discount_amount = min(discount_amount, subtotal)
				else:
					messages.warning(request, 'El cupon no existe o no esta disponible.')

			total = subtotal - discount_amount + shipping
			declaration_text = ''
			if sensitive_items:
				declaration_text = (
					'Declaro que los productos adquiridos serán utilizados exclusivamente '
					'para fines legales de laboratorio, auditoría autorizada y educación técnica.'
				)

			order = Order.objects.create(
				user=request.user if request.user.is_authenticated else None,
				email=form.cleaned_data['email'],
				full_name=form.cleaned_data['full_name'],
				phone=form.cleaned_data['phone'],
				shipping_address=form.cleaned_data['shipping_address'],
				city=form.cleaned_data['city'],
				country=form.cleaned_data['country'],
				shipping_zone=zone,
				subtotal=subtotal,
				discount_amount=discount_amount,
				shipping_cost=shipping,
				total=total,
				estimated_delivery=estimate_delivery(zone),
				coupon_code=coupon.code if coupon else '',
				declaration_text=declaration_text,
				declaration_accepted=form.cleaned_data.get('declaration_accepted', False),
				declaration_accepted_at=timezone.now() if sensitive_items else None,
				declaration_ip=request.META.get('REMOTE_ADDR'),
				declaration_user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
			)

			for item in items:
				product = item['product']
				quantity = item['quantity']
				OrderItem.objects.create(
					order=order,
					product=product,
					quantity=quantity,
					unit_price=item['unit_price'],
				)
				product.stock_quantity = max(product.stock_quantity - quantity, 0)
				product.stock = max(product.stock - quantity, 0)
				product.save(update_fields=['stock_quantity', 'stock'])

			request.session[CART_SESSION_KEY] = {}
			request.session.modified = True
			return redirect('orders:confirmation', order_id=order.id)
	else:
		form = CheckoutForm(initial=initial, requires_declaration=sensitive_items)

	return render(
		request,
		'orders/checkout.html',
		{
			'form': form,
			'items': items,
			'subtotal': subtotal,
			'shipping': calculate_shipping(subtotal, form['shipping_zone'].value() or 'santo_domingo'),
			'total': subtotal + calculate_shipping(subtotal, form['shipping_zone'].value() or 'santo_domingo'),
			'shipping_zones': SHIPPING_ZONES,
			'sensitive_items': sensitive_items,
		},
	)


def order_confirmation(request, order_id):
	order = get_object_or_404(Order, pk=order_id)
	return render(request, 'orders/confirmation.html', {'order': order})


def track_order(request):
	order = None
	error = ''
	if request.method == 'POST':
		order_id = request.POST.get('order_id', '').strip()
		email = request.POST.get('email', '').strip()
		if order_id and email:
			order = Order.objects.filter(pk=order_id, email__iexact=email).first()
		if not order:
			error = 'No encontramos una orden con esos datos.'
	return render(request, 'orders/tracking.html', {'order': order, 'error': error})


@login_required
def account_orders(request):
	return render(request, 'accounts/account.html', {'orders': request.user.orders.all()})

# Create your views here.
