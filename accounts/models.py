from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	full_name = models.CharField(max_length=180, blank=True)
	phone = models.CharField(max_length=40, blank=True)
	company = models.CharField(max_length=140, blank=True)
	address = models.CharField(max_length=220, blank=True)
	city = models.CharField(max_length=120, blank=True)
	country = models.CharField(max_length=120, default='República Dominicana')

	def __str__(self):
		return f'Profile: {self.user.username}'
