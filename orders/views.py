from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.contrib import messages
from django.db.models import Sum, Count
from .models import Order, OrderItem
from cart.models import Cart
import logging

logger = logging.getLogger(__name__)


@login_required
def order_list(request):
    """
    عرض قائمة طلبات المستخدم مع تحسين الأداء.
    """
    orders = Order.objects.filter(user=request.user)\
        .select_related('user')\
        .prefetch_related('items__product')\
        .order_by('-created_at')
    
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """
    عرض تفاصيل الطلب مع حساب العدد الإجمالي للكراتين والقطع.
    يستخدم القيم المخزنة وقت الطلب لضمان الدقة.
    """
    order = Order.objects.filter(id=order_id, user=request.user)\
        .select_related('user')\
        .prefetch_related('items__product__category')\
        .first()
    
    if not order:
        messages.error(request, 'الطلب غير موجود')
        return redirect('orders:order_list')
    
    # إحصائيات سريعة باستخدام التجميع
    totals = order.items.aggregate(
        total_items=Count('id'),
        total_pieces=Sum('quantity')
    )
    total_items = totals['total_items']
    total_pieces = totals['total_pieces'] or 0
    
    # حساب عدد الكراتين بناءً على العناصر التي تم طلبها ككراتين
    # نستخدم حقل pcs_carton المخزن في كل عنصر (تم إضافته حديثاً)
    total_cartons = 0
    for item in order.items.all():
        if item.unit_type == 'carton':
            total_cartons += item.get_quantity_in_cartons()
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'total_items': total_items,
        'total_cartons': int(total_cartons),
        'total_pieces': total_pieces,
    })


@login_required
@require_http_methods(["POST"])
def create_order(request):
    """
    إنشاء طلب جديد من السلة مع حفظ جميع التفاصيل (المقاس، اللون، عدد القطع الفعلي في الكرتونة).
    يتم قفل السلة لمنع التكرار، ويتم مسحها بعد النجاح.
    """
    try:
        with transaction.atomic():
            # قفل السلة لمنع أي عملية متزامنة
            cart = Cart.objects.select_for_update().get(user=request.user)

            if not cart.items.exists():
                messages.error(request, 'السلة فارغة')
                return redirect('cart:cart_view')

            # جمع بيانات العنوان والملاحظات
            phone_number = request.POST.get('phone_number') or getattr(request.user, 'phone', '')
            address = request.POST.get('address', '')
            notes = request.POST.get('notes', '')

            # إنشاء الطلب الرئيسي
            order = Order.objects.create(
                user=request.user,
                phone_number=phone_number,
                address=address,
                notes=notes,
                status='pending'
            )

            # جلب عناصر السلة مع المنتج والـ variant فقط (لا يوجد علاقة مباشرة للون)
            cart_items = cart.items.select_related('product', 'variant', 'size')

            for cart_item in cart_items:
                # ---- 1. استخراج اسم اللون بشكل صحيح ----
                color_name = ''
                if cart_item.variant:
                    color_obj = cart_item.variant.color  # property ترجع VariantAttributeValue أو None
                    if color_obj:
                        color_name = color_obj.value   # الحقل الصحيح هو value وليس name

                # Use the exact direct-size or variant-size carton quantity.
                pcs_carton_value = cart_item.get_pcs_carton()
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,           # الكمية مخزنة بالقطع دائماً
                    unit_type=cart_item.unit_type,
                    color_name=color_name,
                    size_name=cart_item.size_name or '',
                    pcs_carton=pcs_carton_value,           # ⬅️ حقل جديد يجب إضافته في نموذج OrderItem
                )

            # مسح السلة بعد نجاح العملية
            cart.items.all().delete()

            # إرسال إيميل التأكيد بشكل غير متزامن (اختياري)
            try:
                from utils.email_tasks import send_order_confirmation_email_task
                send_order_confirmation_email_task.delay(order.id, request.user.email)
            except Exception as e:
                logger.error(f'فشل في إرسال إيميل التأكيد للطلب {order.id}: {str(e)}')

            messages.success(request, f'✅ تم إنشاء الطلب #{order.id} بنجاح')
            return redirect('orders:order_detail', order_id=order.id)

    except Cart.DoesNotExist:
        messages.error(request, '❌ لا توجد سلة')
        return redirect('cart:cart_view')
    except Exception as e:
        messages.error(request, '❌ حدث خطأ أثناء إنشاء الطلب')
        
        logger.exception(e)
        return redirect('cart:checkout')


@login_required
@require_http_methods(["POST"])
def cancel_order(request, order_id):
    """
    إلغاء الطلب إذا كان لا يزال قيد الانتظار.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, '✅ تم إلغاء الطلب بنجاح')
    else:
        messages.error(request, '❌ لا يمكن إلغاء هذا الطلب')
    
    return redirect('orders:order_detail', order_id=order.id)
