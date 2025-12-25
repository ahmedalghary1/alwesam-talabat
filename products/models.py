from django.db import models
from django.utils.text import slugify
from utils.image_utils import ImageCompressionMixin




class Category(ImageCompressionMixin, models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=255, unique=True, blank=True, db_index=True)  # Added index for performance
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category-images')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        self.save_with_compression(image_field_name='image', *args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(ImageCompressionMixin, models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pcs_carton = models.PositiveIntegerField(default=24)
    slug = models.CharField(max_length=255, unique=True, blank=True, db_index=True)  # Added index for performance
    image = models.ImageField(upload_to='product-image')
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    is_available = models.BooleanField(default=True, verbose_name="متوفر")
    created_at = models.DateTimeField(auto_now_add=True)  # Removed unnecessary null=True, blank=True
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        self.save_with_compression(image_field_name='image', *args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', '-created_at']),  # For category product listing
            models.Index(fields=['-created_at']),  # For latest products
            models.Index(fields=['is_available']),  # For filtering available products
        ]


class ProductImages(ImageCompressionMixin, models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/additional/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.save_with_compression(image_field_name='image', *args, **kwargs)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'صورة إضافية'
        verbose_name_plural = 'صور إضافية'

    def __str__(self):
        return f"صورة لـ {self.product.name}"


class Color(models.Model):
    """ألوان المنتجات - يمكن ربطها بالأنماط"""
    name = models.CharField(max_length=50, verbose_name="اسم اللون")
    hex_code = models.CharField(
        max_length=7, 
        verbose_name="كود اللون", 
        help_text="مثال: #FF0000 للأحمر"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "لون"
        verbose_name_plural = "الألوان"
    
    def __str__(self):
        return f"{self.name} ({self.hex_code})"


class Size(models.Model):
    """أطوال/مقاسات المنتجات - يمكن ربطها بالأنماط"""
    name = models.CharField(max_length=50, verbose_name="اسم المقاس")
    order = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "مقاس"
        verbose_name_plural = "المقاسات"
    
    def __str__(self):
        return self.name


class VariantImage(ImageCompressionMixin, models.Model):
    """صور متعددة لأنماط المنتجات"""
    variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/variants/', verbose_name='الصورة')
    order = models.PositiveIntegerField(default=0, verbose_name='الترتيب')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.save_with_compression(image_field_name='image', *args, **kwargs)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'صورة نمط'
        verbose_name_plural = 'صور الأنماط'

    def __str__(self):
        return f"صورة لنمط {self.variant.name}"


class ProductVariant(ImageCompressionMixin, models.Model):
    """
    أنماط المنتج - كل variant له مواصفات مستقلة
    Product variants - each variant has independent specifications
    """
    VARIANT_TYPE_CHOICES = [
        ('color', 'اللون'),

    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    
    # Core variant identification
    variant_type = models.CharField(max_length=20, choices=VARIANT_TYPE_CHOICES)
    variant_value = models.CharField(max_length=100)  
    
    # Variant-specific attributes (NEW)
    name = models.CharField(max_length=200, help_text="اسم النمط الكامل")
    code = models.CharField(max_length=50, unique=True, blank=True, null=True,
                           help_text="كود/SKU خاص بالنمط")
    pcs_carton = models.PositiveIntegerField(default=24,
                                             help_text="عدد القطع في الكرتونة لهذا النمط")
    image = models.ImageField(upload_to='variant-images', blank=True, null=True,
                              help_text="صورة خاصة بالنمط")
    
    # Color and Size relationships (NEW)
    color = models.ForeignKey(
        Color, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='variants',
        verbose_name="اللون",
        help_text="اللون الخاص بهذا النمط (اختياري)"
    )
    sizes = models.ManyToManyField(
        Size,
        blank=True,
        related_name='variants',
        verbose_name="الأطوال المتاحة",
        help_text="الأطوال/المقاسات المتاحة لهذا النمط (اختياري)"
    )
    
    # Inventory
    is_available = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.save_with_compression(image_field_name='image', *args, **kwargs)
    
    class Meta:
        unique_together = ['product', 'variant_type', 'variant_value']
        ordering = ['variant_type', 'variant_value']
        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"
        indexes = [
            models.Index(fields=['is_available']),  # For filtering available variants
            models.Index(fields=['product', 'is_available']),  # For product variant queries
        ]
    
    def __str__(self):
        return self.name or f"{self.product.name} - {self.variant_value}"
