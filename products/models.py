from django.db import models
from django.utils.text import slugify
from utils.image_utils import ImageCompressionMixin


def _unique_slug(instance, value):
    """Build a stable unique slug, including for repeated Arabic product names."""
    field = instance._meta.get_field('slug')
    base = slugify(value, allow_unicode=True) or 'item'
    base = base[:field.max_length]
    candidate = base
    suffix = 2
    queryset = type(instance)._base_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)
    while queryset.filter(slug=candidate).exists():
        marker = f'-{suffix}'
        candidate = f'{base[:field.max_length - len(marker)]}{marker}'
        suffix += 1
    return candidate


class Category(ImageCompressionMixin, models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, blank=True, db_index=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category-images')
    order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields and 'image' not in update_fields:
            super().save(*args, **kwargs)
        else:
            if not self.slug:
                self.slug = _unique_slug(self, self.name)
            self.save_with_compression(image_field_name='image', *args, **kwargs)

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
    # Default pieces per carton (can be overridden by variants or direct sizes)
    pcs_carton = models.PositiveIntegerField(default=24)
    length_label = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name="اسم خيار الطول/المقاس",
        help_text="مثال: الطول، مقاس السلك، طول الإصبع. يترك فارغاً لاستخدام كلمة المقاس.",
    )
    # Indexed for URL routing and faster queries
    slug = models.CharField(max_length=255, unique=True, blank=True, db_index=True)
    image = models.ImageField(upload_to='product-image')
    order = models.PositiveIntegerField(default=0)

    # Direct sizes with per-size pcs_carton (through model)
    sizes = models.ManyToManyField(
        "Size",
        through='ProductSize',
        through_fields=('product', 'size'),
        blank=True,
        related_name='products',
        verbose_name="الأطوال المتاحة للمنتج",
        help_text="أضف أطوال مباشرة إذا لم يكن للمنتج أنماط. يمكن تحديد الكمية لكل مقاس عبر الواجهة المخصصة."
    )

    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    is_available = models.BooleanField(default=True, verbose_name="متوفر")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields and 'image' not in update_fields:
            super().save(*args, **kwargs)
        else:
            if not self.slug:
                self.slug = _unique_slug(self, self.name)
            self.save_with_compression(image_field_name='image', *args, **kwargs)

    class Meta:
        ordering = ['order']
        verbose_name = "المنتج"
        verbose_name_plural = "المنتجات"
        indexes = [
            models.Index(fields=['category', '-created_at']),  # Category listing
            models.Index(fields=['-created_at']),  # Latest products
            models.Index(fields=['is_available']),  # Availability filtering
        ]

    def __str__(self):
        return self.name

    def get_length_label(self):
        """Return the customer-facing name for direct size/length options."""
        return self.length_label.strip() or 'المقاس'

    def get_card_sale_info(self):
        """Return concise, safe sale information for product listing cards."""
        cached = getattr(self, '_card_sale_info_cache', None)
        if cached is not None:
            return cached

        length_names = []
        label = self.get_length_label()

        for option in self.size_prices.all():
            if option.pcs_carton is None and option.size.name not in length_names:
                length_names.append(option.size.name)

        if not length_names:
            for variant in self.variants.all():
                if not variant.is_available:
                    continue
                variant_names = [
                    option.size.name
                    for option in variant.size_prices.all()
                    if option.pcs_carton is None
                ]
                if variant_names:
                    label = variant.get_length_label()
                    for name in variant_names:
                        if name not in length_names:
                            length_names.append(name)

        if length_names:
            visible_names = length_names[:3]
            values = '، '.join(visible_names)
            if len(length_names) > len(visible_names):
                values += f' +{len(length_names) - len(visible_names)}'
            info = {
                'is_length_only': True,
                'label': label,
                'values': values,
            }
        else:
            info = {
                'is_length_only': False,
                'pcs_carton': self.pcs_carton,
            }

        self._card_sale_info_cache = info
        return info


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
        if update_fields and 'image' not in update_fields:
            super().save(*args, **kwargs)
        else:
            self.save_with_compression(image_field_name='image', *args, **kwargs)

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


class VariantSize(models.Model):
    """
    Intermediate model for Variant - Size relationship with per-size pcs_carton.
    """
    variant = models.ForeignKey(
        'ProductVariant',
        on_delete=models.CASCADE,
        related_name='size_prices'
    )
    size = models.ForeignKey(
        Size,
        on_delete=models.CASCADE,
        related_name='variant_prices'
    )
    pcs_carton = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=None,
        verbose_name="عدد القطع في الكرتونة",
        help_text="اختياري. اتركه فارغاً إذا كان الخيار يباع بالطول مباشرة.",
    )

    class Meta:
        unique_together = ('variant', 'size')
        verbose_name = "مقاس النمط"
        verbose_name_plural = "مقاسات النمط"

    def __str__(self):
        quantity = f'{self.pcs_carton} قطعة/كرتونة' if self.pcs_carton else 'بيع بالطول'
        return f"{self.variant} - {self.size.name}: {quantity}"

    @property
    def sale_text(self):
        """Customer-facing sale text that never exposes a null carton value."""
        if self.pcs_carton is None:
            return 'يباع بالطول مباشرة'
        return f'{self.pcs_carton} قطعة/كرتون'


class ProductSize(models.Model):
    """
    Intermediate model for Product (direct) - Size relationship with per-size pcs_carton.
    Used when product has no variants.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='size_prices'
    )
    size = models.ForeignKey(
        Size,
        on_delete=models.CASCADE,
        related_name='product_prices'
    )
    pcs_carton = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=None,
        verbose_name="عدد القطع في الكرتونة",
        help_text="اختياري. اتركه فارغاً إذا كان الخيار يباع بالطول مباشرة.",
    )

    class Meta:
        unique_together = ('product', 'size')
        verbose_name = "مقاس المنتج المباشر"
        verbose_name_plural = "مقاسات المنتج المباشرة"

    def __str__(self):
        quantity = f'{self.pcs_carton} قطعة/كرتونة' if self.pcs_carton else 'بيع بالطول'
        return f"{self.product.name} - {self.size.name}: {quantity}"

    @property
    def sale_text(self):
        """Customer-facing sale text that never exposes a null carton value."""
        if self.pcs_carton is None:
            return 'يباع بالطول مباشرة'
        return f'{self.pcs_carton} قطعة/كرتون'


class VariantSizeImage(ImageCompressionMixin, models.Model):
    """Gallery image that belongs to one specific variant/size combination."""
    variant_size = models.ForeignKey(
        VariantSize,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='products/variant-sizes/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields and 'image' not in update_fields:
            super().save(*args, **kwargs)
        else:
            self.save_with_compression(image_field_name='image', *args, **kwargs)

    class Meta:
        ordering = ['order', 'created_at']


class ProductSizeImage(ImageCompressionMixin, models.Model):
    """Gallery image that belongs to one direct product/size combination."""
    product_size = models.ForeignKey(
        ProductSize,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='products/product-sizes/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields and 'image' not in update_fields:
            super().save(*args, **kwargs)
        else:
            self.save_with_compression(image_field_name='image', *args, **kwargs)

    class Meta:
        ordering = ['order', 'created_at']


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
        if update_fields and 'image' not in update_fields:
            super().save(*args, **kwargs)
        else:
            self.save_with_compression(image_field_name='image', *args, **kwargs)

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

    def __str__(self):
        if self.hex_code:
            return f"{self.attribute.name}: {self.value} ({self.hex_code})"
        return f"{self.attribute.name}: {self.value}"


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
    # Variant-specific attributes
    name = models.CharField(max_length=200, help_text="اسم النمط الكامل")
    length_label = models.CharField(max_length=50, blank=True, null=True, verbose_name="نوع الطول", help_text="مثال: مقاس السلك، طول الصابع")
    # Unique SKU/product code for inventory tracking
    code = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="كود/SKU الخاص بالنمط")
    # Variant can override product's default pcs_carton
    pcs_carton = models.PositiveIntegerField(default=24, help_text="عدد القطع في الكرتونة لهذا النمط")
    image = models.ImageField(upload_to='variant-images', blank=True, null=True, help_text="صورة خاصة بالنمط")

    sizes = models.ManyToManyField(
        Size,
        through='VariantSize',
        through_fields=('variant', 'size'),
        blank=True,
        related_name='variants',
        verbose_name="المقاسات المتاحة",
        help_text="اختر المقاسات وحدد الكمية لكل مقاس عبر الواجهة المخصصة"
    )
    # Availability flag
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def color(self):
        return self.attributes.filter(attribute__name__iexact="لون").first()

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields and 'image' not in update_fields:
            super().save(*args, **kwargs)
        else:
            self.save_with_compression(image_field_name='image', *args, **kwargs)

    class Meta:
        ordering = ['order']
        verbose_name = "نمط المنتج"
        verbose_name_plural = "أنماط المنتجات"
        indexes = [
            models.Index(fields=['is_available']),
            models.Index(fields=['product', 'is_available']),
        ]

    def __str__(self):
        return self.name or f"{self.product.name}"

    def get_length_label(self):
        """Return the variant label, falling back to its product label."""
        return (self.length_label or '').strip() or self.product.get_length_label()
