"""
Views for accounts API - Authentication and user management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from accounts.models import CustomUser, Profile
from ..serializers.accounts import (
    UserSerializer, ProfileSerializer,
    RegisterSerializer, LoginSerializer
)
import logging
logger = logging.getLogger(__name__)


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

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout and blacklist the refresh token."""
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "تم تسجيل الخروج بنجاح"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(
                {"error": "رمز التحديث غير صالح أو مفقود"},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileViewSet(viewsets.ViewSet):
    """
    ViewSet for user profile management.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get current user profile."""
        user = request.user
        profile = getattr(user, 'profile', None)
        
        return Response({
            "user": UserSerializer(user).data,
            "profile": ProfileSerializer(profile).data if profile else None
        })
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update user profile and address."""
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Update Profile data
        profile_serializer = ProfileSerializer(profile, data=request.data, partial=True)
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()
        
        # Update User data (phone, address) if provided
        user_data = {}
        if 'phone' in request.data:
            user_data['phone'] = request.data['phone']
        if 'address' in request.data:
            user_data['address'] = request.data['address']
        if 'username' in request.data:
            user_data['username'] = request.data['username']
        if 'email' in request.data:
            user_data['email'] = request.data['email']

            
        if user_data:
            user_serializer = UserSerializer(user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        
        return Response({
            "user": UserSerializer(user).data,
            "profile": profile_serializer.data
        })
