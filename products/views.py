from django.core.cache import cache
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from products.models import Product, Category , ProductVariant , Size,VariantAttributeValue , VariantAttribute , VariantSize
import logging
from urllib.parse import unquote
from django.db.models import Prefetch

logger = logging.getLogger(__name__)


def search_products(request):
    """
    Search products by name, description, or category.
    Returns search results page with matching products.
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('products:all_categories')
    
    products = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query) |
        Q(category__name__icontains=query)
    ).distinct().order_by('order')
    
    return render(request, 'products/search_results.html', {
        'products': products,
        'query': query,
        'count': products.count()
    })


CACHE_KEY_ALL_CATEGORIES = "categories:all"

def all_categories(request):
    try:
        categories = cache.get(CACHE_KEY_ALL_CATEGORIES)

        if categories is None:
            categories = list(Category.objects.all().order_by('order'))
            cache.set(CACHE_KEY_ALL_CATEGORIES, categories, 60 * 15)

        return render(request, 'products/all_categories.html', {
            'categories': categories
        })

    except Exception as e:
        logger.exception("Error loading categories")
        messages.error(request, 'حدث خطأ أثناء تحميل الأقسام')
        return redirect('home:home')



def category_products(request, slug):
    """Display products in a specific category"""
    try:
        category = get_object_or_404(Category, slug=slug)
        products = Product.objects.filter(category=category).order_by('order')
        
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
        messages.error(request, e)
        return redirect('products:all_categories')


def product_detail(request, slug):
    """
    Display product details with variants and related products.
    Args:
        slug: Product URL slug
    Returns:
        Product detail page with images, variants, and related items
    """
    try:
        # تحسين استعلامات قاعدة البيانات مع ترتيب الأنماط والأطوال والألوان
        variants_qs = ProductVariant.objects.filter(is_available=True).order_by('order').prefetch_related(
            Prefetch('sizes', queryset=Size.objects.all().order_by('order')),
            Prefetch('attributes', queryset=VariantAttributeValue.objects.select_related('attribute')),
            Prefetch('size_prices', queryset=VariantSize.objects.select_related('size'))  # جديد
        )
        product = get_object_or_404(
            Product.objects.prefetch_related(
                'additional_images',
                Prefetch('variants', queryset=variants_qs)
            ),
            slug=slug
        )

        # صور المنتج مرتبة
        product_images = product.additional_images.all().order_by('order')

        # الحصول على الأنماط من Prefetch المرتب مسبقًا
        variants = product.variants.all()  # already prefetch_related & ordered

        # المنتجات المرتبطة بنفس القسم
        related_products = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id).select_related('category').order_by('order')[:4]

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
        messages.error(request, 'حدث خطأ أثناء تحميل تفاصيل المنتج. يرجى المحاولة لاحقاً')
        messages.error(request, e)
        return redirect('products:all_categories')
