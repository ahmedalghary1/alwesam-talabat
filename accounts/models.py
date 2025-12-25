from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.image_utils import ImageCompressionMixin
from django.conf import settings


class CustomUser(AbstractUser):
    """
    Custom User model with email as the primary authentication field
    and mandatory phone and address fields
    """
    username = models.CharField(max_length=150, unique=True, verbose_name="اسم المستخدم")
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    address = models.TextField(verbose_name="العنوان")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone', 'address']
    
    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"
        
    def __str__(self):
        return self.email


User = settings.AUTH_USER_MODEL


class Profile(models.Model, ImageCompressionMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, verbose_name="نبذة شخصية")
    image = models.ImageField(upload_to='user-image/', blank=True, null=True, verbose_name="صورة الملف الشخصي")
    
    def save(self, *args, **kwargs):
        self.save_with_compression(image_field_name='image', *args, **kwargs)
    
    def __str__(self):
        return f"ملف {self.user.email}"
    

class Address(models.Model):
    """Additional addresses for the user (shipping addresses)"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, default="المنزل", verbose_name="تسمية العنوان")
    street = models.CharField(max_length=255, verbose_name="الشارع")
    city = models.CharField(max_length=100, verbose_name="المدينة")
    state = models.CharField(max_length=100, verbose_name="المحافظة")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="الرمز البريدي")
    country = models.CharField(max_length=100, default="مصر", verbose_name="الدولة")
    is_default = models.BooleanField(default=False, verbose_name="العنوان الافتراضي")

    def __str__(self):
        return f"{self.label}: {self.street}, {self.city}, {self.country}"
    
    class Meta:
        verbose_name = "عنوان"
        verbose_name_plural = "عناوين"