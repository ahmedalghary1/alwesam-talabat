from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Product, ProductImages,
    Size, ProductVariant, VariantImage,
    VariantAttribute, VariantAttributeValue
)


# ─────────────────────────────────────────────
# Inlines
# ─────────────────────────────────────────────

class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 1
    fields = ('image', 'order', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px; border-radius:4px;">', obj.image.url)
        return "-"
    image_preview.short_description = "معاينة"


class VariantImageInline(admin.TabularInline):
    model = VariantImage
    extra = 1
    fields = ('image', 'order', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px; border-radius:4px;">', obj.image.url)
        return "-"
    image_preview.short_description = "معاينة"


class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0
    fields = ('name', 'code', 'pcs_carton', 'sizes', 'is_available', 'image', 'order')
    filter_horizontal = ('sizes', 'attributes')
    show_change_link = True


# ─────────────────────────────────────────────
# Category
# ─────────────────────────────────────────────

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'image_preview', 'order')
    list_editable = ('order',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px; border-radius:4px;">', obj.image.url)
        return "-"
    image_preview.short_description = "الصورة"


# ─────────────────────────────────────────────
# Product
# ─────────────────────────────────────────────

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'pcs_carton', 'is_available', 'image_preview', 'order')
    list_editable = ('is_available', 'order')
    list_filter   = ('category', 'is_available')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('sizes',)
    inlines = [ProductVariantInline, ProductImagesInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px; border-radius:4px;">', obj.image.url)
        return "-"
    image_preview.short_description = "الصورة"


# ─────────────────────────────────────────────
# ProductVariant
# ─────────────────────────────────────────────

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display  = ('name', 'product', 'code', 'pcs_carton', 'is_available', 'image_preview', 'order')
    list_editable = ('is_available', 'order')
    list_filter   = ('product', 'is_available')
    search_fields = ('name', 'code')
    filter_horizontal = ('sizes', 'attributes')
    inlines = [VariantImageInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px; border-radius:4px;">', obj.image.url)
        return "-"
    image_preview.short_description = "الصورة"


# ─────────────────────────────────────────────
# Size
# ─────────────────────────────────────────────

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display  = ('name', 'order')
    list_editable = ('order',)
    search_fields = ('name',)


# ─────────────────────────────────────────────
# VariantAttribute & Values
# ─────────────────────────────────────────────

class VariantAttributeValueInline(admin.TabularInline):
    model = VariantAttributeValue
    extra = 1
    fields = ('value', 'hex_code', 'color_preview')
    readonly_fields = ('color_preview',)

    def color_preview(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="width:24px;height:24px;border-radius:50%;background:{}; border:1px solid #ccc;"></div>',
                obj.hex_code
            )
        return "-"
    color_preview.short_description = "اللون"


@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [VariantAttributeValueInline]