def theme_processor(request):
    """Context processor to add current theme to all templates"""
    theme = request.session.get('theme', 'theme-light')
    return {'current_theme': theme}


def pending_users_count(request):
    """
    Add pending users count to all templates for admin users
    """
    if request.user.is_authenticated and request.user.is_staff:
        from .models import CustomUser
        count = CustomUser.objects.filter(is_active=False, is_staff=False).count()
        return {'pending_count': count}
    return {'pending_count': 0}
