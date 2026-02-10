from django.shortcuts import render
from products.models import Category

from django.core.cache import cache


CACHE_KEY_ALL_CATEGORIES = "categories:all"

def home(request):
    """Home page view"""

    categories = cache.get(CACHE_KEY_ALL_CATEGORIES)

    if categories is None:
        categories = list(Category.objects.all())
        cache.set(CACHE_KEY_ALL_CATEGORIES, categories, 60 * 15)

    return render(request, 'home/home.html', {
        'categories': categories
    })

def faq(request):
    """FAQ page view for SEO"""
    return render(request, 'home/faq.html')
