"""
Django admin configuration for Accounts app.

Registers Profile and Address models with search and filter capabilities.
"""
from django.contrib import admin
from .models import Profile, Address


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'country')
    list_filter = ('country', 'city')
    search_fields = ('user__username', 'street', 'city')
