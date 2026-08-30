import re

from django.core.exceptions import ValidationError


PHONE_DIGITS = str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789')


def validate_phone_number(value):
    """Accept phone numbers, including common formatting, but never letters."""
    phone = str(value or '').strip()
    translated_phone = phone.translate(PHONE_DIGITS)

    if not re.fullmatch(r'\+?[0-9\s()-]+', translated_phone):
        raise ValidationError('رقم الهاتف يجب أن يحتوي على أرقام فقط.')

    digit_count = len(re.sub(r'\D', '', translated_phone))
    if not 10 <= digit_count <= 15:
        raise ValidationError('رقم الهاتف يجب أن يتكون من 10 إلى 15 رقمًا.')
