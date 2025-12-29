from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone_number', 'status', 'created_at', 'get_total_pieces')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = (
        'id',
        'user__username', 
        'user__email',
        'user__first_name',
        'user__last_name',
        'phone_number',
        'address',
        'notes',
        'items__product__name',
    )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    
    def get_total_pieces(self, obj):
        """Display total pieces in admin list"""
        return obj.get_total_pieces()
    get_total_pieces.short_description = 'إجمالي القطع'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'get_display_info', 'quantity', 'unit_type')
    list_filter = ('unit_type', 'order__created_at', 'order__status')
    search_fields = (
        'product__name',
        'order__id',
        'order__user__username',
        'color_name',
        'size_name',
    )
    raw_id_fields = ('order', 'product', 'variant')
    
    def get_display_info(self, obj):
        """Display variant, color, and size information"""
        info_parts = []
        if obj.color_name:
            info_parts.append(f"لون: {obj.color_name}")
        if obj.size_name:
            info_parts.append(f"مقاس: {obj.size_name}")
        return " | ".join(info_parts) if info_parts else "-"
    get_display_info.short_description = 'التفاصيل'
