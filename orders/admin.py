from django.contrib import admin

from .models import Coupon, Order, OrderItem


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0
	readonly_fields = ('product', 'quantity', 'unit_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'full_name', 'email', 'status', 'shipping_zone', 'total', 'created_at')
	list_filter = ('status', 'declaration_accepted', 'created_at')
	search_fields = ('full_name', 'email', 'tracking_number')
	inlines = [OrderItemInline]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
	list_display = ('code', 'discount_percent', 'discount_fixed', 'active', 'valid_from', 'valid_until')
	list_filter = ('active',)
	search_fields = ('code',)

# Register your models here.
