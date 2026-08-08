from django.shortcuts import render
from products.models import Category
from .models import HomeSlide

from django.core.cache import cache
import logging
logger = logging.getLogger(__name__)


CACHE_KEY_ALL_CATEGORIES = "categories:all"

def home(request):
    """Home page view"""

    categories = cache.get(CACHE_KEY_ALL_CATEGORIES)

    if categories is None:
        categories = list(Category.objects.all())
        cache.set(CACHE_KEY_ALL_CATEGORIES, categories, 60 * 15)

    slides = list(HomeSlide.objects.filter(is_active=True))

    return render(request, 'home/home.html', {
        'categories': categories,
        'slides': slides,
    })

def faq(request):
    """FAQ page view for SEO"""
    return render(request, 'home/faq.html')
