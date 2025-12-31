from django.contrib import admin
from .models import CustomerMessage, MessageReply


@admin.register(CustomerMessage)
class CustomerMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'message_preview', 'is_read', 'has_reply', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'user__email', 'message']
    readonly_fields = ['user', 'message', 'created_at']
    
    def message_preview(self, obj):
        """عرض معاينة الرسالة"""
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'معاينة الرسالة'
    
    def has_reply(self, obj):
        """التحقق من وجود رد"""
        return obj.has_reply
    has_reply.boolean = True
    has_reply.short_description = 'تم الرد'


@admin.register(MessageReply)
class MessageReplyAdmin(admin.ModelAdmin):
    list_display = ['customer_message', 'admin_user', 'reply_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['admin_user__username', 'reply']
    readonly_fields = ['customer_message', 'admin_user', 'created_at']
    
    def reply_preview(self, obj):
        """عرض معاينة الرد"""
        return obj.reply[:50] + '...' if len(obj.reply) > 50 else obj.reply
    reply_preview.short_description = 'معاينة الرد'
