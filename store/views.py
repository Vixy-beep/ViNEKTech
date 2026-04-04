from django.db.models import Q
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import json

from .models import Category, NewsletterLead, Product


def home(request):
	# Flipper Zero primero si existe y está featured, luego otros featured
	flipper = Product.objects.filter(active=True, slug='flipper-zero', is_featured=True).first()
	other_featured = Product.objects.filter(active=True, is_featured=True).exclude(slug='flipper-zero')[:7]
	featured_products = []
	if flipper:
		featured_products.append(flipper)
		featured_products.extend(list(other_featured))
	else:
		featured_products = list(Product.objects.filter(active=True, is_featured=True)[:8])
	
	latest_products = Product.objects.filter(active=True)[:8]
	tiers = {
		'entry': Product.objects.filter(active=True, tier=Product.TIER_ENTRY)[:4],
		'mid': Product.objects.filter(active=True, tier=Product.TIER_MID)[:4],
		'pro': Product.objects.filter(active=True, tier=Product.TIER_PRO)[:4],
	}
	return render(
		request,
		'store/home.html',
		{
			'featured_products': featured_products,
			'latest_products': latest_products,
			'tiers': tiers,
		},
	)


@require_http_methods(['POST'])
def newsletter_signup(request):
	email = request.POST.get('email', '').strip().lower()
	if email:
		NewsletterLead.objects.get_or_create(email=email)
	return redirect('store:home')


def catalog(request):
	products = Product.objects.filter(active=True).select_related('category')
	categories = Category.objects.all()

	query = request.GET.get('q', '').strip()
	category_slug = request.GET.get('category', '').strip()
	tier = request.GET.get('tier', '').strip()
	min_price = request.GET.get('min_price', '').strip()
	max_price = request.GET.get('max_price', '').strip()
	sort = request.GET.get('sort', '-created_at').strip()
	per_page_raw = request.GET.get('per_page', '24').strip()
	allowed_per_page = {12, 24, 48, 96}
	try:
		per_page = int(per_page_raw)
	except (TypeError, ValueError):
		per_page = 24
	if per_page not in allowed_per_page:
		per_page = 24

	if query:
		products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
	if category_slug:
		products = products.filter(category__slug=category_slug)
	if tier in {Product.TIER_ENTRY, Product.TIER_MID, Product.TIER_PRO}:
		products = products.filter(tier=tier)
	if min_price:
		products = products.filter(price__gte=min_price)
	if max_price:
		products = products.filter(price__lte=max_price)

	sort_map = {
		'price_asc': 'price',
		'price_desc': '-price',
		'newest': '-created_at',
		'name': 'name',
	}
	products = products.order_by(sort_map.get(sort, '-created_at'))
	paginator = Paginator(products, per_page)
	page_obj = paginator.get_page(request.GET.get('page'))

	return render(
		request,
		'store/catalog.html',
		{
			'products': page_obj,
			'categories': categories,
			'query': query,
			'selected_category': category_slug,
			'selected_tier': tier,
			'sort': sort,
			'min_price': min_price,
			'max_price': max_price,
			'per_page': per_page,
			'total_results': paginator.count,
			'page_obj': page_obj,
		},
	)


def product_detail(request, slug):
	product = get_object_or_404(Product.objects.select_related('category'), slug=slug, active=True)
	related_products = Product.objects.filter(active=True, category=product.category).exclude(pk=product.pk)[:4]
	json_ld = {
		'@context': 'https://schema.org',
		'@type': 'Product',
		'name': product.localized_name,
		'description': product.get_meta_description(),
		'category': product.category.name,
		'offers': {
			'@type': 'Offer',
			'priceCurrency': 'DOP',
			'price': str(product.price),
			'availability': 'https://schema.org/InStock' if product.in_stock else 'https://schema.org/OutOfStock',
		},
	}
	return render(
		request,
		'store/product_detail.html',
		{
			'product': product,
			'related_products': related_products,
			'json_ld': json.dumps(json_ld, ensure_ascii=False),
		},
	)


def terms(request):
	return render(request, 'store/terms.html')


def privacy(request):
	return render(request, 'store/privacy.html')


def responsible_use(request):
	return render(request, 'store/responsible_use.html')


def robots_txt(request):
	lines = [
		'User-agent: *',
		'Allow: /',
		'Disallow: /admin/',
		f'Sitemap: {request.scheme}://{request.get_host()}{reverse("store:sitemap")}',
	]
	return HttpResponse('\n'.join(lines), content_type='text/plain')


def sitemap_xml(request):
	products = Product.objects.filter(active=True)
	urls = [
		f'{request.scheme}://{request.get_host()}{reverse("store:home")}',
		f'{request.scheme}://{request.get_host()}{reverse("store:catalog")}',
	]
	for product in products:
		urls.append(f'{request.scheme}://{request.get_host()}{product.get_absolute_url()}')
	xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
	for url in urls:
		xml.append('<url>')
		xml.append(f'<loc>{url}</loc>')
		xml.append('</url>')
	xml.append('</urlset>')
	return HttpResponse('\n'.join(xml), content_type='application/xml')

# Create your views here.
