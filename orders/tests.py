from django.test import TestCase
from django.urls import reverse

from store.models import Category, Product

from .models import Order


class OrderTests(TestCase):
	def setUp(self):
		category = Category.objects.create(name='Pentest', slug='pentest')
		self.product = Product.objects.create(
			name='Pentest Stick',
			slug='pentest-stick',
			description='Tool',
			category=category,
			price='500.00',
			stock_quantity=4,
			tier='entry',
			is_sensitive=True,
		)

	def test_checkout_creates_order(self):
		self.client.get(reverse('cart:add', args=[self.product.id]))
		payload = {
			'full_name': 'Test User',
			'email': 'test@example.com',
			'phone': '8090000000',
			'shipping_address': 'Calle 1',
			'city': 'Santo Domingo',
			'country': 'República Dominicana',
			'shipping_zone': 'santo_domingo',
			'coupon_code': '',
			'declaration_accepted': True,
		}
		response = self.client.post(reverse('orders:checkout'), payload)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(Order.objects.count(), 1)

# Create your tests here.
