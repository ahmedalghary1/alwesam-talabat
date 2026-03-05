from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Prefetch
from .models import (
    Category, Product, ProductImages, Color, Size,
    VariantAttribute, VariantAttributeValue, ProductVariant, VariantImage
)
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin


# -------------------- SIZE ADMIN --------------------
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    search_fields = ('name',)


# -------------------- VARIANT ATTRIBUTE ADMIN --------------------
@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    search_fields = ('name',)


# -------------------- CATEGORY ADMIN --------------------
@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'order', 'image_tag')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit:cover;border-radius:4px;"/>',
                obj.image.url
            )
        return "-"
    image_tag.short_description = "الصورة"


# -------------------- INLINE IMAGE Mixin --------------------
class InlineImageMixin:
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if getattr(obj, 'image', None):
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit:cover;border-radius:4px;"/>',
                obj.image.url
            )
        return "-"
    image_tag.short_description = "الصورة"


# -------------------- PRODUCT IMAGES INLINE --------------------
class ProductImagesInline(InlineImageMixin, SortableInlineAdminMixin, admin.StackedInline):
    model = ProductImages
    extra = 0
    fields = ("image_tag", "image", "order")
    classes = ("grp-collapse grp-closed",)  # Collapsible with default closed
    verbose_name_plural = "صور إضافية للمنتج"


# -------------------- VARIANT IMAGE INLINE --------------------
class VariantImageInline(InlineImageMixin, SortableInlineAdminMixin, admin.StackedInline):
    model = VariantImage
    extra = 0
    fields = ("image_tag", "image", "order")
    classes = ("grp-collapse grp-closed",)
    verbose_name_plural = "صور النمط"


# -------------------- PRODUCT VARIANT INLINE --------------------
class ProductVariantInline(InlineImageMixin, SortableInlineAdminMixin, admin.StackedInline):
    model = ProductVariant
    extra = 0
    autocomplete_fields = ("attributes", "sizes")
    show_change_link = True
    fields = (
        "name", "code", "pcs_carton", "image_tag", "image",
        "is_available", "attributes_display", "sizes_display", "order"
    )
    readonly_fields = ("image_tag", "attributes_display", "sizes_display")
    classes = ("grp-collapse grp-closed",)
    verbose_name_plural = "أنماط المنتج"

    def attributes_display(self, obj):
        return ", ".join([str(a) for a in obj.attributes.all()])
    attributes_display.short_description = "خصائص النمط"

    def sizes_display(self, obj):
        return ", ".join([s.name for s in obj.sizes.all()])
    sizes_display.short_description = "المقاسات"


# -------------------- PRODUCT ADMIN --------------------
@admin.register(Product)
class ProductAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'category', 'is_available', 'order', 'created_at')
    search_fields = ('name', 'category__name')
    list_filter = ('is_available', 'category')
    inlines = [ProductImagesInline, ProductVariantInline]
    autocomplete_fields = ('sizes',)
    prepopulated_fields = {"slug": ("name",)}

    # تحسين الأداء عند جلب بيانات كبيرة جدًا
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category').prefetch_related(
            'sizes',
            Prefetch('additional_images', queryset=ProductImages.objects.order_by('order')),
            Prefetch('variants', queryset=ProductVariant.objects.prefetch_related('attributes', 'sizes', 'images'))
        )


# -------------------- VARIANT ATTRIBUTE VALUE ADMIN --------------------
@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('value', 'attribute', 'hex_code')
    search_fields = ('value', 'attribute__name')
    autocomplete_fields = ('attribute',)


# -------------------- PRODUCT VARIANT ADMIN --------------------
@admin.register(ProductVariant)
class ProductVariantAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "product", "name", "code", "pcs_carton",
        "is_available", "color_display", "sizes_display", "attributes_display"
    )
    search_fields = ("product__name", "name", "code")
    list_filter = ("is_available", "product")
    autocomplete_fields = ("attributes", "sizes")
    inlines = [VariantImageInline]

    # تحسين الأداء
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product').prefetch_related('attributes', 'sizes', 'images')

    def color_display(self, obj):
        color = obj.color
        if color and color.hex_code:
            return format_html(
                '<span style="background:{};color:#fff;padding:2px 6px;border-radius:3px;font-size:12px;">{}</span>',
                color.hex_code, color.value
            )
        return color.value if color else "-"
    color_display.short_description = "اللون"

    def sizes_display(self, obj):
        return ", ".join([s.name for s in obj.sizes.all()])
    sizes_display.short_description = "المقاسات"

    def attributes_display(self, obj):
        return ", ".join([str(a) for a in obj.attributes.all()])
    attributes_display.short_description = "خصائص النمط"