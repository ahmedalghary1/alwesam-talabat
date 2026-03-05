from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q
from django.utils.safestring import mark_safe
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
            'style="object-fit:cover;border-radius:8px;'
            'border:2px solid #e2e8f0;padding:2px;'
            'box-shadow:0 2px 6px rgba(0,0,0,.12);'
            'transition:transform .2s;" '
            'onmouseover="this.style.transform=\'scale(1.6)\'" '
            'onmouseout="this.style.transform=\'scale(1)\'" />',
            image_field.url, width, height,
        )
    return format_html(
        '<span style="display:inline-flex;align-items:center;justify-content:center;'
        'width:{}px;height:{}px;background:#f1f5f9;border-radius:8px;'
        'border:2px dashed #cbd5e1;color:#94a3b8;font-size:11px;">لا صورة</span>',
        width, height,
    )


def colored_badge(text: str, color: str = "#198754", icon: str = "") -> str:
    icon_html = f'<span style="margin-left:4px;">{icon}</span>' if icon else ""
    return format_html(
        '<span style="background:{};color:#fff;padding:3px 12px;'
        'border-radius:20px;font-size:12px;font-weight:700;'
        'letter-spacing:.3px;display:inline-flex;align-items:center;'
        'gap:4px;box-shadow:0 1px 4px {}44;">{}{}</span>',
        color, color, mark_safe(icon_html), text,
    )


def info_pill(label: str, value: str, bg: str = "#f0f9ff", border: str = "#bae6fd") -> str:
    return format_html(
        '<span style="background:{};border:1px solid {};color:#0369a1;'
        'padding:2px 10px;border-radius:6px;font-size:12px;font-weight:500;">'
        '<b>{}</b>: {}</span>',
        bg, border, label, value,
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
    readonly_fields     = ("image_thumb_large", "created_summary")
    prepopulated_fields = {"slug": ("name",)}
    ordering            = ("order",)
    list_per_page       = 25

    fieldsets = (
        (_("📁 المعلومات الأساسية"), {
            "fields": ("name", "slug", "description"),
            "classes": ("wide",),
        }),
        (_("🖼️ الصورة"), {
            "fields": ("image", "image_thumb_large"),
            "classes": ("collapse", "wide",),
        }),
        (_("⚙️ الإعدادات"), {
            "fields": ("order",),
            "classes": ("wide",),
        }),
    )

    @admin.display(description=_("الصورة"))
    def image_thumb(self, obj):
        return image_preview(obj.image, 52, 52)

    @admin.display(description=_("معاينة الصورة"))
    def image_thumb_large(self, obj):
        return image_preview(obj.image, 240, 240)

    @admin.display(description=_("عدد المنتجات"))
    def product_count(self, obj):
        count = obj.products.count()
        color = "#0d6efd" if count > 0 else "#94a3b8"
        return colored_badge(str(count), color, "📦")

    @admin.display(description="")
    def created_summary(self, obj):
        return info_pill("القسم", obj.name)

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
    verbose_name_plural = _("📷 الصور الإضافية")
    classes             = ("collapse",)

    @admin.display(description=_("معاينة"))
    def image_thumb(self, obj):
        return image_preview(obj.image, 65, 65)


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
    verbose_name_plural = _("🎨 الأنماط")
    show_change_link    = True
    classes             = ("collapse",)

    @admin.display(description=_("معاينة الصورة"))
    def variant_thumb(self, obj):
        return image_preview(obj.image, 65, 65)


# ─────────────────────────────────────────────
#  Product
# ─────────────────────────────────────────────

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display        = (
        "image_thumb", "name", "category_link",
        "sizes_summary", "variant_count",
        "pcs_carton_display", "availability_badge",
        "order", "created_at",
    )
    list_display_links  = ("name",)
    list_editable       = ("order",)
    list_filter         = ("is_available", "category")
    search_fields       = ("name", "slug", "description")
    readonly_fields     = ("image_thumb_large", "created_at", "updated_at", "product_stats")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal   = ("sizes",)
    ordering            = ("order",)
    save_on_top         = True
    inlines             = [ProductImagesInline, ProductVariantInline]
    list_per_page       = 20
    date_hierarchy      = "created_at"

    fieldsets = (
        (_("📋 المعلومات الأساسية"), {
            "fields": ("name", "slug", "description", "category"),
            "classes": ("wide",),
        }),
        (_("🖼️ الصورة الرئيسية"), {
            "fields": ("image", "image_thumb_large"),
            "classes": ("collapse", "wide",),
        }),
        (_("📐 المواصفات"), {
            "fields": ("pcs_carton", "sizes"),
            "classes": ("wide",),
        }),
        (_("⚙️ الإعدادات"), {
            "fields": ("is_available", "order"),
            "classes": ("wide",),
        }),
        (_("📊 إحصائيات"), {
            "fields": ("product_stats",),
            "classes": ("collapse", "wide",),
        }),
        (_("🕒 التواريخ"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse", "wide",),
        }),
    )

    class Media:
        css = {"all": ("admin/css/product_admin_fix.css",)}

    # ── display methods ──────────────────────

    @admin.display(description=_("الصورة"))
    def image_thumb(self, obj):
        return image_preview(obj.image, 58, 58)

    @admin.display(description=_("معاينة الصورة"))
    def image_thumb_large(self, obj):
        return image_preview(obj.image, 240, 240)

    @admin.display(description=_("القسم"))
    def category_link(self, obj):
        if obj.category:
            return format_html(
                '<a href="/admin/products/category/{}/change/" '
                'style="color:#2563eb;text-decoration:none;font-weight:600;">'
                '🏷️ {}</a>',
                obj.category.pk, obj.category.name,
            )
        return format_html('<span style="color:#cbd5e1;">—</span>')

    @admin.display(description=_("الأنماط"))
    def variant_count(self, obj):
        count = obj.variants.count()
        avail = obj.variants.filter(is_available=True).count()
        color = "#7c3aed" if count > 0 else "#94a3b8"
        return format_html(
            '<span title="{} متوفر من {}">{}</span>',
            avail, count, mark_safe(colored_badge(f"{avail}/{count}", color, "🎨")),
        )

    @admin.display(description=_("الحالة"))
    def availability_badge(self, obj):
        if obj.is_available:
            return colored_badge(_("متوفر"), "#059669", "✅")
        return colored_badge(_("غير متوفر"), "#dc2626", "❌")

    @admin.display(description=_("قطع/كرتون"), ordering="pcs_carton")
    def pcs_carton_display(self, obj):
        return info_pill("كرتون", f"{obj.pcs_carton} قطعة")

    @admin.display(description=_("المقاسات"))
    def sizes_summary(self, obj):
        sizes = list(obj.sizes.values_list("name", flat=True)[:5])
        if not sizes:
            return format_html('<span style="color:#cbd5e1;">—</span>')
        tags = "".join(
            f'<span style="background:#ede9fe;color:#5b21b6;padding:1px 7px;'
            f'border-radius:4px;font-size:11px;margin:1px;display:inline-block;">{s}</span>'
            for s in sizes
        )
        return mark_safe(tags)

    @admin.display(description=_("📊 إحصائيات المنتج"))
    def product_stats(self, obj):
        if not obj.pk:
            return "—"
        variants_total    = obj.variants.count()
        variants_avail    = obj.variants.filter(is_available=True).count()
        extra_images      = obj.images.count()
        sizes_count       = obj.sizes.count()

        return format_html(
            '<div style="display:flex;gap:10px;flex-wrap:wrap;padding:8px 0;">'
            '{} {} {} {}'
            '</div>',
            mark_safe(info_pill("الأنماط الكلية",    str(variants_total))),
            mark_safe(info_pill("الأنماط المتوفرة",  str(variants_avail),  "#f0fdf4", "#86efac")),
            mark_safe(info_pill("الصور الإضافية",    str(extra_images),    "#fff7ed", "#fed7aa")),
            mark_safe(info_pill("المقاسات",           str(sizes_count),     "#fdf4ff", "#e9d5ff")),
        )

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related("category")
            .prefetch_related("sizes", "variants")
            .annotate(_variant_count=Count("variants", distinct=True))
        )


# ─────────────────────────────────────────────
#  ProductImages (standalone)
# ─────────────────────────────────────────────

@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display    = ("image_thumb", "product_link", "order", "created_at")
    list_editable   = ("order",)
    list_filter     = ("product",)
    search_fields   = ("product__name",)
    readonly_fields = ("image_thumb_large", "created_at")
    ordering        = ("product", "order")
    list_per_page   = 30

    fieldsets = (
        (None, {
            "fields": ("product", "image", "image_thumb_large", "order"),
            "classes": ("wide",),
        }),
    )

    @admin.display(description=_("الصورة"))
    def image_thumb(self, obj):
        return image_preview(obj.image, 58, 58)

    @admin.display(description=_("معاينة"))
    def image_thumb_large(self, obj):
        return image_preview(obj.image, 220, 220)

    @admin.display(description=_("المنتج"))
    def product_link(self, obj):
        return format_html(
            '<a href="/admin/products/product/{}/change/" '
            'style="color:#2563eb;font-weight:600;">{}</a>',
            obj.product.pk, obj.product.name,
        )


# ─────────────────────────────────────────────
#  Size
# ─────────────────────────────────────────────

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display  = ("size_badge", "name", "order", "created_at")
    list_editable = ("order",)
    search_fields = ("name",)
    ordering      = ("order", "name")
    list_per_page = 40

    @admin.display(description=_("المقاس"))
    def size_badge(self, obj):
        return format_html(
            '<span style="background:#ede9fe;color:#5b21b6;padding:3px 12px;'
            'border-radius:6px;font-size:13px;font-weight:700;">{}</span>',
            obj.name,
        )


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
                '<div style="width:28px;height:28px;border-radius:6px;'
                'background:{};border:2px solid #e2e8f0;display:inline-block;'
                'box-shadow:0 1px 4px {}44;"></div>',
                obj.hex_code, obj.hex_code,
            )
        return format_html('<span style="color:#94a3b8;">—</span>')


@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display  = ("name", "values_count")
    search_fields = ("name",)
    inlines       = [VariantAttributeValueInline]

    @admin.display(description=_("عدد القيم"))
    def values_count(self, obj):
        return colored_badge(str(obj.values.count()), "#f97316", "🏷️")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _values_count=Count("values")
        )


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display  = ("color_swatch", "value", "attribute", "hex_display")
    list_filter   = ("attribute",)
    search_fields = ("value", "attribute__name")

    @admin.display(description=_("اللون"))
    def color_swatch(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="width:28px;height:28px;border-radius:6px;'
                'background:{};border:2px solid #e2e8f0;display:inline-block;'
                'box-shadow:0 1px 4px {}44;"></div>',
                obj.hex_code, obj.hex_code,
            )
        return format_html('<span style="color:#94a3b8;">—</span>')

    @admin.display(description=_("كود اللون"))
    def hex_display(self, obj):
        if obj.hex_code:
            return format_html(
                '<code style="background:#f1f5f9;padding:2px 8px;'
                'border-radius:4px;font-family:monospace;font-size:12px;">'
                '{}</code>',
                obj.hex_code,
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
    verbose_name_plural = _("📸 صور النمط")
    classes             = ("collapse",)

    @admin.display(description=_("معاينة"))
    def image_thumb(self, obj):
        return image_preview(obj.image, 65, 65)


# ─────────────────────────────────────────────
#  ProductVariant (standalone)
# ─────────────────────────────────────────────

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display        = (
        "image_thumb", "name", "product_link",
        "code_display", "pcs_carton_display",
        "attributes_summary", "availability_badge", "order",
    )
    list_display_links  = ("name",)
    list_editable       = ("order",)
    list_filter         = ("is_available", "product__category")
    search_fields       = ("name", "code", "product__name")
    readonly_fields     = ("image_thumb_large", "variant_stats")
    filter_horizontal   = ("sizes", "attributes")
    ordering            = ("product", "order")
    save_on_top         = True
    inlines             = [VariantImageInline]
    list_per_page       = 25

    fieldsets = (
        (_("📋 المعلومات الأساسية"), {
            "fields": ("product", "name", "code"),
            "classes": ("wide",),
        }),
        (_("🖼️ الصورة"), {
            "fields": ("image", "image_thumb_large"),
            "classes": ("collapse", "wide",),
        }),
        (_("📐 المواصفات"), {
            "fields": ("pcs_carton", "length_label", "sizes"),
            "classes": ("wide",),
        }),
        (_("🎨 الخصائص"), {
            "fields": ("attributes",),
            "classes": ("wide",),
        }),
        (_("⚙️ الإعدادات"), {
            "fields": ("is_available", "order"),
            "classes": ("wide",),
        }),
        (_("📊 إحصائيات"), {
            "fields": ("variant_stats",),
            "classes": ("collapse", "wide",),
        }),
    )

    # ── display methods ──────────────────────

    @admin.display(description=_("الصورة"))
    def image_thumb(self, obj):
        return image_preview(obj.image, 58, 58)

    @admin.display(description=_("معاينة الصورة"))
    def image_thumb_large(self, obj):
        return image_preview(obj.image, 240, 240)

    @admin.display(description=_("المنتج"))
    def product_link(self, obj):
        return format_html(
            '<a href="/admin/products/product/{}/change/" '
            'style="color:#2563eb;font-weight:600;">📦 {}</a>',
            obj.product.pk, obj.product.name,
        )

    @admin.display(description=_("الكود"), ordering="code")
    def code_display(self, obj):
        if obj.code:
            return format_html(
                '<code style="background:#f1f5f9;padding:2px 8px;'
                'border-radius:4px;font-size:12px;color:#374151;">{}</code>',
                obj.code,
            )
        return format_html('<span style="color:#cbd5e1;">—</span>')

    @admin.display(description=_("قطع/كرتون"), ordering="pcs_carton")
    def pcs_carton_display(self, obj):
        return info_pill("", f"{obj.pcs_carton} قطعة", "#fff7ed", "#fed7aa")

    @admin.display(description=_("الخصائص"))
    def attributes_summary(self, obj):
        attrs = list(obj.attributes.select_related("attribute")[:4])
        if not attrs:
            return format_html('<span style="color:#cbd5e1;">—</span>')
        parts = []
        for attr in attrs:
            if attr.hex_code:
                parts.append(
                    f'<span style="display:inline-flex;align-items:center;gap:4px;'
                    f'background:#f8fafc;border:1px solid #e2e8f0;padding:2px 8px;'
                    f'border-radius:6px;font-size:11px;margin:1px;">'
                    f'<span style="width:12px;height:12px;border-radius:3px;'
                    f'background:{attr.hex_code};display:inline-block;"></span>'
                    f'{attr.value}</span>'
                )
            else:
                parts.append(
                    f'<span style="background:#f8fafc;border:1px solid #e2e8f0;'
                    f'padding:2px 8px;border-radius:6px;font-size:11px;margin:1px;">'
                    f'{attr.value}</span>'
                )
        return mark_safe("".join(parts))

    @admin.display(description=_("الحالة"))
    def availability_badge(self, obj):
        if obj.is_available:
            return colored_badge(_("متوفر"), "#059669", "✅")
        return colored_badge(_("غير متوفر"), "#dc2626", "❌")

    @admin.display(description=_("📊 إحصائيات النمط"))
    def variant_stats(self, obj):
        if not obj.pk:
            return "—"
        images_count = obj.variant_images.count() if hasattr(obj, "variant_images") else 0
        sizes_count  = obj.sizes.count()
        attrs_count  = obj.attributes.count()

        return format_html(
            '<div style="display:flex;gap:10px;flex-wrap:wrap;padding:8px 0;">'
            '{} {} {}'
            '</div>',
            mark_safe(info_pill("الصور",     str(images_count), "#fff7ed", "#fed7aa")),
            mark_safe(info_pill("المقاسات",  str(sizes_count),  "#fdf4ff", "#e9d5ff")),
            mark_safe(info_pill("الخصائص",   str(attrs_count),  "#f0fdf4", "#86efac")),
        )

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related("product")
            .prefetch_related("sizes", "attributes")
        )