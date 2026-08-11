from django import forms
from django.contrib import admin
from django.db.models import Max
from django.utils.html import format_html, format_html_join
from django.urls import reverse
from django.utils.http import urlencode
from adminsortable2.admin import SortableAdminMixin

from .models import (
    Category, Product, ProductImages, Size,
    VariantAttribute, VariantAttributeValue,
    ProductVariant, VariantImage, VariantSize,
    ProductSize, ProductSizeImage, VariantSizeImage,
)


# ========== Inlines ==========


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        clean_one = super().clean
        if isinstance(data, (list, tuple)):
            return [clean_one(file, initial) for file in data]
        return [clean_one(data, initial)] if data else []


class ProductSizeAdminForm(forms.ModelForm):
    size_images = MultipleFileField(
        required=False,
        label='إضافة صور خاصة بهذا المقاس',
        help_text='يمكن اختيار أكثر من صورة.',
    )

    class Meta:
        model = ProductSize
        fields = '__all__'


class VariantSizeAdminForm(forms.ModelForm):
    size_images = MultipleFileField(
        required=False,
        label='إضافة صور خاصة بهذا المقاس',
        help_text='يمكن اختيار أكثر من صورة.',
    )

    class Meta:
        model = VariantSize
        fields = '__all__'


def _size_images_preview(obj):
    if not obj or not obj.pk:
        return 'احفظ المقاس أولاً لإضافة الصور.'
    images = list(obj.images.all())
    if not images:
        return 'لا توجد صور خاصة بهذا المقاس.'
    return format_html_join(
        '',
        '<img src="{}" alt="" style="width:64px;height:64px;object-fit:contain;margin:3px;border:1px solid #ddd;border-radius:4px;background:#fff" />',
        ((image.image.url,) for image in images if image.image),
    )


def _save_size_inline_images(formset):
    image_model = None
    relation_field = None
    if formset.model is ProductSize:
        image_model = ProductSizeImage
        relation_field = 'product_size'
    elif formset.model is VariantSize:
        image_model = VariantSizeImage
        relation_field = 'variant_size'
    if image_model is None:
        return

    for form in formset.forms:
        if not getattr(form, 'cleaned_data', None) or form.cleaned_data.get('DELETE'):
            continue
        instance = form.instance
        uploaded_images = form.cleaned_data.get('size_images') or []
        if not instance.pk or not uploaded_images:
            continue
        max_order = instance.images.aggregate(Max('order'))['order__max']
        next_order = 0 if max_order is None else max_order + 1
        for index, image in enumerate(uploaded_images):
            image_model.objects.create(
                **{relation_field: instance},
                image=image,
                order=next_order + index,
            )

class ProductImagesInline(admin.TabularInline):
    """صور إضافية للمنتج"""
    model = ProductImages
    extra = 1
    fields = ['image', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    ordering = ['order']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "لا توجد صورة"
    image_preview.short_description = "معاينة"


class VariantImageInline(admin.TabularInline):
    """صور إضافية للنمط"""
    model = VariantImage
    extra = 1
    fields = ['image', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    ordering = ['order']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "لا توجد صورة"
    image_preview.short_description = "معاينة"


class VariantSizeInline(admin.TabularInline):
    """إدارة مقاسات النمط مع الكمية"""
    model = VariantSize
    form = VariantSizeAdminForm
    extra = 1
    fields = ['size', 'pcs_carton', 'current_images', 'size_images']
    readonly_fields = ['current_images']
    autocomplete_fields = ['size']
    show_change_link = True

    def current_images(self, obj):
        return _size_images_preview(obj)
    current_images.short_description = 'الصور الحالية للمقاس'


class ProductSizeInline(admin.TabularInline):
    """إدارة مقاسات المنتج المباشر مع الكمية"""
    model = ProductSize
    form = ProductSizeAdminForm
    extra = 1
    fields = ['size', 'pcs_carton', 'current_images', 'size_images']
    readonly_fields = ['current_images']
    autocomplete_fields = ['size']
    show_change_link = True
    verbose_name = "مقاس مباشر مع الكمية"
    verbose_name_plural = "المقاسات المباشرة والكميات"

    def current_images(self, obj):
        return _size_images_preview(obj)
    current_images.short_description = 'الصور الحالية للمقاس'


class ProductSizeImageInline(admin.TabularInline):
    model = ProductSizeImage
    extra = 1
    fields = ['image', 'order', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" width="72" height="72" style="object-fit:contain" />', obj.image.url)
        return '-'
    image_preview.short_description = 'معاينة'


class VariantSizeImageInline(admin.TabularInline):
    model = VariantSizeImage
    extra = 1
    fields = ['image', 'order', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" width="72" height="72" style="object-fit:contain" />', obj.image.url)
        return '-'
    image_preview.short_description = 'معاينة'


class ProductVariantInline(admin.StackedInline):
    """أنماط المنتج - عرض مع معلومات مختصرة وإمكانية التعديل عبر الرابط"""
    model = ProductVariant
    extra = 1
    fields = [
        ('name', 'code'),
        ('pcs_carton', 'is_available'),
        ('order', 'image'),
        'attributes',
        'sizes_display',
    ]
    filter_horizontal = ['attributes']
    readonly_fields = ['sizes_display']
    ordering = ['order']
    show_change_link = True

    def sizes_display(self, obj):
        """عرض المقاسات مع الكمية الخاصة بكل منها (للقراءة فقط)"""
        if not obj.pk:
            return "احفظ النمط أولاً لإضافة المقاسات"
        size_prices = list(obj.size_prices.select_related('size').all())
        if not size_prices:
            return '-'
        return format_html_join(
            '<br>',
            '<a href="{}">{}: {} قطعة - إدارة صور المقاس</a>',
            (
                (
                    reverse('admin:products_variantsize_change', args=[size_price.pk]),
                    size_price.size.name,
                    size_price.pcs_carton,
                )
                for size_price in size_prices
            ),
        )
    sizes_display.short_description = "المقاسات والكميات وصورها"


class VariantAttributeValueInline(admin.TabularInline):
    """قيم الخاصية (تظهر داخل صفحة الخاصية)"""
    model = VariantAttributeValue
    extra = 2
    fields = ['value', 'hex_code', 'color_preview']
    readonly_fields = ['color_preview']

    def color_preview(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="width: 30px; height: 30px; background: {}; border-radius: 5px;"></div>',
                obj.hex_code
            )
        return "-"
    color_preview.short_description = "اللون"


# ========== Model Admins ==========

@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    """الأقسام"""
    list_display = ['name', 'order', 'products_count', 'image_preview']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['image_preview']
    fieldsets = (
        ('معلومات القسم', {
            'fields': ('name', 'slug', 'description', 'order')
        }),
        ('الصورة', {
            'fields': ('image', 'image_preview')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" style="max-height:100px;" />', obj.image.url)
        return "لا توجد صورة"
    image_preview.short_description = "معاينة"

    def products_count(self, obj):
        count = obj.products.count()
        url = reverse('admin:products_product_changelist') + '?' + urlencode({'category__id__exact': obj.id})
        return format_html('<a href="{}">{} منتج</a>', url, count)
    products_count.short_description = "عدد المنتجات"


@admin.register(Size)
class SizeAdmin(SortableAdminMixin, admin.ModelAdmin):
    """المقاسات"""
    list_display = ['name', 'order', 'products_count', 'variants_count']
    search_fields = ['name']

    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = "عدد المنتجات"

    def variants_count(self, obj):
        return obj.variants.count()
    variants_count.short_description = "عدد الأنماط"


@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    """أنواع الخصائص (لون، مقاس، خامة، ...)"""
    list_display = ['name', 'values_count']
    search_fields = ['name']
    inlines = [VariantAttributeValueInline]

    def values_count(self, obj):
        return obj.values.count()
    values_count.short_description = "عدد القيم"


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    """قيم الخصائص"""
    list_display = ['value', 'attribute', 'color_preview', 'variants_count']
    list_filter = ['attribute']
    search_fields = ['value']
    ordering = ['attribute__name', 'value']

    def color_preview(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="width: 30px; height: 30px; background: {}; border-radius: 5px;"></div>',
                obj.hex_code
            )
        return "-"
    color_preview.short_description = "اللون"

    def variants_count(self, obj):
        return obj.variants.count()
    variants_count.short_description = "عدد الأنماط"


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'pcs_carton', 'images_count']
    list_filter = ['size', 'product__category']
    search_fields = ['product__name', 'size__name']
    autocomplete_fields = ['product', 'size']
    inlines = [ProductSizeImageInline]

    def images_count(self, obj):
        return obj.images.count()
    images_count.short_description = 'عدد الصور'


@admin.register(VariantSize)
class VariantSizeAdmin(admin.ModelAdmin):
    list_display = ['variant', 'size', 'pcs_carton', 'images_count']
    list_filter = ['size', 'variant__product__category']
    search_fields = ['variant__name', 'variant__product__name', 'size__name']
    autocomplete_fields = ['variant', 'size']
    inlines = [VariantSizeImageInline]

    def images_count(self, obj):
        return obj.images.count()
    images_count.short_description = 'عدد الصور'


@admin.register(ProductVariant)
class ProductVariantAdmin(SortableAdminMixin, admin.ModelAdmin):
    """أنماط المنتجات - صفحة التفاصيل الكاملة"""
    list_display = [
        'name', 'product_link', 'code', 'pcs_carton',
        'attributes_colored', 'order', 'is_available', 'color_preview', 'sizes_list'
    ]
    list_editable = ['is_available']
    list_filter = ['is_available', 'product__category', 'attributes__attribute']
    search_fields = ['name', 'code', 'product__name']
    raw_id_fields = ['product']
    filter_horizontal = ['attributes']
    inlines = [VariantImageInline, VariantSizeInline]
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('product', 'name', 'code', 'order')
        }),
        ('المواصفات', {
            'fields': ('pcs_carton', 'is_available', 'length_label')
        }),
        ('الصورة', {
            'fields': ('image',)
        }),
        ('الخصائص', {
            'fields': ('attributes',),
            'classes': ('wide',),
            'description': 'اختر الخصائص (مثل الألوان)'
        }),
        # ملاحظة: المقاسات تدار عبر VariantSizeInline
    )

    class Media:
        css = {'all': ('admin/css/product_admin_fix.css',)}

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        _save_size_inline_images(formset)

    def product_link(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = "المنتج"

    def attributes_colored(self, obj):
        parts = []
        for a in obj.attributes.all():
            if a.hex_code:
                parts.append(format_html(
                    '<span style="display:inline-block; margin:2px; padding:2px 5px; background:{}; color:#fff; border-radius:3px;">{}: {}</span>',
                    a.hex_code, a.attribute.name, a.value
                ))
            else:
                parts.append(f"{a.attribute.name}: {a.value}")
        return format_html(' '.join(parts)) if parts else "-"
    attributes_colored.short_description = "الخصائص"

    def color_preview(self, obj):
        color = obj.color
        if color and color.hex_code:
            return format_html(
                '<div style="width:30px; height:30px; background:{}; border-radius:5px;" title="{}"></div>',
                color.hex_code, color.value
            )
        return "-"
    color_preview.short_description = "اللون"

    def sizes_list(self, obj):
        size_info = [f"{vs.size.name} ({vs.pcs_carton})" for vs in obj.size_prices.all()]
        return ", ".join(size_info) if size_info else "-"
    sizes_list.short_description = "المقاسات (الكمية)"


@admin.register(Product)
class ProductAdmin(SortableAdminMixin, admin.ModelAdmin):
    """المنتجات الرئيسية"""
    list_display = [
        'name', 'category_link', 'pcs_carton',
        'order', 'is_available', 'image_preview',
        'variants_count'
    ]
    list_editable = ['is_available']
    list_filter = ['is_available', 'category', 'created_at']
    search_fields = ['name', 'description', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    raw_id_fields = ['category']  # تم إزالة 'sizes' من هنا
    inlines = [ProductImagesInline, ProductSizeInline, ProductVariantInline]  # أضفنا ProductSizeInline
    fieldsets = (
        ('معلومات المنتج', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('المواصفات', {
            'fields': ('pcs_carton', 'length_label', 'is_available', 'order')
        }),
        ('الصور', {
            'fields': ('image', 'image_preview'),
        }),
        # تم إزالة قسم "المقاسات العامة" لأنها تدار عبر ProductSizeInline
        ('معلومات إضافية', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    actions = ['make_available', 'make_unavailable']

    class Media:
        css = {'all': ('admin/css/product_admin_fix.css',)}

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        _save_size_inline_images(formset)

    def category_link(self, obj):
        if obj.category:
            url = reverse('admin:products_category_change', args=[obj.category.id])
            return format_html('<a href="{}">{}</a>', url, obj.category.name)
        return "-"
    category_link.short_description = "القسم"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "لا توجد صورة"
    image_preview.short_description = "الصورة"

    def variants_count(self, obj):
        count = obj.variants.count()
        url = reverse('admin:products_productvariant_changelist') + '?' + urlencode({'product__id__exact': obj.id})
        return format_html('<a href="{}">{} نمط</a>', url, count)
    variants_count.short_description = "عدد الأنماط"

    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} منتج/منتجات تم تفعيلها')
    make_available.short_description = "تفعيل المنتجات المحددة"

    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} منتج/منتجات تم إلغاء تفعيلها')
    make_unavailable.short_description = "إلغاء تفعيل المنتجات المحددة"


@admin.register(ProductImages)
class ProductImagesAdmin(SortableAdminMixin, admin.ModelAdmin):
    """الصور الإضافية للمنتجات"""
    list_display = ['product', 'image_preview', 'order', 'created_at']
    list_filter = ['product__category']
    search_fields = ['product__name']
    raw_id_fields = ['product']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "لا توجد صورة"
    image_preview.short_description = "الصورة"


# تخصيص عنوان الموقع في لوحة الإدارة
admin.site.site_header = "لوحة تحكم المتجر"
admin.site.site_title = "مدير المتجر"
admin.site.index_title = "الرئيسية"
