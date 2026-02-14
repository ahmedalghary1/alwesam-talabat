"""
Views for support API - Customer support messaging.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from support.models import CustomerMessage
from ..serializers.support import CustomerMessageSerializer, CreateMessageSerializer

import logging
logger = logging.getLogger(__name__)

class SupportViewSet(viewsets.ViewSet):
    """
    ViewSet for customer support messages.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get all user messages."""
        messages = CustomerMessage.objects.filter(user=request.user)\
            .prefetch_related('replies')\
            .order_by('-created_at')
        
        serializer = CustomerMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Get specific message with replies."""
        try:
            message = CustomerMessage.objects.prefetch_related('replies')\
                .get(id=pk, user=request.user)
            serializer = CustomerMessageSerializer(message)
            return Response(serializer.data)
        except CustomerMessage.DoesNotExist:
            return Response(
                {"error": "الرسالة غير موجودة"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """Send new support message."""
        serializer = CreateMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message = CustomerMessage.objects.create(
            user=request.user,
            message=serializer.validated_data['message']
        )
        
        return Response(
            CustomerMessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )
