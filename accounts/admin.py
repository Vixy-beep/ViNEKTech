from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'full_name', 'phone', 'company', 'city', 'country')
	search_fields = ('user__username', 'full_name', 'company')

# Register your models here.
