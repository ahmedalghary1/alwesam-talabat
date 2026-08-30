from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Max, Count, Q, Prefetch
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from .models import CustomerMessage, MessageReply

@staff_member_required
def messages_list(request):
    """
    show list of all conversations grouped by user
    """
    # Get last message for each user with unread count
    users_with_messages = CustomerMessage.objects.values('user').annotate(
        last_message_date=Max('created_at'),
        total_messages=Count('id'),
        unread_count=Count('id', filter=Q(is_read=False))
    ).order_by('-last_message_date')
    
    # Get user info and last message for each
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
def start_conversation(request):
    """Allow a staff member to start a new support conversation with a customer."""
    user_model = get_user_model()
    customers = user_model.objects.filter(is_staff=False).order_by('username', 'id')

    selected_customer_id = request.POST.get('customer', '').strip()
    message_text = request.POST.get('message', '').strip()

    if request.method == 'POST':
        customer = (
            customers.filter(pk=selected_customer_id).first()
            if selected_customer_id.isdigit()
            else None
        )
        if customer is None:
            messages.error(request, 'يرجى اختيار عميل صحيح.')
        elif not message_text:
            messages.error(request, 'الرسالة فارغة.')
        else:
            initial_message = CustomerMessage.objects.create(
                user=customer,
                message=message_text,
                sent_by_admin=True,
                admin_user=request.user,
                is_read=True,
            )
            messages.success(request, f'تم بدء المحادثة مع {customer.username} بنجاح.')
            return redirect(
                'admin_support:conversation_detail',
                message_id=initial_message.id,
            )

    return render(request, 'admin/support/start_conversation.html', {
        'customers': customers,
        'selected_customer_id': selected_customer_id,
        'message_text': message_text,
    })


@staff_member_required
def conversation_detail(request, message_id):
    """
    show all messages of a user (full conversation)
    """
    # Get first message to retrieve user information
    first_message = get_object_or_404(CustomerMessage, id=message_id)
    user = first_message.user
    
    # Get all messages of this user with replies
    all_user_messages = CustomerMessage.objects.filter(
        user=user
    ).select_related('user', 'admin_user').prefetch_related(
        Prefetch('replies', queryset=MessageReply.objects.select_related('admin_user'))
    ).order_by('created_at')
    
    # mark all messages as read
    CustomerMessage.objects.filter(user=user, is_read=False).update(is_read=True)
    
    context = {
        'client': user,
        'user_messages': all_user_messages, 
        'total_messages': all_user_messages.count(),
    }
    
    return render(request, 'admin/support/conversation_detail.html', context)


@staff_member_required
@require_POST
def send_reply(request, message_id):
    """
    send reply to a customer message.
    
    Marks message as read after sending reply.
    """
    message = get_object_or_404(CustomerMessage, id=message_id)
    reply_text = request.POST.get('reply', '').strip()
        
    if reply_text:
        reply = MessageReply.objects.create(
            customer_message=message,
            admin_user=request.user,
            reply=reply_text
        )
            
        # Mark message as read
        if not message.is_read:
            message.is_read = True
            message.save(update_fields=['is_read'])
            
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
@require_POST
def mark_as_read(request, message_id):
    """
    Mark message as read.
    
    AJAX endpoint to update message read status.
    """
    message = get_object_or_404(CustomerMessage, id=message_id)
    if not message.is_read:
        message.is_read = True
        message.save(update_fields=['is_read'])
    return JsonResponse({
        'success': True,
        'message': 'تم تحديد الرسالة كمقروءة'
    })


@staff_member_required
@require_POST
def delete_message(request, message_id):
    """
    Delete all messages of a user (full conversation)
    """
    message = get_object_or_404(CustomerMessage, id=message_id)
    user = message.user
    deleted_count = CustomerMessage.objects.filter(user=user).delete()[0]
    messages.success(request, f'تم حذف {deleted_count} رسالة من المحادثة بنجاح')
    return redirect('admin_support:messages_list')
