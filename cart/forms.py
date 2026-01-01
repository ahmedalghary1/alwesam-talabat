"""
Django Forms for Cart operations with proper validation
"""
from django import forms
from core.constants import MAX_QUANTITY_PER_ITEM, UNIT_TYPE_CHOICES


class AddToCartForm(forms.Form):
    """Form for adding items to cart with validation"""
    quantity = forms.IntegerField(
        min_value=1,
        max_value=MAX_QUANTITY_PER_ITEM,
        error_messages={
            'min_value': 'الكمية يجب أن تكون أكبر من صفر',
            'max_value': f'الكمية القصوى هي {MAX_QUANTITY_PER_ITEM}',
            'required': 'الكمية مطلوبة',
            'invalid': 'الكمية غير صحيحة',
        }
    )
    unit_type = forms.ChoiceField(
        choices=UNIT_TYPE_CHOICES,
        error_messages={
            'required': 'نوع الوحدة مطلوب',
            'invalid_choice': 'نوع الوحدة غير صحيح',
        }
    )
    variant_id = forms.IntegerField(
        required=False,
        min_value=1,
    )
    size_name = forms.CharField(
        required=False,
        max_length=100,
    )


class UpdateCartForm(forms.Form):
    """Form for updating cart item quantity"""
    quantity = forms.IntegerField(
        min_value=1,
        max_value=MAX_QUANTITY_PER_ITEM,
        error_messages={
            'min_value': 'الكمية يجب أن تكون أكبر من صفر',
            'max_value': f'الكمية القصوى هي {MAX_QUANTITY_PER_ITEM}',
            'required': 'الكمية مطلوبة',
            'invalid': 'الكمية غير صحيحة',
        }
    )
