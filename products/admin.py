from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

from .models import (
    Product,
    Category,
    ProductImages,
    ProductVariant,
    Size,
    VariantImage,
    VariantAttribute,
    VariantAttributeValue
)


# -------------------------------------------------
# Size
# -------------------------------------------------

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    ordering = ("order",)
    search_fields = ("name",)


# -------------------------------------------------
# Variant Attributes
# -------------------------------------------------

class VariantAttributeValueInline(admin.TabularInline):
    model = VariantAttributeValue
    extra = 1


@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [VariantAttributeValueInline]


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attribute", "value", "hex_code")
    list_filter = ("attribute",)
    search_fields = ("value",)


# -------------------------------------------------
# Product Images
# -------------------------------------------------

class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 1
    fields = ("image", "order")


# -------------------------------------------------
# Variant Images
# -------------------------------------------------

class VariantImageInline(admin.TabularInline):
    model = VariantImage
    extra = 2
    fields = ("image", "order")


# -------------------------------------------------
# Product Variant Inline داخل المنتج
# -------------------------------------------------

class ProductVariantInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProductVariant
    extra = 1
    filter_horizontal = ("sizes", "attributes")

    fields = (
        "name",
        "code",
        "pcs_carton",
        "is_available",
        "attributes",
        "sizes",
        "order",
    )


# -------------------------------------------------
# Category
# -------------------------------------------------

@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order",)
    search_fields = ("name",)


# -------------------------------------------------
# Product
# -------------------------------------------------

@admin.register(Product)
class ProductAdmin(SortableAdminMixin, admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "variants_count",
        "variants_link",
        "pcs_carton",
        "order",
    )

    list_filter = ("category", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    filter_horizontal = ("sizes",)

    inlines = [
        ProductImagesInline,
        ProductVariantInline
    ]

    ordering = ("order",)

    fieldsets = (
        ("معلومات المنتج", {
            "fields": (
                "name",
                "slug",
                "category",
                "description",
            )
        }),

        ("الصورة الرئيسية", {
            "fields": ("image",)
        }),

        ("التعبئة", {
            "fields": ("pcs_carton",)
        }),

        ("المقاسات العامة", {
            "fields": ("sizes",)
        }),

        ("الحالة", {
            "fields": ("is_available",)
        }),
    )

    def variants_count(self, obj):
        return obj.variants.count()
    variants_count.short_description = "عدد الأنماط"

    def variants_link(self, obj):
        url = (
            reverse("admin:products_productvariant_changelist")
            + f"?product__id__exact={obj.id}"
        )

        return format_html(
            '<a class="button" href="{}">عرض الأنماط</a>',
            url
        )

    variants_link.short_description = "الأنماط"


# -------------------------------------------------
# Product Variant
# -------------------------------------------------

@admin.register(ProductVariant)
class ProductVariantAdmin(SortableAdminMixin, admin.ModelAdmin):

    list_display = (
        "product",
        "name",
        "color_display",
        "attributes_display",
        "pcs_carton",
        "is_available",
        "order",
    )

    list_filter = (
        "product",
        "is_available",
    )

    search_fields = (
        "product__name",
        "name",
        "code",
    )

    autocomplete_fields = ("product",)

    filter_horizontal = (
        "sizes",
        "attributes",
    )

    inlines = [
        VariantImageInline
    ]

    ordering = ("order",)

    list_select_related = ("product",)

    list_per_page = 40

    fieldsets = (
        ("معلومات النمط", {
            "fields": (
                "product",
                "name",
                "code",
                "is_available",
            )
        }),

        ("الخصائص", {
            "fields": (
                "attributes",
                "sizes",
                "length_label",
            )
        }),

        ("التعبئة", {
            "fields": (
                "pcs_carton",
            )
        }),

        ("الصورة", {
            "fields": (
                "image",
            )
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("attributes__attribute")

    # ----------------------
    # عرض اللون
    # ----------------------

    def color_display(self, obj):
        color = obj.color

        if not color:
            return "-"

        return format_html(
            '<span style="display:inline-block;width:16px;height:16px;background:{};border-radius:50%;margin-right:6px;"></span>{}',
            color.hex_code or "#ccc",
            color.value
        )

    color_display.short_description = "اللون"

    # ----------------------
    # عرض الخصائص
    # ----------------------

    def attributes_display(self, obj):

        attrs = obj.attributes.all()

        if not attrs:
            return "-"

        return ", ".join(
            f"{a.attribute.name}: {a.value}"
            for a in attrs
        )

    attributes_display.short_description = "الخصائص"