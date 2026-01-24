"""
Custom permissions for API endpoints.
"""
from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners of an object or admin to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users can access everything
        if request.user.is_staff:
            return True
        
        # Check if object has user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsActiveUser(permissions.BasePermission):
    """
    Permission to check if user account is active.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active
