from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from decimal import Decimal
import stripe
from django.conf import settings

from cart.utils import CART_SESSION_KEY, cart_items

from .forms import CheckoutForm
from .models import Coupon, Order, OrderItem
from .shipping import SHIPPING_ZONES, calculate_shipping, estimate_delivery

stripe.api_key = settings.STRIPE_SECRET_KEY


def _get_progress_stage(order):
	if order.status in {Order.STATUS_SHIPPED, Order.STATUS_DELIVERED}:
		return 3
	if order.status == Order.STATUS_PAID or order.paid:
		return 2
	return 1


def _attach_email_orders_to_user(user):
	"""Attach historical guest orders to a logged-in user by matching email."""
	if not user.is_authenticated or not user.email:
		return 0
	return Order.objects.filter(user__isnull=True, email__iexact=user.email).update(user=user)


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

	if order.user:
		if not request.user.is_authenticated:
			messages.info(request, 'Inicia sesion para ver tu pedido.')
			return redirect('accounts:login')
		if request.user != order.user:
			messages.error(request, 'No tienes acceso a ese pedido.')
			return redirect('orders:tracking')
	elif request.user.is_authenticated and request.user.email and order.email.lower() == request.user.email.lower():
		order.user = request.user
		order.save(update_fields=['user'])

	order.progress_stage = _get_progress_stage(order)

	return render(
		request,
		'orders/confirmation.html',
		{
			'order': order,
			'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
		},
	)


@login_required
def track_order(request):
	_attach_email_orders_to_user(request.user)
	orders = request.user.orders.prefetch_related('items__product').all()
	for current in orders:
		current.progress_stage = _get_progress_stage(current)
	selected_order = None
	selected_id = request.GET.get('order', '').strip()
	if selected_id.isdigit():
		selected_order = orders.filter(pk=int(selected_id)).first()
	if selected_order is None:
		selected_order = orders.first()
	return render(request, 'orders/tracking.html', {'orders': orders, 'order': selected_order})


@login_required
def account_orders(request):
	_attach_email_orders_to_user(request.user)
	return render(request, 'accounts/account.html', {'orders': request.user.orders.all()})


@require_http_methods(['POST'])
def create_checkout_session(request):
	"""Create a Stripe Checkout Session for an existing order"""
	try:
		order_id = request.POST.get('order_id', '').strip()
		order = get_object_or_404(Order, pk=order_id)
		
		# Security: only allow user to pay their own orders
		if order.user and request.user != order.user:
			return JsonResponse({'error': 'Acceso denegado'}, status=403)
		
		# Verify email for non-authenticated orders
		if not order.user:
			if request.user.is_authenticated and request.user.email.lower() == order.email.lower():
				order.user = request.user
				order.save(update_fields=['user'])
			elif request.POST.get('email', '').lower() != order.email.lower():
				return JsonResponse({'error': 'Email no coincide'}, status=403)
		
		# Create line items for Stripe
		line_items = []
		for item in order.items.all():
			line_items.append({
				'price_data': {
					'currency': 'usd',  # Stripe uses USD
					'unit_amount': int(item.unit_price * 100),  # Convert to cents
					'product_data': {
						'name': item.product.localized_name,
						'description': f"SKU: {item.product.slug}",
						'images': [item.product.image_url] if item.product.image_url else [],
					},
				},
				'quantity': item.quantity,
			})
		
		# Add shipping as line item
		line_items.append({
			'price_data': {
				'currency': 'usd',
				'unit_amount': int((order.shipping_cost / Decimal('62')) * 100),  # Convert DOP to USD
				'product_data': {
					'name': f'Envio ({order.get_shipping_zone_display()})',
				},
			},
			'quantity': 1,
		})
		
		# Add discount if applicable
		if order.discount_amount > 0:
			line_items.append({
				'price_data': {
					'currency': 'usd',
					'unit_amount': -int((order.discount_amount / Decimal('62')) * 100),  # Negative for discount
					'product_data': {
						'name': f'Descuento ({order.coupon_code})',
					},
				},
				'quantity': 1,
			})
		
		# Create Stripe session
		session = stripe.checkout.Session.create(
			payment_method_types=['card'],
			line_items=line_items,
			mode='payment',
			success_url=request.build_absolute_uri(reverse('orders:confirmation', kwargs={'order_id': order.id})),
			cancel_url=request.build_absolute_uri(reverse('orders:tracking')),
			customer_email=order.email,
			client_reference_id=str(order.id),
			metadata={
				'order_id': str(order.id),
				'customer_name': order.full_name,
				'country': order.country,
			},
		)
		
		return JsonResponse({'sessionId': session.id})
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(['POST'])
def stripe_webhook(request):
	"""Handle Stripe webhook events (payment success, failure, etc.)"""
	import json
	
	payload = request.body
	sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
	
	try:
		event = stripe.Webhook.construct_event(
			payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
		)
	except ValueError:
		return JsonResponse({'error': 'Invalid payload'}, status=400)
	except stripe.error.SignatureVerificationError:
		return JsonResponse({'error': 'Invalid signature'}, status=400)
	
	# Handle checkout session completed
	if event['type'] == 'checkout.session.completed':
		session = event['data']['object']
		order_id = session.get('client_reference_id')
		
		if order_id:
			order = Order.objects.filter(pk=order_id).first()
			if order:
				order.paid = True
				if order.status == Order.STATUS_PENDING:
					order.status = Order.STATUS_PAID
				order.payment_method = 'stripe'
				order.stripe_session_id = session['id']
				order.save(update_fields=['paid', 'status', 'payment_method', 'stripe_session_id'])
				
				# Send confirmation email
				order.send_confirmation_email()
	
	return JsonResponse({'status': 'success'}, status=200)

# Create your views here.
