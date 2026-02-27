"""
Django admin configuration for Products app.

Registers models with customized list displays, filters, and inline editing.
"""
from django.contrib import admin
from .models import Product, Category, ProductImages, ProductVariant , Color , Size,VariantImage

admin.site.register(Color)
admin.site.register(Size)

class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = [
        'name', 'code', 'variant_type',
        'pcs_carton', 'image',
        'is_available','color', 'sizes'  
    ]
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')  
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)  


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'pcs_carton', 'order')  # ← أضف order
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('sizes',)
    inlines = [ProductImagesInline, ProductVariantInline]
    ordering = ('order',)  # ← ترتيب المنتجات حسب order


@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')

class VariantImageInline(admin.TabularInline):
    model = VariantImage
    extra = 5 
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'code', 'variant_type', 'pcs_carton', 'is_available', 'order')  # ← أضف order
    list_filter = ('variant_type', 'is_available')
    search_fields = ('product__name', 'name', 'code')
    inlines = [VariantImageInline]
    filter_horizontal = ('sizes',)
    ordering = ('order',)  
