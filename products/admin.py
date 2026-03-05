from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from .models import (
    Product, Category, ProductImages,
    ProductVariant, Size,
    VariantImage, VariantAttribute, VariantAttributeValue
)


# -----------------------------
# Size Admin
# -----------------------------
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    ordering = ("order",)
    search_fields = ("name",)


# -----------------------------
# Variant Attribute System
# -----------------------------
class VariantAttributeValueInline(admin.TabularInline):
    model = VariantAttributeValue
    extra = 1
    fields = ("value", "hex_code")
    show_change_link = True


@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [VariantAttributeValueInline]
    search_fields = ("name",)


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attribute", "value", "hex_code")
    list_filter = ("attribute",)
    search_fields = ("value",)
    ordering = ("attribute", "value")


# -----------------------------
# Product Images Inline
# -----------------------------
class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 1
    readonly_fields = ("image_tag",)
    fields = ("image_tag", "image", "order")
    show_change_link = True

    def image_tag(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="width: 60px; height:auto;" />'
        return "-"
    image_tag.allow_tags = True
    image_tag.short_description = "صورة"


# -----------------------------
# Variant Image Inline
# -----------------------------
class VariantImageInline(admin.TabularInline):
    model = VariantImage
    extra = 3
    readonly_fields = ("image_tag",)
    fields = ("image_tag", "image", "order")
    show_change_link = True

    def image_tag(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="width: 60px; height:auto;" />'
        return "-"
    image_tag.allow_tags = True
    image_tag.short_description = "صورة"


# -----------------------------
# Product Variant Inline (داخل المنتج)
# -----------------------------
class ProductVariantInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProductVariant
    extra = 1
    filter_horizontal = ("sizes", "attributes")
    fields = (
        "name",
        "code",
        "pcs_carton",
        "image_tag",
        "image",
        "is_available",
        "attributes",
        "sizes",
        "order",
    )
    readonly_fields = ("image_tag",)

    def image_tag(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="width: 60px; height:auto;" />'
        return "-"
    image_tag.allow_tags = True
    image_tag.short_description = "صورة النمط"


# -----------------------------
# Category Admin
# -----------------------------
@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order",)
    search_fields = ("name",)


# -----------------------------
# Product Admin
# -----------------------------
@admin.register(Product)
class ProductAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("name", "category", "pcs_carton", "order", "is_available", "created_at")
    list_filter = ("category", "is_available", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("sizes",)
    inlines = [ProductImagesInline, ProductVariantInline]
    ordering = ("order",)
    # تحسين عرض الصفحة الكبيرة
    class Media:
        css = {
            "all": ("admin/css/custom_admin.css",)
        }


# -----------------------------
# Product Variant Admin (صفحة مستقلة)
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
        "color_name_display",
        "sizes_list_display",
    )
    list_filter = ("is_available", "product")
    search_fields = ("product__name", "name", "code")
    filter_horizontal = ("sizes", "attributes")
    inlines = [VariantImageInline]
    ordering = ("order",)

    def color_name_display(self, obj):
        color = obj.color
        return color.value if color else "-"
    color_name_display.short_description = "اللون"

    def sizes_list_display(self, obj):
        return ", ".join([size.name for size in obj.sizes.all()])
    sizes_list_display.short_description = "المقاسات"