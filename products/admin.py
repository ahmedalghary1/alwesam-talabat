from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from adminsortable2.admin import SortableAdminMixin

from .models import (
    Category, Product, ProductImages, Size,
    VariantAttribute, VariantAttributeValue,
    ProductVariant, VariantImage
)


# ========== Inlines ==========

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


class ProductVariantInline(admin.StackedInline):
    """أنماط المنتج - عرض رأسي (مكدس) مع معلومات مختصرة"""
    model = ProductVariant
    extra = 1
    fields = [
        ('name', 'code'),
        ('pcs_carton', 'is_available'),
        ('order', 'image_preview'),
    ]
    readonly_fields = ['image_preview']
    ordering = ['order']
    show_change_link = True  # رابط لتعديل النمط في صفحة منفصلة

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = "الصورة"


class VariantAttributeValueInline(admin.TabularInline):
    """قيم الخاصية (تظهر داخل صفحة الخاصية)"""
    model = VariantAttributeValue
    extra = 2
    fields = ['value', 'hex_code', 'color_preview']

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


@admin.register(ProductVariant)
class ProductVariantAdmin(SortableAdminMixin, admin.ModelAdmin):
    """أنماط المنتجات - صفحة التفاصيل الكاملة"""
    list_display = [
        'name', 'product_link', 'code', 'pcs_carton',
        'attributes_colored', 'order', 'is_available', 'color_preview', 'sizes_list'
    ]
    list_editable = ['is_available']  # order يتم عبر السحب بفضل SortableAdminMixin
    list_filter = ['is_available', 'product__category', 'attributes__attribute']
    search_fields = ['name', 'code', 'product__name']
    raw_id_fields = ['product']
    filter_horizontal = ['sizes', 'attributes']
    inlines = [VariantImageInline]
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
            'fields': ('attributes', 'sizes'),
            'classes': ('wide',),
            'description': 'اختر الخصائص (الألوان) والمقاسات المتاحة'
        }),
    )

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
        sizes = obj.sizes.all()
        if sizes:
            return ", ".join([s.name for s in sizes])
        return "-"
    sizes_list.short_description = "المقاسات"


@admin.register(Product)
class ProductAdmin(SortableAdminMixin, admin.ModelAdmin):
    """المنتجات الرئيسية"""
    list_display = [
        'name', 'category_link', 'pcs_carton',
        'order', 'is_available', 'image_preview',
        'variants_count'
    ]
    list_editable = ['is_available']  # order يتم عبر السحب
    list_filter = ['is_available', 'category', 'created_at']
    search_fields = ['name', 'description', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    raw_id_fields = ['category', 'sizes']
    inlines = [ProductImagesInline, ProductVariantInline]
    fieldsets = (
        ('معلومات المنتج', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('المواصفات', {
            'fields': ('pcs_carton', 'is_available', 'order')
        }),
        ('الصور', {
            'fields': ('image', 'image_preview'),
        }),
        ('المقاسات العامة', {
            'fields': ('sizes',),
            'description': 'هذه المقاسات تطبق على المنتج ككل إذا لم يكن له أنماط'
        }),
        ('معلومات إضافية', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    actions = ['make_available', 'make_unavailable']

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