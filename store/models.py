from django.db import models
from django.urls import reverse
from django.conf import settings
from decimal import Decimal
from django.utils import timezone
from django.utils.translation import get_language


class Category(models.Model):
	name = models.CharField(max_length=120)
	slug = models.SlugField(unique=True)
	parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, related_name='children')

	class Meta:
		verbose_name_plural = 'categories'
		ordering = ['name']

	def __str__(self):
		return self.name


class Brand(models.Model):
	name = models.CharField(max_length=120, unique=True)
	slug = models.SlugField(unique=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class Collection(models.Model):
	name = models.CharField(max_length=140)
	slug = models.SlugField(unique=True)
	description = models.TextField(blank=True)
	is_featured = models.BooleanField(default=False)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class Product(models.Model):
	TIER_ENTRY = 'entry'
	TIER_MID = 'mid'
	TIER_PRO = 'pro'
	TIER_CHOICES = [
		(TIER_ENTRY, 'Inicial'),
		(TIER_MID, 'Intermedio'),
		(TIER_PRO, 'Pro'),
	]

	name = models.CharField(max_length=180)
	name_es = models.CharField(max_length=180, blank=True)
	name_en = models.CharField(max_length=180, blank=True)
	slug = models.SlugField(unique=True)
	short_description = models.CharField(max_length=240, blank=True)
	short_description_es = models.CharField(max_length=240, blank=True)
	short_description_en = models.CharField(max_length=240, blank=True)
	description = models.TextField()
	description_es = models.TextField(blank=True)
	description_en = models.TextField(blank=True)
	category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
	brand = models.ForeignKey(Brand, blank=True, null=True, on_delete=models.SET_NULL, related_name='products')
	product_type = models.CharField(max_length=80, blank=True)
	tags = models.CharField(max_length=260, blank=True)
	collections = models.ManyToManyField(Collection, blank=True, related_name='products')
	price = models.DecimalField(max_digits=10, decimal_places=2)
	price_dop = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	currency = models.CharField(max_length=8, default='USD')
	cost_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	import_cost_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	total_cost_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	suggested_price_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	margin_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	last_exchange_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	stock = models.PositiveIntegerField(default=0)
	compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	stock_quantity = models.PositiveIntegerField(default=0)
	tier = models.CharField(max_length=10, choices=TIER_CHOICES, default=TIER_ENTRY)
	requires_declaration = models.BooleanField(default=False)
	phase = models.PositiveSmallIntegerField(default=1)
	use_case_declaration = models.TextField(blank=True)
	is_sensitive = models.BooleanField(default=False)
	is_featured = models.BooleanField(default=False)
	is_bestseller = models.BooleanField(default=False)
	active = models.BooleanField(default=True)
	is_active = models.BooleanField(default=True)
	meta_title = models.CharField(max_length=180, blank=True)
	meta_description = models.CharField(max_length=260, blank=True)
	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(default=timezone.now)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('store:product_detail', kwargs={'slug': self.slug})

	def get_meta_title(self):
		if self.meta_title:
			return self.meta_title
		return f'{self.localized_name} | ViNEK TECH'

	def get_meta_description(self):
		if self.meta_description:
			return self.meta_description
		return (self.localized_short_description or self.localized_description)[:255]

	@property
	def in_stock(self):
		return self.available_stock > 0

	@property
	def available_stock(self):
		if self.stock_quantity > 0:
			return self.stock_quantity
		return self.stock

	@property
	def effective_active(self):
		return self.active and self.is_active

	@property
	def declaration_required(self):
		return self.requires_declaration or self.is_sensitive

	@property
	def localized_name(self):
		lang = (get_language() or 'es').split('-')[0]
		if lang == 'en':
			return self.name_en or self.name
		return self.name_es or self.name

	@property
	def localized_short_description(self):
		lang = (get_language() or 'es').split('-')[0]
		if lang == 'en':
			return self.short_description_en or self.short_description or self.description
		return self.short_description_es or self.short_description or self.description_es or self.description

	@property
	def localized_description(self):
		lang = (get_language() or 'es').split('-')[0]
		if lang == 'en':
			return self.description_en or self.description
		return self.description_es or self.description

	@property
	def price_dop_value(self):
		if self.price_dop and self.price_dop > 0:
			return self.price_dop
		rate = Decimal(str(getattr(settings, 'USD_TO_DOP_RATE', '59.00')))
		return (Decimal(str(self.price)) * rate).quantize(Decimal('0.01'))

	def save(self, *args, **kwargs):
		self.updated_at = timezone.now()
		if not self.name_en:
			self.name_en = self.name
		if not self.description_en:
			self.description_en = self.description
		if not self.short_description_en and self.short_description:
			self.short_description_en = self.short_description
		if self.stock_quantity <= 0 and self.stock > 0:
			self.stock_quantity = self.stock
		if self.stock <= 0 and self.stock_quantity > 0:
			self.stock = self.stock_quantity
		if self.requires_declaration:
			self.is_sensitive = True
		self.active = self.is_active and self.active
		self.is_active = self.active
		if self.currency.upper() == 'USD':
			rate = Decimal(str(getattr(settings, 'USD_TO_DOP_RATE', '59.00')))
			self.last_exchange_rate = rate
			self.price_dop = (Decimal(str(self.price)) * rate).quantize(Decimal('0.01'))
		super().save(*args, **kwargs)


class ProductVariant(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
	title = models.CharField(max_length=120)
	sku = models.CharField(max_length=60, unique=True)
	barcode = models.CharField(max_length=100, blank=True)
	option_1_name = models.CharField(max_length=40, blank=True)
	option_1_value = models.CharField(max_length=60, blank=True)
	option_2_name = models.CharField(max_length=40, blank=True)
	option_2_value = models.CharField(max_length=60, blank=True)
	price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	price_dop = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	stock = models.PositiveIntegerField(default=0)
	active = models.BooleanField(default=True)

	class Meta:
		ordering = ['id']

	def __str__(self):
		return f'{self.product.name} - {self.title}'

	@property
	def price_dop_value(self):
		if self.price_dop and self.price_dop > 0:
			return self.price_dop
		base_price = Decimal(str(self.price)) if self.price is not None else Decimal(str(self.product.price))
		rate = Decimal(str(getattr(settings, 'USD_TO_DOP_RATE', '62.00')))
		return (base_price * rate).quantize(Decimal('0.01'))

	def save(self, *args, **kwargs):
		base_price = Decimal(str(self.price)) if self.price is not None else Decimal(str(self.product.price))
		rate = Decimal(str(getattr(settings, 'USD_TO_DOP_RATE', '62.00')))
		self.price_dop = (base_price * rate).quantize(Decimal('0.01'))
		super().save(*args, **kwargs)


class ProductImage(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
	image = models.ImageField(upload_to='products/')
	alt_text = models.CharField(max_length=160, blank=True)
	is_primary = models.BooleanField(default=False)

	class Meta:
		ordering = ['-is_primary', 'id']

	def __str__(self):
		return f'{self.product.name} image'


class NewsletterLead(models.Model):
	email = models.EmailField(unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.email


class DailyOpsReport(models.Model):
	report_date = models.DateField(unique=True)
	exchange_rate = models.DecimalField(max_digits=8, decimal_places=2)
	products_updated = models.PositiveIntegerField(default=0)
	high_margin_count = models.PositiveIntegerField(default=0)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-report_date']

	def __str__(self):
		return f'Daily Ops {self.report_date}'
