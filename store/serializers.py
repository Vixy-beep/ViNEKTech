from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'name_es',
            'name_en',
            'slug',
            'product_type',
            'tags',
            'short_description',
            'short_description_es',
            'short_description_en',
            'description',
            'description_es',
            'description_en',
            'price',
            'cost_usd',
            'import_cost_usd',
            'total_cost_usd',
            'suggested_price_usd',
            'margin_pct',
            'compare_at_price',
            'stock_quantity',
            'stock',
            'tier',
            'requires_declaration',
            'phase',
            'active',
            'is_featured',
            'is_bestseller',
            'category',
        ]
