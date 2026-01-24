"""
Serializers for support app - Customer messages and replies.
"""
from rest_framework import serializers
from support.models import CustomerMessage, MessageReply


class MessageReplySerializer(serializers.ModelSerializer):
    """Serializer for admin replies."""
    admin_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MessageReply
        fields = ['id', 'reply', 'admin_name', 'created_at']
    
    def get_admin_name(self, obj):
        return obj.admin_user.username if obj.admin_user else 'خدمة العملاء'


class CustomerMessageSerializer(serializers.ModelSerializer):
    """Serializer for customer messages."""
    replies = MessageReplySerializer(many=True, read_only=True)
    has_reply = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CustomerMessage
        fields = ['id', 'message', 'is_read', 'has_reply',
                  'replies', 'created_at']
        read_only_fields = ['is_read']


class CreateMessageSerializer(serializers.Serializer):
    """Serializer for creating new customer message."""
    message = serializers.CharField()
    
    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("الرسالة لا يمكن أن تكون فارغة")
        return value.strip()
