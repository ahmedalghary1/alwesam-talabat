from django.contrib import admin
from .models import (
    Category, 
    Product, 
    ProductImages, 
    Size, 
    VariantImage, 
    VariantAttribute, 
    VariantAttributeValue, 
    ProductVariant
)

# --- Inlines (لعرض النماذج المتعلقة ببعضها داخل صفحة واحدة) ---

class ProductImageInline(admin.TabularInline):
    """عرض الصور الإضافية للمنتج داخل صفحة المنتج"""
    model = ProductImages
    extra = 1
    fields = ('image', 'order')

class VariantImageInline(admin.TabularInline):
    """عرض صور النمط داخل صفحة النمط"""
    model = VariantImage
    extra = 1
    fields = ('image', 'order')

class ProductVariantInline(admin.StackedInline):
    """
    عرض أنماط المنتج داخل صفحة المنتج.
    استخدمنا StackedInline لأن النمط يحتوي على حقول كثيرة وعلاقات ManyToMany.
    """
    model = ProductVariant
    extra = 1
    fk_name = 'product'
    fields = ('name', 'code', 'image', 'pcs_carton', 'is_available', 'order', 'attributes', 'sizes')
    filter_horizontal = ('attributes', 'sizes') # سهولة اختيار الخصائص والمقاسات
    show_change_link = True # زر للتعديل الكامل في صفحة منفصلة إذا لزم الأمر

class VariantAttributeValueInline(admin.TabularInline):
    """عرض قيم الخصائص داخل صفحة نوع الخاصية (مثل: إضافة ألوان تحت اسم "لون")"""
    model = VariantAttributeValue
    extra = 2
    fields = ('value', 'hex_code')

# --- Model Admins ---

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',) # السماح بتعديل الترتيب مباشرة من القائمة
    search_fields = ('name',)
    ordering = ('order',)

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
    ordering = ('order',)

@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [VariantAttributeValueInline]
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_available', 'order', 'created_at')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline] # تضمين الصور والأنماط
    
    # تحسين اختيار العلاقات
    filter_horizontal = ('sizes',) # للمقاسات المباشرة للمنتج
    autocomplete_fields = ['category'] # بحث سريع عن القسم
    list_editable = ('is_available', 'order')
    ordering = ('order',)
    date_hierarchy = 'created_at'

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """
    إدارة مستقلة للأنماط (في حال أردت التعديل السريع على الأنماط دون الدخول للمنتج)
    """
    list_display = ('name', 'product', 'code', 'is_available', 'order')
    list_filter = ('product', 'is_available')
    search_fields = ('name', 'code', 'product__name')
    inlines = [VariantImageInline]
    
    filter_horizontal = ('attributes', 'sizes')
    autocomplete_fields = ['product']
    list_editable = ('is_available', 'order')

# تسجيل موديل صور النمط إذا كنت تريد إدارته بشكل منفصل (اختياري)
# admin.site.register(VariantImage)