from django.contrib import admin

from .models import Brand, Category, Collection, DailyOpsReport, NewsletterLead, Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
	model = ProductImage
	extra = 1


class ProductVariantInline(admin.TabularInline):
	model = ProductVariant
	extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', 'parent')
	prepopulated_fields = {'slug': ('name',)}
	search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('name', 'brand', 'category', 'tier', 'price', 'price_dop', 'margin_pct', 'stock', 'requires_declaration', 'phase', 'active')
	list_filter = ('tier', 'category', 'brand', 'requires_declaration', 'phase', 'is_featured', 'is_bestseller', 'active')
	prepopulated_fields = {'slug': ('name',)}
	search_fields = ('name', 'name_es', 'name_en', 'description', 'description_es', 'description_en')
	inlines = [ProductImageInline, ProductVariantInline]
	filter_horizontal = ('collections',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug')
	prepopulated_fields = {'slug': ('name',)}


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', 'is_featured')
	prepopulated_fields = {'slug': ('name',)}
	list_filter = ('is_featured',)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
	list_display = ('sku', 'product', 'title', 'price', 'price_dop', 'stock', 'active')
	list_filter = ('active',)
	search_fields = ('sku', 'product__name', 'title')


@admin.register(NewsletterLead)
class NewsletterLeadAdmin(admin.ModelAdmin):
	list_display = ('email', 'created_at')
	search_fields = ('email',)


@admin.register(DailyOpsReport)
class DailyOpsReportAdmin(admin.ModelAdmin):
	list_display = ('report_date', 'exchange_rate', 'products_updated', 'high_margin_count', 'created_at')
	search_fields = ('report_date',)

# Register your models here.
