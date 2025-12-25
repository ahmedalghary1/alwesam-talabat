from django.contrib import admin
from .models import Product, Category, ProductImages, ProductVariant , Color , Size

admin.site.register(Color)
admin.site.register(Size)

class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['name', 'code', 'variant_type', 'variant_value', 
              'pcs_carton', 'image',  'is_available']
    readonly_fields = []


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'pcs_carton')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImagesInline, ProductVariantInline]


@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'code', 'variant_type', 'variant_value', 'pcs_carton', 'is_available')
    list_filter = ('variant_type', 'is_available')
    search_fields = ('product__name', 'name', 'code', 'variant_value')
