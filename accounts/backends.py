from django.contrib.auth.backends import ModelBackend
from django.db.models import F, Q, Value
from django.db.models.functions import Replace
from .models import CustomUser
import logging
import re

logger = logging.getLogger(__name__)


ARABIC_DIGITS = str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789')
PHONE_SEPARATORS = (' ', '-', '(', ')', '+', '.', '/')


def normalize_phone_identifier(value):
    """Normalize a phone entered at login without changing stored user data."""
    translated = str(value or '').strip().translate(ARABIC_DIGITS)
    if not translated or not re.fullmatch(r'[\d\s()+\-./]+', translated):
        return None

    digits = re.sub(r'\D', '', translated)
    if not 10 <= len(digits) <= 15:
        return None

    # Accept the common Egyptian forms: 010..., 10..., +2010..., 002010...
    if digits.startswith('0020') and len(digits) == 14:
        digits = f'0{digits[4:]}'
    elif digits.startswith('20') and len(digits) == 12:
        digits = f'0{digits[2:]}'
    elif digits.startswith('1') and len(digits) == 10:
        digits = f'0{digits}'
    return digits


def _phone_lookup_values(normalized_phone):
    values = {normalized_phone}
    if len(normalized_phone) == 11 and normalized_phone.startswith('01'):
        national_number = normalized_phone[1:]
        values.update({
            national_number,
            f'20{national_number}',
            f'0020{national_number}',
        })
    return values


def _find_user_by_phone(identifier):
    """Find one phone owner, including legacy formatted values, without writes."""
    normalized_phone = normalize_phone_identifier(identifier)
    if normalized_phone is None:
        return None

    normalized_field = F('phone')
    for separator in PHONE_SEPARATORS:
        normalized_field = Replace(normalized_field, Value(separator), Value(''))
    for source, target in zip('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789'):
        normalized_field = Replace(normalized_field, Value(source), Value(target))

    matches = list(
        CustomUser.objects.annotate(_phone_digits=normalized_field)
        .filter(
            Q(phone__iexact=str(identifier).strip())
            | Q(_phone_digits__in=_phone_lookup_values(normalized_phone))
        )
        .order_by('pk')[:2]
    )
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        logger.error('Ambiguous normalized phone prevented authentication')
    return None


class EmailUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login with:
    - Email address
    - Phone number
    - Username
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user using email, phone number, or username
        
        Args:
            username: Can be an email address, phone number, or username
            password: User's password
        
        Returns:
            CustomUser instance if authentication succeeds, None otherwise
        """
        if username is None or password is None:
            return None

        username = username.strip()
        
        user = None
        
        # Preserve email/username behavior, and add a read-only phone lookup.
        try:
            user = CustomUser.objects.get(email__iexact=username)
            logger.info('User found by email')
        except CustomUser.DoesNotExist:
            user = _find_user_by_phone(username)
            if user is not None:
                logger.info('User found by phone')
            else:
                try:
                    user = CustomUser.objects.get(username__iexact=username)
                    logger.info('User found by username')
                except CustomUser.DoesNotExist:
                    # Run one password hash to reduce account-enumeration timing leaks.
                    CustomUser().set_password(password)
                    logger.warning('No user found for supplied login identifier')
                    return None
                except CustomUser.MultipleObjectsReturned:
                    logger.error('Duplicate username prevents authentication')
                    return None
        except CustomUser.MultipleObjectsReturned:
            logger.error('Duplicate email prevents authentication')
            return None
        
        # Verify password
        if user and user.check_password(password):
            logger.info('Password verified for user: %s', user.email or user.username)
            return user
        
        logger.warning('Password verification failed for supplied login identifier')
        return None
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None


# Keep existing authenticated sessions valid after renaming the backend.
EmailPhoneBackend = EmailUsernameBackend
