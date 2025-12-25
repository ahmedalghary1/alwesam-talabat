"""
Custom validators for the products app
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_positive_integer(value):
    """
    Validate that a value is a positive integer
    
    Args:
        value: The value to validate
        
    Raises:
        ValidationError: If value is not positive
    """
    if value <= 0:
        raise ValidationError(
            _('%(value)s يجب أن تكون قيمة موجبة'),
            params={'value': value},
        )


def validate_carton_quantity(value):
    """
    Validate carton quantity (between 1 and 1000)
    
    Args:
        value: The quantity to validate
        
    Raises:
        ValidationError: If quantity is invalid
    """
    if value < 1:
        raise ValidationError('عدد القطع في الكرتونة يجب أن يكون على الأقل 1')
    if value > 1000:
        raise ValidationError('عدد القطع في الكرتونة لا يمكن أن يتجاوز 1000')
