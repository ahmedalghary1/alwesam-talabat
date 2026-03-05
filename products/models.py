from django.db import models
from django.utils.text import slugify
from utils.image_utils import ImageCompressionMixin


class Category(ImageCompressionMixin, models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, blank=True, db_index=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category-images')
    order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields and 'order' in update_fields:
            super().save(*args, **kwargs)
        else:
            if not self.slug:
                self.slug = slugify(self.name, allow_unicode=True)
            super().save(*args, **kwargs)
            self.save_with_compression(image_field_name='image')
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = "القسم"
        verbose_name_plural = "الأقسام"

class Product(ImageCompressionMixin, models.Model):
    """
    Main product model for wholesale items.
    Products are sold by carton with configurable pieces per carton.
    Can have multiple variants (colors, sizes) and additional images.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Default pieces per carton (can be overridden by variants)
    pcs_carton = models.PositiveIntegerField(default=24)
    # Indexed for URL routing and faster queries
    slug = models.CharField(max_length=255, unique=True, blank=True, db_index=True)
    image = models.ImageField(upload_to='product-image')
    order = models.PositiveIntegerField(default=0)
    # 👇 أضف هذا الجزء هنا
    sizes = models.ManyToManyField(
        "Size",
        blank=True,

        related_name='products',
        verbose_name="الأطوال المتاحة للمنتج",
        help_text="أضف أطوال مباشرة إذا لم يكن للمنتج أنماط"
    )

    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    is_available = models.BooleanField(default=True, verbose_name="متوفر")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields and 'order' in update_fields:
            super().save(*args, **kwargs)
        else:
            if not self.slug:
                self.slug = slugify(self.name, allow_unicode=True)
            super().save(*args, **kwargs)
            self.save_with_compression(image_field_name='image')

    class Meta:
        ordering = ['order']
        # Strategic indexes for common query patterns
        verbose_name = "المنتج"
        verbose_name_plural = "المنتجات"
        indexes = [
            models.Index(fields=['category', '-created_at']),  # Category listing
            models.Index(fields=['-created_at']),  # Latest products
            models.Index(fields=['is_available']),  # Availability filtering
        ]

class ProductImages(ImageCompressionMixin, models.Model):
    """
    Additional product images for gallery/slideshow.
    
    Images are ordered by the 'order' field for display control.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/additional/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields and 'order' in update_fields:
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
            self.save_with_compression(image_field_name='image')

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'صورة إضافية'
        verbose_name_plural = 'صور إضافية'

    def __str__(self):
        return f"صورة لـ {self.product.name}"


class Size(models.Model):
    """
    Product sizes/lengths for product variants.
    Examples: S, M, L, XL or wire gauges, fabric lengths, etc.
    Ordered by 'order' field for consistent display.
    """
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
    """
    Multiple images for product variants.
    Allows variants to have their own image gallery.
    """
    variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/variants/', verbose_name='الصورة')
    order = models.PositiveIntegerField(default=0, verbose_name='الترتيب')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields and 'order' in update_fields:
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
            self.save_with_compression(image_field_name='image')
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'صورة نمط'
        verbose_name_plural = 'صور الأنماط'

        def __str__(self):
            return f"صورة لنمط {self.variant.name}"

class VariantAttribute(models.Model):
    """
    نوع المتغير: لون - مقاس - خامة - موديل ...
    """
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "نوع خاصية"
        verbose_name_plural = "أنواع الخصائص"

    def __str__(self):
        return self.name


class VariantAttributeValue(models.Model):
    attribute = models.ForeignKey(
        VariantAttribute,
        related_name="values",
        on_delete=models.CASCADE
    )
    value = models.CharField(max_length=100)

    hex_code = models.CharField(
        max_length=7,
        blank=True,
        null=True,
        help_text="يستخدم فقط لو كانت الخاصية لون"
    )

    class Meta:
        unique_together = ("attribute", "value")


class ProductVariant(ImageCompressionMixin, models.Model):
    """
    Product variants with independent specifications.
    Each variant can have its own color, sizes, SKU code, and piece count.
    This allows selling the same product in different configurations.
    Example: Same shirt in different colors or different wire gauges.
    """

    attributes = models.ManyToManyField(
        VariantAttributeValue,
        blank=True,
        related_name="variants",
        verbose_name="خصائص النمط"
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    order = models.PositiveIntegerField(default=0)
    # Variant classification
    # Variant-specific attributes
    name = models.CharField(max_length=200, help_text="اسم النمط الكامل")
    length_label = models.CharField(max_length=50, blank=True, null=True, verbose_name="نوع الطول", help_text="مثال: مقاس السلك، طول الصابع")
    # Unique SKU/product code for inventory tracking
    code = models.CharField(max_length=50, unique=True, blank=True, null=True,help_text="كود/SKU خاص بالنمط")
    # Variant can override product's default pcs_carton
    pcs_carton = models.PositiveIntegerField(default=24,help_text="عدد القطع في الكرتونة لهذا النمط")
    image = models.ImageField(upload_to='variant-images', blank=True, null=True,help_text="صورة خاصة بالنمط")
    

    sizes = models.ManyToManyField(
        Size,
        blank=True,
        related_name='variants',
        verbose_name="الأطوال المتاحة",
        help_text="الأطوال/المقاسات المتاحة لهذا النمط (اختياري)"
    )
    
    # Availability flag
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def color(self):
        return self.attributes.filter(attribute__name="لون").first()

    def __str__(self):
        return self.name or f"{self.product.name}"
        
    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields and 'order' in update_fields:
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
            self.save_with_compression(image_field_name='image')

    class Meta:
        # Ensure each product has unique variant codes

        unique_together = ['product', 'code']
        ordering = ['order']
        verbose_name = "نمط المنتج"
        verbose_name_plural = "أنماط المنتجات"
        # Optimize common queries
        indexes = [
            models.Index(fields=['is_available']),
            models.Index(fields=['product', 'is_available']),
        ]

