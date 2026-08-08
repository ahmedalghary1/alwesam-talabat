from django.contrib.auth.backends import ModelBackend
from .models import CustomUser
import logging

logger = logging.getLogger(__name__)


class EmailUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login with either:
    - Email address
    - Username
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user using email or username
        
        Args:
            username: Can be either email address or username
            password: User's password
        
        Returns:
            CustomUser instance if authentication succeeds, None otherwise
        """
        if username is None or password is None:
            return None

        username = username.strip()
        
        user = None
        
        # Try to find user by email first
        try:
            user = CustomUser.objects.get(email__iexact=username)
            logger.info(f'User found by email: {username}')
        except CustomUser.DoesNotExist:
            # Try to find user by username
            try:
                user = CustomUser.objects.get(username__iexact=username)
                logger.info(f'User found by username: {username}')
            except CustomUser.DoesNotExist:
                logger.warning(f'No user found with email or username: {username}')
                return None
            except CustomUser.MultipleObjectsReturned:
                logger.error('Duplicate username prevents authentication: %s', username)
                return None
        except CustomUser.MultipleObjectsReturned:
            logger.error('Duplicate email prevents authentication: %s', username)
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


# Keep existing authenticated sessions valid after renaming the backend.
EmailPhoneBackend = EmailUsernameBackend
