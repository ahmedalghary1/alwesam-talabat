from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from products.models import Product, Category
import logging

logger = logging.getLogger(__name__)


def search_products(request):
    """بحث في المنتجات"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('products:all_categories')
    
    products = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query) |
        Q(category__name__icontains=query)
    ).distinct()
    
    return render(request, 'products/search_results.html', {
        'products': products,
        'query': query,
        'count': products.count()
    })


def all_categories(request):
    """عرض جميع الأقسام"""
    try:
        categories = Category.objects.all()
        return render(request, 'products/all_categories.html', {
            'categories': categories
        })
    except Exception as e:
        messages.error(request, 'حدث خطأ أثناء تحميل الأقسام')
        return redirect('home:home')


def category_products(request, slug):
    """عرض منتجات قسم محدد"""
    try:
        category = get_object_or_404(Category, slug=slug)
        products = Product.objects.filter(category=category)
        
        return render(request, 'products/categories.html', {
            'category': category,
            'products': products
        })
    except Http404:
        messages.error(request, 'القسم غير موجود')
        return redirect('products:all_categories')
    except Exception as e:
        logger.error(f'Error loading category products for slug {slug}: {str(e)}', exc_info=True)
        # SECURITY: Don't expose internal error details to users
        messages.error(request, 'حدث خطأ أثناء تحميل المنتجات. يرجى المحاولة لاحقاً')
        return redirect('products:all_categories')


def product_detail(request, slug):
    """عرض تفاصيل منتج"""
    try:
        product = get_object_or_404(Product, slug=slug)
        
        # Get product images
        product_images = product.additional_images.all()
        
        # Get product variants with optimized queries
        variants = product.variants.filter(
            is_available=True
        ).select_related('color').prefetch_related('sizes')
        
        # منتجات ذات صلة (نفس القسم) - مع تحسين الأداء
        related_products = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id).select_related('category')[:4]
        
        return render(request, 'products/product_detail.html', {
            'product': product,
            'product_images': product_images,
            'variants': variants,
            'related_products': related_products
        })
    except Http404:
        messages.error(request, 'المنتج غير موجود')
        return redirect('products:all_categories')
    except Exception as e:
        logger.error(f'Error loading product detail for slug {slug}: {str(e)}', exc_info=True)
        # SECURITY: Don't expose internal error details to users
        messages.error(request, 'حدث خطأ أثناء تحميل تفاصيل المنتج. يرجى المحاولة لاحقاً')
        return redirect('products:all_categories')