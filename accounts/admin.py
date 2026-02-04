"""
Django admin configuration for Accounts app.

Registers Profile  models with search and filter capabilities.
"""
from django.contrib import admin
from .models import Profile , CustomUser

admin.site.register(CustomUser)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)
