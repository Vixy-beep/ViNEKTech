from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class StoreTests(TestCase):
	def setUp(self):
		category = Category.objects.create(name='Networking', slug='networking')
		Product.objects.create(
			name='Secure Router',
			slug='secure-router',
			description='Router de pruebas.',
			short_description='Router seguro',
			category=category,
			price='1200.00',
			stock_quantity=5,
			tier='entry',
			is_active=True,
		)

	def test_home_loads(self):
		response = self.client.get(reverse('store:home'))
		self.assertEqual(response.status_code, 200)

	def test_product_meta_title_fallback(self):
		product = Product.objects.get(slug='secure-router')
		self.assertIn('ViNEK TECH', product.get_meta_title())

# Create your tests here.
