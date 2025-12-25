from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages


class CheckUserActiveMiddleware:
    """
    Middleware to check if user is active on every request.
    If user is logged in but account is deactivated, force logout.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Check if user account is inactive
            if not request.user.is_active:
                # Log the user out
                logout(request)
                messages.warning(
                    request, 
                    'تم إيقاف حسابك من قبل المسؤول. يرجى التواصل مع الإدارة للمزيد من المعلومات.'
                )
                # Redirect to login page
                return redirect('accounts:login')
        
        response = self.get_response(request)
        return response
