from django.core.cache import cache
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from products.models import (
    Product, Category, ProductVariant, Size, VariantAttributeValue,
    VariantAttribute, VariantSize, ProductSize,
)
import logging
from urllib.parse import unquote
from django.db.models import Prefetch
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

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
        return redirect('products:all_categories')


@never_cache
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
            Prefetch(
                'size_prices',
                queryset=VariantSize.objects.select_related('size').prefetch_related('images'),
            ),
            'images',
        )
        product = get_object_or_404(
            Product.objects.prefetch_related(
                'additional_images',
                Prefetch('variants', queryset=variants_qs),
                Prefetch(
                    'size_prices',
                    queryset=ProductSize.objects.select_related('size').prefetch_related('images').order_by('size__order'),
                ),
            ),
            slug=slug
        )

        # صور المنتج مرتبة
        product_images = product.additional_images.all().order_by('order')

        # الحصول على الأنماط من Prefetch المرتب مسبقًا
        variants = product.variants.all()  # already prefetch_related & ordered

        direct_size_prices = list(product.size_prices.all())
        variants_data = []
        variant_images_data = {}
        for variant in variants:
            color = variant.color
            variant_images = [
                {'url': image.image.url, 'alt': variant.name}
                for image in variant.images.all() if image.image
            ]
            if not variant_images and variant.image:
                variant_images = [{'url': variant.image.url, 'alt': variant.name}]
            variant_images_data[str(variant.pk)] = variant_images
            variants_data.append({
                'id': variant.pk,
                'name': variant.name,
                'order': variant.order,
                'pcsCarton': variant.pcs_carton,
                'isAvailable': variant.is_available,
                'colorId': color.pk if color else None,
                'colorName': color.value if color else '',
                'colorHex': color.hex_code if color and color.hex_code else '',
                'lengthLabel': variant.get_length_label(),
                'sizePrices': [
                    {
                        'sizeId': size_price.size_id,
                        'sizeName': size_price.size.name,
                        'pcsCarton': size_price.pcs_carton,
                        'supportsCarton': size_price.pcs_carton is not None,
                        'images': [
                            {'url': image.image.url, 'alt': f'{variant.name} - {size_price.size.name}'}
                            for image in size_price.images.all() if image.image
                        ],
                    }
                    for size_price in variant.size_prices.all()
                ],
                'image': variant.image.url if variant.image else '',
                'attributeType': 'color' if color else 'text',
                'variantName': variant.name,
            })

        product_images_data = []
        if product.image:
            product_images_data.append({'url': product.image.url, 'alt': product.name})
        product_images_data.extend(
            {'url': image.image.url, 'alt': product.name}
            for image in product_images if image.image
        )

        product_page_data = {
            'product': {
                'id': product.pk,
                'name': product.name,
                'image': product.image.url if product.image else '',
                'pcsCarton': product.pcs_carton,
                'hasSizes': bool(direct_size_prices),
                'lengthLabel': product.get_length_label(),
                'cartonQuantityUrl': reverse(
                    'products:product_carton_quantity', args=[product.slug]
                ),
            },
            'directSizePrices': [
                {
                    'sizeId': size_price.size_id,
                    'sizeName': size_price.size.name,
                    'pcsCarton': size_price.pcs_carton,
                    'supportsCarton': size_price.pcs_carton is not None,
                    'images': [
                        {'url': image.image.url, 'alt': f'{product.name} - {size_price.size.name}'}
                        for image in size_price.images.all() if image.image
                    ],
                }
                for size_price in direct_size_prices
            ],
            'variants': variants_data,
            'variantImages': variant_images_data,
            'productImages': product_images_data,
        }

        # المنتجات المرتبطة بنفس القسم
        related_products = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id).select_related('category').order_by('order')[:4]

        return render(request, 'products/product_detail.html', {
            'product': product,
            'product_images': product_images,
            'variants': variants,
            'related_products': related_products,
            'direct_size_prices': direct_size_prices,
            'product_page_data': product_page_data,
        })

    except Http404:
        messages.error(request, 'المنتج غير موجود')
        return redirect('products:all_categories')
    except Exception as e:
        logger.error(f'Error loading product detail for slug {slug}: {str(e)}', exc_info=True)
        messages.error(request, 'حدث خطأ أثناء تحميل تفاصيل المنتج. يرجى المحاولة لاحقاً')
        return redirect('products:all_categories')


@require_GET
@never_cache
def product_carton_quantity(request, slug):
    """Return the authoritative carton quantity for one product/variant size."""
    product = get_object_or_404(Product, slug=slug, is_available=True)
    try:
        size_id = int(request.GET.get('size_id', ''))
        if size_id < 1:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({'error': 'المقاس غير صحيح'}, status=400)

    variant_id = request.GET.get('variant_id')
    if variant_id:
        try:
            variant_id = int(variant_id)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'النمط غير صحيح'}, status=400)
        size_price = get_object_or_404(
            VariantSize.objects.select_related('size'),
            variant_id=variant_id,
            variant__product=product,
            variant__is_available=True,
            size_id=size_id,
        )
    else:
        size_price = get_object_or_404(
            ProductSize.objects.select_related('size'),
            product=product,
            size_id=size_id,
        )

    response = JsonResponse({
        'product_id': product.pk,
        'variant_id': variant_id or None,
        'size_id': size_price.size_id,
        'size_name': size_price.size.name,
        'length_label': (
            size_price.variant.get_length_label()
            if variant_id
            else product.get_length_label()
        ),
        'pcs_carton': size_price.pcs_carton,
        'supports_carton': size_price.pcs_carton is not None,
    })
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response
