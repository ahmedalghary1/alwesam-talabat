from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('pending-approval/', views.pending_approval_view, name='pending_approval'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('set-language/', views.set_language, name='set_language'),
    path('set-theme/', views.set_theme, name='set_theme'),
    path('get-theme/', views.get_theme, name='get_theme'),
    path('get-language/', views.get_language, name='get_language'),
]
