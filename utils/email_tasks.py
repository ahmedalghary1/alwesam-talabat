"""
Celery tasks for sending emails asynchronously.

All email sending operations should use these tasks to avoid blocking
the main request-response cycle and provide better user experience.
"""
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_activation_email_task(self, user_id, login_url):
    """
    Send account activation email to user.
    
    Args:
        user_id: ID of the user to send activation email to
        login_url: Absolute URL to the login page
        
    Returns:
        str: Success or error message
    """
    try:
        from accounts.models import CustomUser
        
        # Get user from database
        user = CustomUser.objects.get(id=user_id)
        
        subject = 'تم تفعيل حسابك - الوسام طلبات'
        
        # Context for the email template
        context = {
            'username': user.username,
            'login_url': login_url,
        }
        
        # Render HTML content
        html_content = render_to_string('emails/activation_email.html', context)
        text_content = strip_tags(html_content)  # Fallback for plain text
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@elwsam.com')
        recipient_list = [user.email]
        
        # Create and send the email
        email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f'Activation email sent successfully to {user.email}')
        return f'Activation email sent to {user.email}'
        
    except CustomUser.DoesNotExist:
        logger.error(f'User with ID {user_id} does not exist')
        return f'User with ID {user_id} not found'
        
    except Exception as e:
        logger.error(f'Error sending activation email to user {user_id}: {str(e)}')
        # Retry the task if it fails
        raise self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation_email_task(self, order_id, user_email):
    """
    Send order confirmation email to customer.
    Args:
        order_id: ID of the order
        user_email: Email address of the customer
        
    Returns:
        str: Success or error message
    """
    try:
        from orders.models import Order
        
        # Get order from database with related items
        order = Order.objects.select_related('user').prefetch_related(
            'items__product', 'items__variant'
        ).get(id=order_id)
        
        subject = f'تأكيد الطلب #{order.id} - الوسام طلبات'
        
        # Calculate order totals
        total_items = order.items.count()
        total_pieces = order.get_total_pieces()

        # Context for the email template
        context = {
            'order': order,
            'username': order.user.username,
            'order_number': order.id,
            'order_items': order.items.all(),
            'total_items': total_items,
            'total_pieces': total_pieces,
            'order_date': order.created_at,
        }
        
        # Render HTML content
        html_content = render_to_string('emails/order_confirmation.html', context)
        text_content = strip_tags(html_content)
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@elwsam.com')
        recipient_list = [user_email]
        
        # Create and send the email
        email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f'Order confirmation email sent successfully for order #{order.id} to {user_email}')
        return f'Order confirmation email sent for order #{order.id}'
        
    except Order.DoesNotExist:
        logger.error(f'Order with ID {order_id} does not exist')
        return f'Order with ID {order_id} not found'
        
    except Exception as e:
        logger.error(f'Error sending order confirmation email for order {order_id}: {str(e)}')
        # Retry the task if it fails
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_status_email_task(self, order_id, new_status, user_email):
    """
    Send order status update email to customer.
    Args:
        order_id: ID of the order
        new_status: New status of the order
        user_email: Email address of the customer
    Returns:
        str: Success or error message
    """
    try:
        from orders.models import Order
        
        # Get order from database
        order = Order.objects.select_related('user').get(id=order_id)
        
        # Status translations
        status_translations = {
            'pending': 'قيد الانتظار',
            'confirmed': 'تم التأكيد',
            'shipped': 'تم الشحن',
            'delivered': 'تم التسليم',
            'cancelled': 'تم الإلغاء',
        }
        
        status_text = status_translations.get(new_status, new_status)
        subject = f'تحديث حالة الطلب #{order.id} - الوسام طلبات'
        
        # Context for the email template
        context = {
            'order': order,
            'username': order.user.username,
            'order_number': order.id,
            'new_status': new_status,
            'status_text': status_text,
        }
        
        # Render HTML content
        html_content = render_to_string('emails/order_status_update.html', context)
        text_content = strip_tags(html_content)
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@elwsam.com')
        recipient_list = [user_email]
        
        # Create and send the email
        email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f'Order status email sent successfully for order #{order.id} to {user_email}')
        return f'Order status email sent for order #{order.id}'
        
    except Order.DoesNotExist:
        logger.error(f'Order with ID {order_id} does not exist')
        return f'Order with ID {order_id} not found'
        
    except Exception as e:
        logger.error(f'Error sending order status email for order {order_id}: {str(e)}')
        # Retry the task if it fails
        raise self.retry(exc=e)