"""
Views for accounts API - Authentication and user management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from accounts.models import CustomUser, Profile, Address
from ..serializers.accounts import (
    UserSerializer, ProfileSerializer, AddressSerializer,
    RegisterSerializer, LoginSerializer
)


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet for authentication - register and login.
    """
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            "message": "تم التسجيل بنجاح. حسابك في انتظار موافقة المسؤول.",
            "user": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login with email or phone."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username_or_phone = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=username_or_phone, password=password)
        
        if user is None:
            return Response(
                {"error": "بيانات الدخول غير صحيحة"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {"error": "حسابك في انتظار موافقة المسؤول"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        })


class UserProfileViewSet(viewsets.ViewSet):
    """
    ViewSet for user profile management.
    """
    permission_classes = [IsAuthenticated]
    
    def retrieve(self, request):
        """Get current user profile."""
        user = request.user
        profile = getattr(user, 'profile', None)
        
        return Response({
            "user": UserSerializer(user).data,
            "profile": ProfileSerializer(profile).data if profile else None
        })
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update user profile."""
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)
        
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)


class AddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user addresses.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
