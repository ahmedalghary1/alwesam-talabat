from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q, Prefetch
from .models import CustomerMessage, MessageReply
import json


@staff_member_required
def messages_list(request):
    """عرض قائمة جميع المحادثات مجمعة حسب المستخدم"""
    from django.db.models import Max, Count, Q
    
    # جلب آخر رسالة لكل مستخدم مع عدد الرسائل غير المقروءة
    users_with_messages = CustomerMessage.objects.values('user').annotate(
        last_message_date=Max('created_at'),
        total_messages=Count('id'),
        unread_count=Count('id', filter=Q(is_read=False))
    ).order_by('-last_message_date')
    
    # جلب معلومات المستخدمين وآخر رسالة لكل منهم
    conversations = []
    for user_data in users_with_messages:
        user_id = user_data['user']
        last_message = CustomerMessage.objects.filter(user_id=user_id).order_by('-created_at').first()
        
        conversations.append({
            'user': last_message.user,
            'last_message': last_message,
            'total_messages': user_data['total_messages'],
            'unread_count': user_data['unread_count'],
            'last_message_date': user_data['last_message_date'],
            'has_unread': user_data['unread_count'] > 0
        })
    
    context = {
        'conversations': conversations,
        'unread_count': sum(conv['unread_count'] for conv in conversations),
    }
    
    return render(request, 'admin/support/messages_list.html', context)


@staff_member_required
def conversation_detail(request, message_id):
    """عرض جميع رسائل المستخدم (المحادثة الكاملة)"""
    # جلب الرسالة الأولى للحصول على معلومات المستخدم
    first_message = get_object_or_404(CustomerMessage, id=message_id)
    user = first_message.user
    
    # جلب جميع رسائل هذا المستخدم مع الردود
    all_user_messages = CustomerMessage.objects.filter(
        user=user
    ).select_related('user').prefetch_related(
        Prefetch('replies', queryset=MessageReply.objects.select_related('admin_user'))
    ).order_by('created_at')
    
    # تحديد جميع الرسائل غير المقروءة كمقروءة
    CustomerMessage.objects.filter(user=user, is_read=False).update(is_read=True)
    
    context = {
        'user': user,
        'user_messages': all_user_messages,  # تم تغيير الاسم من messages إلى user_messages
        'total_messages': all_user_messages.count(),
    }
    
    return render(request, 'admin/support/conversation_detail.html', context)


@staff_member_required
def send_reply(request, message_id):
    """إرسال رد على رسالة"""
    if request.method == 'POST':
        message = get_object_or_404(CustomerMessage, id=message_id)
        reply_text = request.POST.get('reply', '').strip()
        
        if reply_text:
            reply = MessageReply.objects.create(
                customer_message=message,
                admin_user=request.user,
                reply=reply_text
            )
            
            # تحديد الرسالة كمقروءة
            if not message.is_read:
                message.is_read = True
                message.save()
            
            # إذا كان AJAX request، أرجع JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'reply': {
                        'id': reply.id,
                        'text': reply.reply,
                        'admin_name': reply.admin_user.username if reply.admin_user else 'خدمة العملاء',
                        'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M')
                    }
                })
            
            messages.success(request, 'تم إرسال الرد بنجاح')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'الرد فارغ'
                }, status=400)
            messages.error(request, 'الرد فارغ')
    
    return redirect('admin_support:conversation_detail', message_id=message_id)


@staff_member_required
def mark_as_read(request, message_id):
    """تحديد رسالة كمقروءة"""
    if request.method == 'POST':
        message = get_object_or_404(CustomerMessage, id=message_id)
        message.is_read = True
        message.save()
        
        return JsonResponse({
            'success': True,
            'message': 'تم تحديد الرسالة كمقروءة'
        })
    
    return JsonResponse({
        'success': False,
        'error': 'طريقة غير صحيحة'
    }, status=400)


@staff_member_required
def delete_message(request, message_id):
    """حذف جميع رسائل المستخدم (المحادثة الكاملة)"""
    if request.method == 'POST':
        message = get_object_or_404(CustomerMessage, id=message_id)
        user = message.user
        
        # حذف جميع رسائل هذا المستخدم (سيتم حذف الردود تلقائياً بسبب CASCADE)
        deleted_count = CustomerMessage.objects.filter(user=user).delete()[0]
        
        messages.success(request, f'تم حذف {deleted_count} رسالة من المحادثة بنجاح')
        return redirect('admin_support:messages_list')
    
    return redirect('admin_support:messages_list')
