from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.image_utils import ImageCompressionMixin
from django.conf import settings


class CustomUser(AbstractUser):
    """
    Custom User model for wholesale e-commerce system.
    
    Uses email as the primary authentication field instead of username.
    All new users are created with is_active=False and require admin approval
    before they can log in. This allows for business verification of wholesale customers.
    """
    username = models.CharField(max_length=150, unique=True, verbose_name="اسم المستخدم")
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    # Indexed for performance when searching/filtering users by phone
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف", db_index=True)
    address = models.TextField(verbose_name="العنوان")
    
    # Email is used for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone', 'address']
    
    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمين"
        
    def __str__(self):
        return self.email


User = settings.AUTH_USER_MODEL


class Profile(ImageCompressionMixin, models.Model):
    """
    Extended user profile with bio and profile image.
    
    Automatically compresses uploaded images to optimize storage and performance.
    Profile is created via signal when a user registers.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, verbose_name="نبذة شخصية")
    image = models.ImageField(upload_to='user-image/', blank=True, null=True, verbose_name="صورة الملف الشخصي")
    
    def save(self, *args, **kwargs):
        # Compress image before saving to reduce file size
        self.save_with_compression(image_field_name='image', *args, **kwargs)
    class Meta:
        verbose_name='حساب المستخدم '
        verbose_name_plural='حسابات المستخدمين'
    def __str__(self):
        return f"ملف {self.user.email}"
    
