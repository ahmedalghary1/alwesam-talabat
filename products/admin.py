from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.urls import reverse
from django.utils.http import urlencode
from .models import (
    Category, Product, ProductImages, Size, 
    VariantAttribute, VariantAttributeValue, 
    ProductVariant, VariantImage
)

from adminsortable2.admin import SortableAdminMixin 

class ProductImagesInline(admin.TabularInline):
    """Inline admin for product additional images"""
    model = ProductImages
    extra = 1
    fields = ['image', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    # ✅ إضافة order إلى الحقول القابلة للتعديل
    list_editable = ['order']
    # ✅ ترتيب الصور حسب order
    ordering = ['order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "لا توجد صورة"
    image_preview.short_description = "معاينة الصورة"


class VariantImageInline(admin.TabularInline):
    """Inline admin for variant images"""
    model = VariantImage
    extra = 1
    fields = ['image', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    # ✅ إضافة order إلى الحقول القابلة للتعديل
    list_editable = ['order']
    # ✅ ترتيب الصور حسب order
    ordering = ['order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "لا توجد صورة"
    image_preview.short_description = "الصورة"


class ProductVariantInline(admin.TabularInline):
    """Inline admin for product variants"""
    model = ProductVariant
    extra = 1
    fields = [
        'name', 'code', 'pcs_carton', 'order', 
        'is_available', 'image_preview', 'view_sizes'
    ]
    readonly_fields = ['image_preview', 'view_sizes']
    raw_id_fields = ['sizes']
    # ✅ ترتيب الأنماط حسب order
    ordering = ['order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "لا توجد صورة"
    image_preview.short_description = "الصورة"
    
    def view_sizes(self, obj):
        if obj.pk:
            sizes = obj.sizes.all()
            if sizes:
                return ", ".join([size.name for size in sizes])
            return "لا يوجد مقاسات"
        return "احفظ النمط أولاً لإضافة مقاسات"
    view_sizes.short_description = "المقاسات"


@admin.register(Category)
class CategoryAdmin(SortableAdminMixin,admin.ModelAdmin):
    """Category admin with image preview and auto slug"""
    list_display = ['name', 'order', 'products_count', 'image_preview', 'created_at']
    list_editable = ['order']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['image_preview', 'created_at']
    # ✅ ترتيب الأقسام حسب order
    ordering = ['order']
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
            return format_html('<img src="{}" width="100" style="max-height: 100px;" />', obj.image.url)
        return "لا توجد صورة"
    image_preview.short_description = "معاينة الصورة"
    
    def products_count(self, obj):
        count = obj.products.count()
        url = reverse('admin:products_product_changelist') + '?' + urlencode({'category__id__exact': obj.id})
        return format_html('<a href="{}">{} منتج</a>', url, count)
    products_count.short_description = "عدد المنتجات"
    
    def created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(obj, 'created_at') else "-"
    created_at.short_description = "تاريخ الإضافة"


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    """Size admin with ordering"""
    list_display = ['name', 'order', 'products_count', 'variants_count']
    list_editable = ['order']
    search_fields = ['name']
    # ✅ ترتيب المقاسات حسب order
    ordering = ['order']
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = "عدد المنتجات"
    
    def variants_count(self, obj):
        return obj.variants.count()
    variants_count.short_description = "عدد الأنماط"


@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    """Variant attribute admin (Color, Size, Material, etc.)"""
    list_display = ['name', 'values_count']
    search_fields = ['name']
    # ✅ ترتيب الخصائص حسب الاسم (لأنه ليس لديه order)
    ordering = ['name']
    
    def values_count(self, obj):
        return obj.values.count()
    values_count.short_description = "عدد القيم"


class VariantAttributeValueInline(admin.TabularInline):
    """Inline for attribute values"""
    model = VariantAttributeValue
    extra = 2
    fields = ['value', 'hex_code', 'color_preview']
    
    def color_preview(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="width: 30px; height: 30px; background-color: {}; border-radius: 5px;"></div>',
                obj.hex_code
            )
        return "-"
    color_preview.short_description = "معاينة اللون"


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    """Attribute values admin with hex code support"""
    list_display = ['value', 'attribute', 'color_preview', 'variants_count']
    list_filter = ['attribute']
    search_fields = ['value']
    list_editable = []
    # ✅ ترتيب القيم حسب attribute ثم value
    ordering = ['attribute__name', 'value']
    
    def color_preview(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="width: 30px; height: 30px; background-color: {}; border-radius: 5px;"></div>',
                obj.hex_code
            )
        return "-"
    color_preview.short_description = "اللون"
    
    def variants_count(self, obj):
        return obj.variants.count()
    variants_count.short_description = "عدد الأنماط"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Product variant admin"""
    list_display = [
        'name', 'product_link', 'code', 'pcs_carton', 
        'order', 'is_available', 'color_preview', 'sizes_list'
    ]
    list_editable = ['order', 'is_available']
    list_filter = ['is_available', 'product__category', 'attributes__attribute']
    search_fields = ['name', 'code', 'product__name']
    raw_id_fields = ['product', 'sizes', 'attributes']
    inlines = [VariantImageInline]
    # ✅ ترتيب الأنماط حسب order
    ordering = ['order']
    
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
    
    def color_preview(self, obj):
        color = obj.color
        if color and color.hex_code:
            return format_html(
                '<div style="width: 30px; height: 30px; background-color: {}; border-radius: 5px;" title="{}"></div>',
                color.hex_code, color.value
            )
        return "-"
    color_preview.short_description = "اللون"
    
    def sizes_list(self, obj):
        sizes = obj.sizes.all()
        if sizes:
            return ", ".join([size.name for size in sizes])
        return "-"
    sizes_list.short_description = "المقاسات"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Main product admin with all features"""
    list_display = [
        'name', 'category_link', 'pcs_carton', 
        'order', 'is_available', 'image_preview', 
        'variants_count', 'created_at'
    ]
    list_editable = ['order', 'is_available']
    list_filter = ['is_available', 'category', 'created_at']
    search_fields = ['name', 'description', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    raw_id_fields = ['category', 'sizes']
    # ✅ ترتيب المنتجات حسب order
    ordering = ['order']
    
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
            'classes': ('wide',),
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
    
    def created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at.short_description = "تاريخ الإضافة"
    
    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} منتج/منتجات تم تفعيلها')
    make_available.short_description = "تفعيل المنتجات المحددة"
    
    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} منتج/منتجات تم إلغاء تفعيلها')
    make_unavailable.short_description = "إلغاء تفعيل المنتجات المحددة"


@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    """Admin for additional product images"""
    list_display = ['product', 'image_preview', 'order', 'created_at']
    list_editable = ['order']
    list_filter = ['product__category']
    search_fields = ['product__name']
    raw_id_fields = ['product']
    # ✅ ترتيب الصور حسب order
    ordering = ['order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "لا توجد صورة"
    image_preview.short_description = "الصورة"


# تخصيص عنوان الموقع في لوحة الإدارة
admin.site.site_header = "لوحة تحكم المتجر"
admin.site.site_title = "مدير المتجر"
admin.site.index_title = "الرئيسية"