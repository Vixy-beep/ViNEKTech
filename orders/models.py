from django.db import models
from django.contrib.auth.models import User

from store.models import Product


class Order(models.Model):
	STATUS_PENDING = 'pending'
	STATUS_PAID = 'paid'
	STATUS_SHIPPED = 'shipped'
	STATUS_DELIVERED = 'delivered'
	STATUS_CHOICES = [
		(STATUS_PENDING, 'Pending'),
		(STATUS_PAID, 'Paid'),
		(STATUS_SHIPPED, 'Shipped'),
		(STATUS_DELIVERED, 'Delivered'),
	]

	user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='orders')
	status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
	email = models.EmailField()
	full_name = models.CharField(max_length=180)
	phone = models.CharField(max_length=40)
	shipping_address = models.CharField(max_length=220)
	city = models.CharField(max_length=120)
	country = models.CharField(max_length=120, default='República Dominicana')
	shipping_zone = models.CharField(max_length=30, default='santo_domingo')
	subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	estimated_delivery = models.DateField(blank=True, null=True)
	tracking_number = models.CharField(max_length=80, blank=True)
	coupon_code = models.CharField(max_length=40, blank=True)
	payment_provider = models.CharField(max_length=40, default='manual')
	payment_reference = models.CharField(max_length=120, blank=True)
	declaration_text = models.TextField(blank=True)
	declaration_accepted = models.BooleanField(default=False)
	declaration_accepted_at = models.DateTimeField(blank=True, null=True)
	declaration_ip = models.GenericIPAddressField(blank=True, null=True)
	declaration_user_agent = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'Order #{self.pk}'


class Coupon(models.Model):
	code = models.CharField(max_length=40, unique=True)
	description = models.CharField(max_length=180, blank=True)
	discount_percent = models.PositiveSmallIntegerField(default=0)
	discount_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	active = models.BooleanField(default=True)
	valid_from = models.DateTimeField(blank=True, null=True)
	valid_until = models.DateTimeField(blank=True, null=True)

	def __str__(self):
		return self.code


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
	product = models.ForeignKey(Product, on_delete=models.PROTECT)
	quantity = models.PositiveIntegerField(default=1)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return f'{self.product.name} x {self.quantity}'

	@property
	def line_total(self):
		return self.quantity * self.unit_price
