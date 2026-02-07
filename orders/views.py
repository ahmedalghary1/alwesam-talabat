from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.contrib import messages
from .models import Order, OrderItem
from cart.models import Cart
import logging

logger = logging.getLogger(__name__)


@login_required
def order_list(request):
    """
    Display list of user's orders.
    
    Shows all orders with optimized database queries.
    """
    orders = Order.objects.filter(user=request.user)\
        .select_related('user')\
        .prefetch_related('items__product')\
        .order_by('-created_at')
    
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """
    Display detailed order information.
    
    Shows order items, quantities, and calculated totals.
    Uses database aggregation for performance.
    """
    order = Order.objects.filter(id=order_id, user=request.user)\
        .select_related('user')\
        .prefetch_related('items__product__category')\
        .first()
    
    if not order:
        messages.error(request, 'الطلب غير موجود')
        return redirect('orders:order_list')
    
    # Calculate totals using aggregation (performance optimization)
    from django.db.models import Sum, F, Count
    
    totals = order.items.aggregate(
        total_items=Count('id'),
        total_pieces=Sum('quantity')
    )
    
    total_items = totals['total_items']
    total_pieces = totals['total_pieces'] or 0
    
    # Calculate cartons based on unit_type
    total_cartons = 0
    for item in order.items.select_related('product'):
        if item.unit_type == 'carton':
            total_cartons += item.get_quantity_in_cartons()
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'total_items': total_items,
        'total_cartons': total_cartons,
        'total_pieces': total_pieces,
    })




@login_required
@require_http_methods(["POST"])
def create_order(request):
    """
    Create new order from shopping cart.

    Converts cart items to order items with transaction safety.
    Preserves variant, color, and size information for historical accuracy.
    Clears cart after successful order creation.
    """

    try:
        with transaction.atomic():

            # 🔐 LOCK the cart to prevent double submission
            cart = Cart.objects.select_for_update().get(user=request.user)

            # Re-check cart after lock
            if not cart.items.exists():
                messages.error(request, 'السلة فارغة')
                return redirect('cart:cart_view')

            phone_number = request.POST.get('phone_number') or getattr(request.user, 'phone', '')
            address = request.POST.get('address', '')
            notes = request.POST.get('notes', '')

            # Create order
            order = Order.objects.create(
                user=request.user,
                phone_number=phone_number,
                address=address,
                notes=notes,
                status='pending'
            )

            # Fetch cart items efficiently
            cart_items = cart.items.select_related(
                'product',
                'variant',
                'variant__color'
            )

            for cart_item in cart_items:
                # Preserve size & color exactly as chosen
                size_name = cart_item.size_name or ''
                color_name = (
                    cart_item.variant.color.name
                    if cart_item.variant and cart_item.variant.color
                    else ''
                )

                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                    unit_type=cart_item.unit_type,
                    color_name=color_name,
                    size_name=size_name
                )

            # Clear cart AFTER successful order creation
            cart.items.all().delete()

            # Send confirmation email asynchronously (non-blocking)
            try:
                from utils.email_tasks import send_order_confirmation_email_task
                send_order_confirmation_email_task.delay(order.id, request.user.email)
            except Exception as e:
                logger.error(
                    f'Failed to queue order confirmation email for order {order.id}: {str(e)}'
                )

            messages.success(request, f'تم إنشاء الطلب #{order.id} بنجاح')
            return redirect('orders:order_detail', order_id=order.id)

    except Cart.DoesNotExist:
        messages.error(request, 'لا توجد سلة')
        return redirect('cart:cart_view')

    except Exception as e:
        messages.error(request, 'حدث خطأ أثناء إنشاء الطلب')
        logger.exception(e)
        return redirect('cart:checkout')


@login_required
@require_http_methods(["POST"])
def cancel_order(request, order_id):
    """
    Cancel pending order.

    Only allows cancellation of orders with 'pending' status.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'تم إلغاء الطلب بنجاح')
    else:
        messages.error(request, 'لا يمكن إلغاء هذا الطلب')
    
    return redirect('orders:order_detail', order_id=order.id)
