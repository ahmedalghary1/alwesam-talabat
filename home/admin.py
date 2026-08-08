from django.contrib import admin
from django.utils.html import format_html

from .models import HomeSlide
from .forms import HomeSlideForm


@admin.register(HomeSlide)
class HomeSlideAdmin(admin.ModelAdmin):
    form = HomeSlideForm
    list_display = ['preview', 'title', 'order', 'is_active', 'updated_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'alt_text']
    readonly_fields = ['preview_large', 'image_width', 'image_height', 'created_at', 'updated_at']
    ordering = ['order', 'id']

    @admin.display(description='معاينة')
    def preview(self, obj):
        if not obj.image:
            return '-'
        return format_html(
            '<img src="{}" alt="" style="width:120px;height:48px;object-fit:contain;background:#f4f4f4">',
            obj.image.url,
        )

    @admin.display(description='معاينة الصورة')
    def preview_large(self, obj):
        if not obj.image:
            return '-'
        return format_html(
            '<img src="{}" alt="" style="max-width:720px;width:100%;height:auto">',
            obj.image.url,
        )

    def delete_queryset(self, request, queryset):
        for slide in queryset.iterator():
            slide.delete()
