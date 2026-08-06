from django.contrib.auth.backends import ModelBackend
from .models import CustomUser
import logging

logger = logging.getLogger(__name__)


class EmailPhoneBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login with either:
    - Email address
    - Phone number
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user using email or phone number
        
        Args:
            username: Can be either email or phone number
            password: User's password
        
        Returns:
            CustomUser instance if authentication succeeds, None otherwise
        """
        if username is None or password is None:
            return None
        
        user = None
        
        # Try to find user by email first
        try:
            user = CustomUser.objects.get(email=username)
            logger.info(f'User found by email: {username}')
        except CustomUser.DoesNotExist:
            # Try to find user by phone number
            try:
                user = CustomUser.objects.get(phone=username)
                logger.info(f'User found by phone: {username}')
            except CustomUser.DoesNotExist:
                logger.warning(f'No user found with email or phone: {username}')
                return None
            except CustomUser.MultipleObjectsReturned:
                # A database upgraded from an older release may still contain
                # duplicate phone numbers until migration 0005 is applied.
                logger.error('Duplicate phone number prevents authentication: %s', username)
                return None
        
        # Verify password
        if user and user.check_password(password):
            logger.info(f'Password verified for user: {user.email}')
            return user
        
        logger.warning(f'Password verification failed for: {username}')
        return None
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
