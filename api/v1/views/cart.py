"""
Views for cart API - Shopping cart management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from cart.models import Cart, CartItem
from cart.services import InvalidProductSelection, resolve_product_selection
from products.models import Product
from ..serializers.cart import CartSerializer, AddToCartSerializer, CartItemSerializer
import logging
logger = logging.getLogger(__name__)


class CartViewSet(viewsets.ViewSet):
    """
    ViewSet for shopping cart operations.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get current user's cart."""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart."""
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        product_id = serializer.validated_data['product_id']
        variant_id = serializer.validated_data.get('variant_id')
        quantity = serializer.validated_data['quantity']
        unit_type = serializer.validated_data['unit_type']
        size_name = serializer.validated_data.get('size_name', '')
        size_id = serializer.validated_data.get('size_id')
        
        product = Product.objects.get(id=product_id)
        try:
            selection = resolve_product_selection(
                product,
                variant_id=variant_id,
                size_id=size_id,
                size_name=size_name,
            )
        except InvalidProductSelection as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        variant = selection.variant
        size_name = selection.size.name if selection.size else ''
        
        # Convert to pieces if unit is carton
        if unit_type == 'carton':
            quantity = quantity * selection.pcs_carton
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            unit_type=unit_type,
            size_name=size_name,
            defaults={'quantity': quantity, 'size': selection.size}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.size = selection.size
            cart_item.save()
        
        return Response(
            CartItemSerializer(cart_item).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """Remove item from cart."""
        item_id = request.data.get('item_id')
        try:
            cart = Cart.objects.get(user=request.user)
            item = CartItem.objects.get(id=item_id, cart=cart)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response(
                {"error": "العنصر غير موجود"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Update item quantity."""
        item_id = request.data.get('item_id')
        new_quantity = request.data.get('quantity')
        
        try:
            cart = Cart.objects.get(user=request.user)
            item = CartItem.objects.get(id=item_id, cart=cart)
            item.quantity = new_quantity
            item.save()
            return Response(CartItemSerializer(item).data)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response(
                {"error": "العنصر غير موجود"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from cart."""
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response(
                {"error": "السلة غير موجودة"},
                status=status.HTTP_404_NOT_FOUND
            )
