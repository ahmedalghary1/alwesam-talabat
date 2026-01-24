"""
URL configuration for API v1.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import accounts, products, cart, orders, support

# Create router
router = DefaultRouter()

# Authentication & User
router.register(r'auth', accounts.AuthViewSet, basename='auth')
router.register(r'profile', accounts.UserProfileViewSet, basename='profile')
router.register(r'addresses', accounts.AddressViewSet, basename='address')

# Products
router.register(r'categories', products.CategoryViewSet, basename='category')
router.register(r'products', products.ProductViewSet, basename='product')

# Cart
router.register(r'cart', cart.CartViewSet, basename='cart')

# Orders
router.register(r'orders', orders.OrderViewSet, basename='order')

# Support
router.register(r'support', support.SupportViewSet, basename='support')

urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
