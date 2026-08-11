"""
Serializers for cart app - Shopping cart and cart items.
"""
from rest_framework import serializers
from cart.models import Cart, CartItem
from products.models import Product
from core.constants import MAX_QUANTITY_PER_ITEM


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    variant_info = serializers.SerializerMethodField()
    quantity_in_cartons = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_image',
                  'variant', 'variant_info', 'quantity',
                  'unit_type', 'size', 'size_name', 'length_label',
                  'quantity_in_cartons']
        read_only_fields = ['id', 'size']
    
    def get_variant_info(self, obj):
        if obj.variant:
            return {
                'color': obj.variant.color.value if obj.variant.color else None,
                'sku_code': obj.variant.code
            }
        return None
    
    def get_quantity_in_cartons(self, obj):
        return obj.get_quantity_in_cartons()


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart."""
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=MAX_QUANTITY_PER_ITEM,
    )
    unit_type = serializers.ChoiceField(choices=['piece', 'carton'])
    size_name = serializers.CharField(required=False, allow_blank=True)
    size_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    
    def validate_product_id(self, value):
        if not Product.objects.filter(id=value, is_available=True).exists():
            raise serializers.ValidationError("المنتج غير متاح")
        return value
    
    def validate_variant_id(self, value):
        # Product ownership and size compatibility are validated together in
        # the view, where the selected product is available.
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    """Validate a cart item update in the unit selected by the customer."""

    item_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=MAX_QUANTITY_PER_ITEM,
    )


class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart."""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        return obj.get_item_count()
