from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from .models import CustomerMessage, MessageReply
import json
import logging
logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def send_message(request):
    """
    Send new message from customer.
    
    Creates a customer message in the support system.
    """
    try:
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return JsonResponse({
                'success': False,
                'error': 'الرسالة فارغة'
            }, status=400)
        
        # Create message
        message = CustomerMessage.objects.create(
            user=request.user,
            message=message_text
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'text': message.message,
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
                'user': request.user.username
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@never_cache
@require_http_methods(["GET"])
def get_user_messages(request):
    """
    Get all user messages with replies.
    
    Returns a list of all messages from the authenticated user
    including admin replies.
    """
    try:
        messages = CustomerMessage.objects.filter(
            user=request.user
        ).prefetch_related(
            Prefetch(
                'replies',
                queryset=MessageReply.objects.select_related('admin_user').order_by('created_at', 'id')
            )
        ).order_by('created_at', 'id')
        
        messages_data = []
        for msg in messages:
            msg_dict = {
                'id': msg.id,
                'text': msg.message,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
                'is_read': msg.is_read,
                'replies': []
            }
            
            # Add replies
            for reply in msg.replies.all():
                msg_dict['replies'].append({
                    'id': reply.id,
                    'text': reply.reply,
                    'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M'),
                    'admin': reply.admin_user.username if reply.admin_user else 'خدمة العملاء'
                })
            
            messages_data.append(msg_dict)
        
        return JsonResponse({
            'success': True,
            'messages': messages_data
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_conversation(request, message_id):
    """
    Get specific conversation by message ID.
    
    Returns message with all its replies.
    """
    try:
        message = CustomerMessage.objects.prefetch_related('replies').get(
            id=message_id,
            user=request.user
        )
        
        conversation = {
            'id': message.id,
            'text': message.message,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_read': message.is_read,
            'replies': []
        }
        
        for reply in message.replies.all():
            conversation['replies'].append({
                'id': reply.id,
                'text': reply.reply,
                'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M'),
                'admin': reply.admin_user.username if reply.admin_user else 'خدمة العملاء'
            })
        
        return JsonResponse({
            'success': True,
            'conversation': conversation
        })
    
    except CustomerMessage.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'الرسالة غير موجودة'
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
