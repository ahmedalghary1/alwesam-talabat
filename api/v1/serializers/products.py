"""
Serializers for products app - Categories, Products, and Variants.
"""
from rest_framework import serializers
from products.models import (
    Category, Product, ProductVariant, Size,
    ProductImages, VariantImage, VariantSize,
    VariantAttributeValue, VariantAttribute
)


class ColorSerializer(serializers.ModelSerializer):
    """
    Serializer for product colors.
    Uses VariantAttributeValue filtered for color attributes.
    """
    class Meta:
        model = VariantAttributeValue
        fields = ['id', 'value', 'hex_code']
    
    def to_representation(self, instance):
        """Custom representation to use 'name' field instead of 'value' for API consistency"""
        data = super().to_representation(instance)
        data['name'] = data.pop('value')  # Rename value to name for API consistency
        return data


class SizeSerializer(serializers.ModelSerializer):
    """Serializer for product sizes."""
    
    class Meta:
        model = Size
        fields = ['id', 'name', 'order']


class SizeImageSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    image = serializers.ImageField(read_only=True)
    order = serializers.IntegerField(read_only=True)


class SizeCartonQuantitySerializer(serializers.ModelSerializer):
    """A selectable size together with its authoritative carton quantity."""
    id = serializers.IntegerField(source='size_id', read_only=True)
    name = serializers.CharField(source='size.name', read_only=True)
    order = serializers.IntegerField(source='size.order', read_only=True)
    images = SizeImageSerializer(many=True, read_only=True)

    class Meta:
        model = VariantSize
        fields = ['id', 'name', 'order', 'pcs_carton', 'images']


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


class VariantAttributeValueSerializer(serializers.ModelSerializer):
    """Serializer for variant attribute values."""
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)
    
    class Meta:
        model = VariantAttributeValue
        fields = ['id', 'attribute_name', 'value', 'hex_code']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for product variants."""
    # ✅ استخدام VariantAttributeValue بدلاً من Color
    colors = serializers.SerializerMethodField()
    sizes = SizeSerializer(many=True, read_only=True)
    size_options = SizeCartonQuantitySerializer(source='size_prices', many=True, read_only=True)
    images = VariantImageSerializer(many=True, read_only=True)
    attributes = VariantAttributeValueSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'name', 'colors', 'sizes', 'size_options', 'code', 'pcs_carton',
            'is_available', 'images', 'attributes', 'order'
        ]
    
    def get_colors(self, obj):
        """Get color attributes for this variant."""
        color_attributes = obj.attributes.filter(
            attribute__name__in=["لون", "Color"]
        )
        return ColorSerializer(color_attributes, many=True).data


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories."""
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'order', 'products_count']
    
    def get_products_count(self, obj):
        return obj.products.filter(is_available=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for product list."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category_name', 'category_slug',
            'image', 'pcs_carton', 'is_available', 'order'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product."""
    category = CategorySerializer(read_only=True)
    variants = serializers.SerializerMethodField()
    additional_images = ProductImageSerializer(many=True, read_only=True)
    size_options = SizeCartonQuantitySerializer(source='size_prices', many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category',
            'image', 'pcs_carton', 'is_available', 'order',
            'variants', 'size_options', 'additional_images',
            'created_at', 'updated_at'
        ]
    
    def get_variants(self, obj):
        """Get variants with proper ordering and filtering."""
        variants = obj.variants.filter(is_available=True).order_by('order').prefetch_related(
            'sizes', 'size_prices__size', 'size_prices__images',
            'attributes__attribute', 'images'
        )
        return ProductVariantSerializer(variants, many=True).data


# ✅ إضافة Serializers إضافية مفيدة
class ColorListSerializer(serializers.Serializer):
    """
    Serializer for listing all available colors with their variants.
    مفيد لعرض جميع الألوان المتاحة في المتجر.
    """
    id = serializers.IntegerField()
    name = serializers.CharField()
    hex_code = serializers.CharField()
    products_count = serializers.IntegerField()
    variants_count = serializers.IntegerField()


class ProductVariantMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal variant serializer for quick references.
    """
    color_name = serializers.SerializerMethodField()
    color_hex = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'code', 'color_name', 'color_hex', 'is_available']
    
    def get_color_name(self, obj):
        color = obj.attributes.filter(attribute__name__in=["لون", "Color"]).first()
        return color.value if color else None
    
    def get_color_hex(self, obj):
        color = obj.attributes.filter(attribute__name__in=["لون", "Color"]).first()
        return color.hex_code if color else None
