from django.contrib import admin

from .models import Coupon, Order, OrderItem


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0
	readonly_fields = ('product', 'quantity', 'unit_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'full_name', 'email', 'status', 'payment_method', 'total', 'created_at')
	list_filter = ('status', 'payment_method', 'paid', 'declaration_accepted', 'created_at')
	search_fields = ('full_name', 'email', 'tracking_number', 'stripe_session_id')
	readonly_fields = ('stripe_session_id', 'created_at', 'updated_at')
	fieldsets = (
		('Cliente', {
			'fields': ('user', 'full_name', 'email', 'phone')
		}),
		('Envío', {
			'fields': ('shipping_address', 'city', 'country', 'shipping_zone', 'estimated_delivery', 'tracking_number')
		}),
		('Valores', {
			'fields': ('subtotal', 'discount_amount', 'shipping_cost', 'total', 'coupon_code')
		}),
		('Pago', {
			'fields': ('status', 'paid', 'payment_method', 'payment_provider', 'payment_reference', 'stripe_session_id')
		}),
		('Declaración (si aplica)', {
			'fields': ('declaration_accepted', 'declaration_accepted_at', 'declaration_text', 'declaration_ip', 'declaration_user_agent'),
			'classes': ('collapse',)
		}),
		('Metadata', {
			'fields': ('created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)
	inlines = [OrderItemInline]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
	list_display = ('code', 'discount_percent', 'discount_fixed', 'active', 'valid_from', 'valid_until')
	list_filter = ('active',)
	search_fields = ('code',)

# Register your models here.
