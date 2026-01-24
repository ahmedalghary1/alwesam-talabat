"""
Serializers for orders app - Customer orders and order items.
"""
from rest_framework import serializers
from orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    display_name = serializers.SerializerMethodField()
    quantity_in_cartons = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'display_name',
                  'quantity', 'unit_type', 'color_name', 'size_name',
                  'quantity_in_cartons']
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    
    def get_quantity_in_cartons(self, obj):
        return obj.get_quantity_in_cartons()


class OrderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for order list."""
    items_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'status', 'status_display', 'items_count',
                  'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single order."""
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_pieces = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'status_display',
                  'phone_number', 'address', 'notes',
                  'items', 'total_pieces',
                  'created_at', 'updated_at']
        read_only_fields = ['user']
    
    def get_total_pieces(self, obj):
        return obj.get_total_pieces()


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating new order."""
    phone_number = serializers.CharField(max_length=20)
    address = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)
