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
        verbose_name_plural = "المستخدمون"
        
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
    
    def __str__(self):
        return f"ملف {self.user.email}"
    

class Address(models.Model):
    """
    Additional shipping addresses for users.
    
    Users can have multiple addresses (home, office, warehouse, etc.)
    with one marked as default for checkout convenience.
    """
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