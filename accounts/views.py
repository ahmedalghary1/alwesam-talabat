from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import translation
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from .forms import SignupForm, LoginForm, ProfileUpdateForm
from .models import CustomUser
from cart.models import Cart, CartItem
from products.models import Product
from core.constants import LOGIN_RATE_LIMIT
import json
import logging

logger = logging.getLogger(__name__)


def signup_view(request):
    """تسجيل مستخدم جديد"""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Set user as inactive - requires admin approval
            user.is_active = False
            user.save()
            
            logger.info(f'New user registered (inactive): {user.email}')
            
            # Redirect to pending approval page (no auto-login)
            return redirect('accounts:pending_approval')
    else:
        form = SignupForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


@ratelimit(key='ip', rate=LOGIN_RATE_LIMIT, method='POST', block=True)
def login_view(request):
    """تسجيل دخول بالإيميل أو رقم الهاتف"""
    if request.method == 'POST':
        username_or_phone = request.POST.get('email')  # Field name is 'email' but accepts both
        password = request.POST.get('password')
        
        # Authenticate using email or phone (custom backend handles both)
        user = authenticate(request, username=username_or_phone, password=password)
        
        if user is not None:
            # Check if user account is active
            if not user.is_active:
                logger.warning(f'Login attempt for inactive user: {user.email}')
                messages.warning(request, 'حسابك في انتظار موافقة المسؤول. سيتم إشعارك عند تفعيل حسابك.')
                return render(request, 'accounts/login.html', {'form': LoginForm()})
            
            login(request, user)
            logger.info(f'User {user.email} logged in successfully')
            
            # مزامنة السلة
            sync_cart_on_login(request)
            
            messages.success(request, f'مرحباً {user.username}!')
            next_url = request.GET.get('next', 'home:home')
            return redirect(next_url)
        else:
            logger.warning(f'Failed login attempt for: {username_or_phone}')
            messages.error(request, 'البريد الإلكتروني/رقم الهاتف أو كلمة المرور غير صحيحة')
    
    form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def pending_approval_view(request):
    """صفحة انتظار الموافقة"""
    return render(request, 'accounts/pending_approval.html')


def logout_view(request):
    """تسجيل خروج"""
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح')
    return redirect('home:home')


@login_required
def profile_view(request):
    """عرض الملف الشخصي"""
    from orders.models import Order
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    return render(request, 'accounts/profile.html', {
        'recent_orders': recent_orders
    })


@login_required
def update_profile(request):
    """تحديث معلومات المستخدم"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث معلوماتك بنجاح')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/update_profile.html', {'form': form})


def sync_cart_on_login(request):
    """مزامنة السلة من localStorage عند تسجيل الدخول"""
    # هذه الدالة يتم استدعاؤها من JavaScript
    pass


@require_POST
def set_theme(request):
    """تعيين الثيم (فاتح/داكن) في الجلسة"""
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
    """تعيين اللغة في الجلسة"""
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
    """الحصول على الثيم الحالي"""
    theme = request.session.get('theme', 'theme-light')
    return JsonResponse({'theme': theme})


def get_language(request):
    """الحصول على اللغة الحالية"""
    language = request.session.get('language', 'ar')
    return JsonResponse({'language': language})
