from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import UserProfile


def signup(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			UserProfile.objects.get_or_create(user=user)
			login(request, user)
			return redirect('store:home')
	else:
		form = UserCreationForm()
	return render(request, 'accounts/signup.html', {'form': form})


@login_required
def profile(request):
	profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
	if request.method == 'POST':
		profile_obj.full_name = request.POST.get('full_name', '')
		profile_obj.phone = request.POST.get('phone', '')
		profile_obj.company = request.POST.get('company', '')
		profile_obj.address = request.POST.get('address', '')
		profile_obj.city = request.POST.get('city', '')
		profile_obj.country = request.POST.get('country', 'República Dominicana')
		profile_obj.save()
		return redirect('accounts:profile')
	return render(request, 'accounts/profile.html', {'profile': profile_obj})

# Create your views here.
