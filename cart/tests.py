from django.test import TestCase
from django.urls import reverse

from store.models import Category, Product


class CartTests(TestCase):
	def setUp(self):
		category = Category.objects.create(name='Lab', slug='lab')
		self.product = Product.objects.create(
			name='Lab Key',
			slug='lab-key',
			description='Key',
			category=category,
			price='100.00',
			stock_quantity=3,
			tier='entry',
		)

	def test_add_to_cart(self):
		self.client.get(reverse('cart:add', args=[self.product.id]))
		response = self.client.get(reverse('cart:detail'))
		self.assertContains(response, 'Lab Key')

# Create your tests here.
