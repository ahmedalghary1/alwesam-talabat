from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from .models import (
    Product, Category, ProductImages,
    ProductVariant, Size,
    VariantImage, VariantAttribute, VariantAttributeValue
)

# -----------------------------
# Size
# -----------------------------
admin.site.register(Size)


# -----------------------------
# Variant Attribute System
# -----------------------------

class VariantAttributeValueInline(admin.TabularInline):
    model = VariantAttributeValue
    extra = 1


@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [VariantAttributeValueInline]


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attribute", "value", "hex_code")
    list_filter = ("attribute",)
    search_fields = ("value",)


# -----------------------------
# Product Images Inline
# -----------------------------
class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 1


# -----------------------------
# Variant Image Inline
# -----------------------------
class VariantImageInline(admin.TabularInline):
    model = VariantImage
    extra = 3


# -----------------------------
# Product Variant Inline (داخل المنتج)
# -----------------------------
class ProductVariantInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProductVariant
    extra = 1
    filter_horizontal = ("sizes", "attributes")
    fields = [
        "name",
        "code",
        "pcs_carton",
        "image",
        "is_available",
        "attributes",
        "sizes",
        "order",
    ]


# -----------------------------
# Category
# -----------------------------
@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order",)


# -----------------------------
# Product
# -----------------------------
@admin.register(Product)
class ProductAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("name", "category", "pcs_carton", "order")
    list_filter = ("category", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("sizes",)
    inlines = [ProductImagesInline, ProductVariantInline]
    ordering = ("order",)


# -----------------------------
# Product Variant (صفحة مستقلة)
# -----------------------------
@admin.register(ProductVariant)
class ProductVariantAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "product",
        "name",
        "code",
        "pcs_carton",
        "is_available",
        "order",
    )
    list_filter = ("is_available", "product")
    search_fields = ("product__name", "name", "code")
    filter_horizontal = ("sizes", "attributes")
    inlines = [VariantImageInline]
    ordering = ("order",)