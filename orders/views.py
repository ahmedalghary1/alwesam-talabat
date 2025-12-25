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
    """عرض قائمة طلبات المستخدم"""
    orders = Order.objects.filter(user=request.user)\
        .select_related('user')\
        .prefetch_related('items__product')\
        .order_by('-created_at')
    
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """عرض تفاصيل طلب"""
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
    """إنشاء طلب جديد من السلة"""
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.error(request, 'السلة فارغة')
        return redirect('cart:cart_view')
    
    phone_number = request.POST.get('phone_number', request.user.phone)
    address = request.POST.get('address', '')
    notes = request.POST.get('notes', '')
    
    try:
        with transaction.atomic():
            # إنشاء الطلب
            order = Order.objects.create(
                user=request.user,
                phone_number=phone_number,
                address=address,
                notes=notes,
                status='pending'
            )
            
            # نقل عناصر السلة إلى الطلب
            cart_items = cart.items.all()
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,  # Already in pieces
                    unit_type=cart_item.unit_type  # NEW: preserve unit type
                )
            
            # تفريغ السلة
            cart.items.all().delete()
            
            messages.success(request, f'تم إنشاء الطلب #{order.id} بنجاح')
            return redirect('orders:order_detail', order_id=order.id)
            
    except Exception as e:
        messages.error(request, f'حدث خطأ: {str(e)}')
        return redirect('cart:checkout')


@login_required
@require_http_methods(["POST"])
def cancel_order(request, order_id):
    """إلغاء طلب"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'تم إلغاء الطلب بنجاح')
    else:
        messages.error(request, 'لا يمكن إلغاء هذا الطلب')
    
    return redirect('orders:order_detail', order_id=order.id)
