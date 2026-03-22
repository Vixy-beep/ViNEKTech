from rest_framework import generics

from .models import Product
from .serializers import ProductSerializer


class ProductListApi(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('category')
        q = self.request.query_params.get('q', '').strip()
        tier = self.request.query_params.get('tier', '').strip()
        if q:
            qs = qs.filter(name__icontains=q)
        if tier:
            qs = qs.filter(tier=tier)
        return qs
