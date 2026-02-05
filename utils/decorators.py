"""
Utility decorators for the Alwesam-Talabat project
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


def handle_exceptions(redirect_url='home:home', error_message='حدث خطأ غير متوقع'):
    """
    Decorator to handle exceptions in views
    Args:
        redirect_url: URL name to redirect to on error
        error_message: Default error message to display
    Usage:
        @handle_exceptions(redirect_url='products:all_categories')
        def my_view(request):
           # view code 
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                return view_func(request, *args, **kwargs)
            except Exception as e:
                logger.error(
                    f'Error in {view_func.__name__}: {str(e)}', 
                    exc_info=True,
                    extra={'request': request}
                )
                messages.error(request, f'{error_message}: {str(e)}')
                return redirect(redirect_url)
        return wrapper
    return decorator
