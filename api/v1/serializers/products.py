"""
Serializers for products app - Categories, Products, and Variants.
"""
from rest_framework import serializers
from products.models import (
    Category, Product, ProductVariant, Color, Size,
    ProductImages, VariantImage
)


class ColorSerializer(serializers.ModelSerializer):
    """Serializer for product colors."""
    
    class Meta:
        model = Color
        fields = ['id', 'name', 'hex_code']


class SizeSerializer(serializers.ModelSerializer):
    """Serializer for product sizes."""
    
    class Meta:
        model = Size
        fields = ['id', 'name', 'order']


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for additional product images."""
    
    class Meta:
        model = ProductImages
        fields = ['id', 'image', 'order']


class VariantImageSerializer(serializers.ModelSerializer):
    """Serializer for variant images."""
    
    class Meta:
        model = VariantImage
        fields = ['id', 'image', 'order']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for product variants."""
    color = ColorSerializer(read_only=True)
    sizes = SizeSerializer(many=True, read_only=True)
    images = VariantImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = ['id', 'color', 'sizes', 'sku_code', 'pcs_carton', 
                  'is_available', 'images']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories."""
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'products_count']
    
    def get_products_count(self, obj):
        return obj.products.filter(is_available=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for product list."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'category_name', 'image', 
                  'pcs_carton', 'is_available']


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product."""
    category = CategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    additional_images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'category',
                  'image', 'pcs_carton', 'is_available',
                  'variants', 'additional_images',
                  'created_at', 'updated_at']
