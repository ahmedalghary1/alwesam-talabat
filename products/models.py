# admin.py
from django.contrib import admin
from django.utils.html import format_html
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.contrib.auth.models import User
from .models import (
    Category, Product, ProductImages, Color, Size,
    VariantAttribute, VariantAttributeValue, ProductVariant, VariantImage
)

# ---------------- تسجيل User (حل مشاكل Jazzmin أو أي ثيم) ----------------
admin.site.register(User)

# ---------------- Category Admin ----------------
@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'order', 'image_tag')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;"/>', obj.image.url)
        return "-"
    image_tag.short_description = "الصورة"

# ---------------- Product Images Inline ----------------
class ProductImagesInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProductImages
    extra = 1
    readonly_fields = ("image_tag",)
    fields = ("image_tag", "image", "order")
    classes = ("collapse",)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;"/>', obj.image.url)
        return "-"
    image_tag.short_description = "الصورة"

# ---------------- Variant Image Inline ----------------
class VariantImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = VariantImage
    extra = 1
    readonly_fields = ("image_tag",)
    fields = ("image_tag", "image", "order")
    classes = ("collapse",)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;"/>', obj.image.url)
        return "-"
    image_tag.short_description = "الصورة"

# ---------------- ProductVariant Inline ----------------
class ProductVariantInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProductVariant
    extra = 1
    autocomplete_fields = ("attributes", "sizes")
    show_change_link = True
    fields = (
        "name",
        "code",
        "pcs_carton",
        "image_tag",
        "image",
        "is_available",
        "attributes_display",
        "sizes_display",
        "order",
    )
    readonly_fields = ("image_tag", "attributes_display", "sizes_display")
    classes = ("collapse",)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;"/>', obj.image.url)
        return "-"
    image_tag.short_description = "الصورة"

    def attributes_display(self, obj):
        return ", ".join([str(a) for a in obj.attributes.all()])
    attributes_display.short_description = "خصائص النمط"

    def sizes_display(self, obj):
        return ", ".join([s.name for s in obj.sizes.all()])
    sizes_display.short_description = "المقاسات"

# ---------------- Product Admin ----------------
@admin.register(Product)
class ProductAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'category', 'is_available', 'order', 'created_at')
    search_fields = ('name', 'category__name')
    list_filter = ('is_available', 'category')
    inlines = [ProductImagesInline, ProductVariantInline]
    autocomplete_fields = ('sizes',)
    prepopulated_fields = {"slug": ("name",)}

# ---------------- VariantAttributeValue Admin ----------------
@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('value', 'attribute', 'hex_code')
    search_fields = ('value', 'attribute__name')
    autocomplete_fields = ('attribute',)

# ---------------- ProductVariant Admin ----------------
@admin.register(ProductVariant)
class ProductVariantAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "product",
        "name",
        "code",
        "pcs_carton",
        "is_available",
        "color_display",
        "sizes_display",
        "attributes_display",
    )
    search_fields = ("product__name", "name", "code")
    list_filter = ("is_available", "product")
    autocomplete_fields = ("attributes", "sizes")
    inlines = [VariantImageInline]

    class Media:
        css = {'all': ('admin/css/custom_admin.css',)}

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

# ---------------- Color Admin ----------------
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "hex_code", "order")
    search_fields = ("name", "hex_code")

# ---------------- Size Admin ----------------
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    search_fields = ("name",)

# ---------------- VariantAttribute Admin ----------------
@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)