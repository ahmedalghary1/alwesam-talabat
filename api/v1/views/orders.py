"""
Views for orders API - Order management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from orders.models import Order, OrderItem
from cart.models import Cart
from ..serializers.orders import (
    OrderListSerializer, OrderDetailSerializer, CreateOrderSerializer
)
from ..permissions import IsOwnerOrAdmin

import logging
logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for orders.
    List, retrieve, create, and cancel orders.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)\
            .select_related('user')\
            .prefetch_related('items__product')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderDetailSerializer
    
    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        """Create order from cart items."""
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                # Serialize checkout for each cart so two concurrent API calls
                # cannot create two orders from the same items.
                cart = Cart.objects.select_for_update().get(user=request.user)
                cart_items = list(
                    cart.items.select_related('product', 'variant', 'size')
                )
                if not cart_items:
                    return Response(
                        {"error": "السلة فارغة"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                order = Order.objects.create(
                    user=request.user,
                    phone_number=serializer.validated_data['phone_number'],
                    address=serializer.validated_data['address'],
                    notes=serializer.validated_data.get('notes', ''),
                    status='pending'
                )

                for cart_item in cart_items:
                    color_name = ''
                    size_name = cart_item.size_name

                    if cart_item.variant and cart_item.variant.color:
                        color_name = cart_item.variant.color.value

                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        variant=cart_item.variant,
                        quantity=cart_item.quantity,
                        unit_type=cart_item.unit_type,
                        color_name=color_name,
                        size_name=size_name,
                        length_label=cart_item.length_label or 'المقاس',
                        is_length_only=cart_item.is_length_only,
                        pcs_carton=cart_item.get_pcs_carton(),
                    )

                cart.items.all().delete()

                try:
                    from utils.email_tasks import send_order_confirmation_email_task
                    transaction.on_commit(
                        lambda: send_order_confirmation_email_task.delay(
                            order.id,
                            request.user.email,
                        ),
                        robust=True,
                    )
                except Exception:
                    pass  # Don't fail order creation if email setup fails
        except Cart.DoesNotExist:
            return Response(
                {"error": "السلة غير موجودة"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            OrderDetailSerializer(order).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel pending order."""
        order = self.get_object()
        
        if order.status != 'pending':
            return Response(
                {"error": "لا يمكن إلغاء هذا الطلب"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        
        return Response(OrderDetailSerializer(order).data)
