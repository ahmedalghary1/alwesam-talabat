from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from .models import (
    Category, Product, ProductImages,
    Size, VariantImage,
    VariantAttribute, VariantAttributeValue, ProductVariant,
)


# ─────────────────────────────────────────────
#  Shared helpers
# ─────────────────────────────────────────────

def image_preview(image_field, width: int = 60, height: int = 60) -> str:
    if image_field:
        return format_html(
            '<img src="{}" width="{}" height="{}" '
            'style="object-fit:cover;border-radius:6px;'
            'border:1px solid #ddd;padding:2px;" />',
            image_field.url, width, height,
        )
    return format_html(
        '<span style="color:#aaa;font-style:italic;">{}</span>', _("لا توجد صورة")
    )


def colored_badge(text: str, color: str = "#198754") -> str:
    return format_html(
        '<span style="background:{};color:#fff;padding:2px 10px;'
        'border-radius:12px;font-size:12px;font-weight:600;">{}</span>',
        color, text,
    )


# ─────────────────────────────────────────────
#  Category
# ─────────────────────────────────────────────

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ("image_thumb", "name", "slug", "product_count", "order")
    list_display_links  = ("name",)
    list_editable       = ("order",)
    search_fields       = ("name", "slug")
    # slug قابل للتعديل — لا يوجد في readonly_fields
    readonly_fields     = ("image_thumb_large",)
    prepopulated_fields = {"slug": ("name",)}
    ordering            = ("order",)

    fieldsets = (
        (_("المعلومات الأساسية"), {
            "fields": ("name", "slug", "description"),
            "classes": ("wide",),
        }),
        (_("الصورة"), {
            "fields": ("image", "image_thumb_large"),
            "classes": ("collapse", "wide",),
        }),
        (_("الترتيب"), {
            "fields": ("order",),
            "classes": ("wide",),
        }),
    )

    @admin.display(description=_("الصورة"))
    def image_thumb(self, obj):
        return image_preview(obj.image, 50, 50)

    @admin.display(description=_("معاينة الصورة"))
    def image_thumb_large(self, obj):
        return image_preview(obj.image, 200, 200)

    @admin.display(description=_("عدد المنتجات"))
    def product_count(self, obj):
        return colored_badge(str(obj.products.count()), "#0d6efd")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _product_count=Count("products")
        )


# ─────────────────────────────────────────────
#  Product inlines
# ─────────────────────────────────────────────

class ProductImagesInline(admin.TabularInline):
    model               = ProductImages
    extra               = 1
    fields              = ("image", "image_thumb", "order")
    readonly_fields     = ("image_thumb",)
    ordering            = ("order",)
    verbose_name        = _("صورة إضافية")
    verbose_name_plural = _("الصور الإضافية")

    @admin.display(description=_("معاينة"))
    def image_thumb(self, obj):
        return image_preview(obj.image, 60, 60)


class ProductVariantInline(admin.StackedInline):
    model               = ProductVariant
    extra               = 0
    fields              = (
        ("name", "code"),
        ("pcs_carton", "is_available", "order"),
        ("image", "variant_thumb"),
        "sizes",
        "attributes",
        "length_label",
    )
    readonly_fields     = ("variant_thumb",)
    filter_horizontal   = ("sizes", "attributes")
    verbose_name        = _("نمط")
    verbose_name_plural = _("الأنماط")
    show_change_link    = True

    @admin.display(description=_("معاينة الصورة"))
    def variant_thumb(self, obj):
        return image_preview(obj.image, 60, 60)


# ─────────────────────────────────────────────
#  Product
# ─────────────────────────────────────────────

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display        = (
        "image_thumb", "name", "category_link",
        "pcs_carton", "variant_count", "availability_badge",
        "order", "created_at",
    )
    list_display_links  = ("name",)
    list_editable       = ("order",)
    list_filter         = ("is_available", "category")
    search_fields       = ("name", "slug", "description")
    # slug قابل للتعديل — محذوف من readonly_fields
    readonly_fields     = ("image_thumb_large", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal   = ("sizes",)
    ordering            = ("order",)
    save_on_top         = True
    inlines             = [ProductImagesInline, ProductVariantInline]

    # "wide" على كل fieldset يجعل المحتوى يمتد لعرض كامل
    # ويزيل المساحة الفارغة على اليمين في Jazzmin
    fieldsets = (
        (_("المعلومات الأساسية"), {
            "fields": ("name", "slug", "description", "category"),
            "classes": ("wide",),
        }),
        (_("الصورة الرئيسية"), {
            "fields": ("image", "image_thumb_large"),
            "classes": ("collapse", "wide",),
        }),
        (_("المواصفات"), {
            "fields": ("pcs_carton", "sizes"),
            "classes": ("wide",),
        }),
        (_("الإعدادات"), {
            "fields": ("is_available", "order"),
            "classes": ("wide",),
        }),
        (_("التواريخ"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse", "wide",),
        }),
    )

    class Media:
        css = {
            "all": ("admin/css/product_admin_fix.css",),
        }

    @admin.display(description=_("الصورة"))
    def image_thumb(self, obj):
        return image_preview(obj.image, 55, 55)

    @admin.display(description=_("معاينة الصورة"))
    def image_thumb_large(self, obj):
        return image_preview(obj.image, 220, 220)

    @admin.display(description=_("القسم"))
    def category_link(self, obj):
        if obj.category:
            return format_html(
                '<a href="/admin/products/category/{}/change/">{}</a>',
                obj.category.pk, obj.category.name,
            )
        return format_html('<span style="color:#aaa;">—</span>')

    @admin.display(description=_("الأنماط"))
    def variant_count(self, obj):
        return colored_badge(str(obj.variants.count()), "#6f42c1")

    @admin.display(description=_("الحالة"))
    def availability_badge(self, obj):
        if obj.is_available:
            return colored_badge(_("متوفر"), "#198754")
        return colored_badge(_("غير متوفر"), "#dc3545")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category").annotate(
            _variant_count=Count("variants", distinct=True)
        )


# ─────────────────────────────────────────────
#  ProductImages (standalone)
# ─────────────────────────────────────────────

@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display    = ("image_thumb", "product", "order", "created_at")
    list_editable   = ("order",)
    list_filter     = ("product",)
    search_fields   = ("product__name",)
    readonly_fields = ("image_thumb_large", "created_at")
    ordering        = ("product", "order")

    fieldsets = (
        (None, {
            "fields": ("product", "image", "image_thumb_large", "order"),
            "classes": ("wide",),
        }),
    )

    @admin.display(description=_("الصورة"))
    def image_thumb(self, obj):
        return image_preview(obj.image, 55, 55)

    @admin.display(description=_("معاينة"))
    def image_thumb_large(self, obj):
        return image_preview(obj.image, 200, 200)


# ─────────────────────────────────────────────
#  Size
# ─────────────────────────────────────────────

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display  = ("name", "order", "created_at")
    list_editable = ("order",)
    search_fields = ("name",)
    ordering      = ("order", "name")


# ─────────────────────────────────────────────
#  VariantAttribute & VariantAttributeValue
# ─────────────────────────────────────────────

class VariantAttributeValueInline(admin.TabularInline):
    model               = VariantAttributeValue
    extra               = 1
    fields              = ("value", "hex_code", "color_preview")
    readonly_fields     = ("color_preview",)
    verbose_name        = _("قيمة")
    verbose_name_plural = _("القيم")

    @admin.display(description=_("معاينة اللون"))
    def color_preview(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="width:24px;height:24px;border-radius:4px;'
                'background:{};border:1px solid #ccc;display:inline-block;"></div>',
                obj.hex_code,
            )
        return "—"


@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display  = ("name", "values_count")
    search_fields = ("name",)
    inlines       = [VariantAttributeValueInline]

    @admin.display(description=_("عدد القيم"))
    def values_count(self, obj):
        return colored_badge(str(obj.values.count()), "#fd7e14")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _values_count=Count("values")
        )


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display  = ("value", "attribute", "color_swatch")
    list_filter   = ("attribute",)
    search_fields = ("value", "attribute__name")

    @admin.display(description=_("معاينة اللون"))
    def color_swatch(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="width:24px;height:24px;border-radius:4px;'
                'background:{};border:1px solid #ccc;display:inline-block;'
                'margin-right:6px;"></div> {}',
                obj.hex_code, obj.hex_code,
            )
        return "—"


# ─────────────────────────────────────────────
#  VariantImage inline
# ─────────────────────────────────────────────

class VariantImageInline(admin.TabularInline):
    model               = VariantImage
    extra               = 1
    fields              = ("image", "image_thumb", "order")
    readonly_fields     = ("image_thumb",)
    ordering            = ("order",)
    verbose_name        = _("صورة النمط")
    verbose_name_plural = _("صور النمط")

    @admin.display(description=_("معاينة"))
    def image_thumb(self, obj):
        return image_preview(obj.image, 60, 60)


# ─────────────────────────────────────────────
#  ProductVariant (standalone)
# ─────────────────────────────────────────────

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display        = (
        "image_thumb", "name", "product_link",
        "code", "pcs_carton", "availability_badge", "order",
    )
    list_display_links  = ("name",)
    list_editable       = ("order",)
    list_filter         = ("is_available", "product__category")
    search_fields       = ("name", "code", "product__name")
    readonly_fields     = ("image_thumb_large",)
    filter_horizontal   = ("sizes", "attributes")
    ordering            = ("product", "order")
    save_on_top         = True
    inlines             = [VariantImageInline]

    fieldsets = (
        (_("المعلومات الأساسية"), {
            "fields": ("product", "name", "code"),
            "classes": ("wide",),
        }),
        (_("الصورة"), {
            "fields": ("image", "image_thumb_large"),
            "classes": ("collapse", "wide",),
        }),
        (_("المواصفات"), {
            "fields": ("pcs_carton", "length_label", "sizes"),
            "classes": ("wide",),
        }),
        (_("الخصائص"), {
            "fields": ("attributes",),
            "classes": ("wide",),
        }),
        (_("الإعدادات"), {
            "fields": ("is_available", "order"),
            "classes": ("wide",),
        }),
    )

    @admin.display(description=_("الصورة"))
    def image_thumb(self, obj):
        return image_preview(obj.image, 55, 55)

    @admin.display(description=_("معاينة الصورة"))
    def image_thumb_large(self, obj):
        return image_preview(obj.image, 200, 200)

    @admin.display(description=_("المنتج"))
    def product_link(self, obj):
        return format_html(
            '<a href="/admin/products/product/{}/change/">{}</a>',
            obj.product.pk, obj.product.name,
        )

    @admin.display(description=_("الحالة"))
    def availability_badge(self, obj):
        if obj.is_available:
            return colored_badge(_("متوفر"), "#198754")
        return colored_badge(_("غير متوفر"), "#dc3545")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product")