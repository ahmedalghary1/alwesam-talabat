from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from .forms import SignupForm, LoginForm, ProfileUpdateForm, ProfileImageForm
from core.constants import LOGIN_RATE_LIMIT
import json
import logging

logger = logging.getLogger(__name__)


def signup_view(request):
    """
    Register a new user account.
    
    New users are created with is_active=False and require admin approval
    before they can login. This implements a business verification workflow.
    """
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                # Set user as inactive - requires admin approval
                user.is_active = False
                user.save()
                form.save_profile_image(user)
            
            logger.info('New user registered (inactive): %s', user.email or user.username)
            messages.success(
                request,
                'تم إنشاء حسابك بنجاح وإرساله إلى المسؤول للمراجعة.'
            )
            # Redirect to pending approval page (no auto-login)
            return redirect('accounts:pending_approval')
    else:
        form = SignupForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


@ratelimit(key='ip', rate=LOGIN_RATE_LIMIT, method='POST', block=True)
def login_view(request):
    """
    Authenticate user with phone number, email, or username.
    
    Uses a custom authentication backend that accepts all three identifiers.
    Rate limited to prevent brute force attacks.
    """
    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            identifier = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # The backend accepts phone, email, or username through this identifier.
            user = authenticate(request, username=identifier, password=password)

            if user is not None:
                # Check if user account is active
                if not user.is_active:
                    logger.warning('Login attempt for inactive user: %s', user.email or user.username)
                    messages.warning(request, 'حسابك في انتظار موافقة المسؤول. سيتم إشعارك عند تفعيل حسابك.')
                    return render(request, 'accounts/login.html', {'form': form})

                login(request, user)
                logger.info('User %s logged in successfully', user.email or user.username)

                # Sync cart from localStorage to database
                sync_cart_on_login(request)

                messages.success(request, f'مرحباً {user.username}!')
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url and url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    return redirect(next_url)
                return redirect('home:home')

            logger.warning('Failed login attempt for supplied identifier')
            messages.error(request, 'رقم الهاتف/البريد الإلكتروني أو كلمة المرور غير صحيحة')

    return render(request, 'accounts/login.html', {'form': form})


def pending_approval_view(request):
    """
    Display pending approval page.
    
    Shown to users after registration while waiting for admin approval.
    """
    return render(request, 'accounts/pending_approval.html')


def logout_view(request):
    """
    Log out the current user and redirect to homepage.
    """
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح')
    return redirect('home:home')


@login_required
def profile_view(request):
    """
    Display user profile with recent orders.
    """
    from orders.models import Order
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    return render(request, 'accounts/profile.html', {
        'recent_orders': recent_orders
    })


@login_required
def update_profile(request):
    """
    Update user profile information and profile image.
    """
    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, instance=request.user)
        # Handle profile fields if they exist, otherwise create/get profile
        profile = getattr(request.user, 'profile', None)
        profile_form = ProfileImageForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'تم تحديث معلوماتك بنجاح')
            return redirect('accounts:profile')
    else:
        user_form = ProfileUpdateForm(instance=request.user)
        # Create profile if not exists
        profile = getattr(request.user, 'profile', None)
        profile_form = ProfileImageForm(instance=profile)
    
    return render(request, 'accounts/update_profile.html', {
        'form': user_form,
        'profile_form': profile_form
    })


def sync_cart_on_login(request):
    """
    Sync cart from localStorage to database on login.
    
    This function is called from JavaScript after successful authentication.
    The actual sync logic is handled client-side via AJAX.
    """
    pass


@require_POST
def set_theme(request):
    """
    Set user theme preference (light/dark) in session.
    """
    try:
        data = json.loads(request.body)
        theme = data.get('theme', 'theme-light')
        
        if theme in ['theme-light', 'theme-dark']:
            request.session['theme'] = theme
            return JsonResponse({'success': True, 'theme': theme})
        
        return JsonResponse({'success': False, 'error': 'Invalid theme'}, status=400)
    except:
        return JsonResponse({'success': False, 'error': 'Bad request'}, status=400)


@require_POST
def set_language(request):
    """
    Set user language preference (Arabic/English) in session.
    """
    try:
        data = json.loads(request.body)
        language = data.get('language', 'ar')
        
        if language in ['ar', 'en']:
            request.session['language'] = language
            return JsonResponse({'success': True, 'language': language})
        
        return JsonResponse({'success': False, 'error': 'Invalid language'}, status=400)
    except:
        return JsonResponse({'success': False, 'error': 'Bad request'}, status=400)


def get_theme(request):
    """
    Get current theme preference from session.
    """
    theme = request.session.get('theme', 'theme-light')
    return JsonResponse({'theme': theme})


def get_language(request):
    """
    Get current language preference from session.
    """
    language = request.session.get('language', 'ar')
    return JsonResponse({'language': language})
