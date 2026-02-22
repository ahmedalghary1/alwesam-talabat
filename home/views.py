from django.shortcuts import render
from products.models import Category

import logging
logger = logging.getLogger(__name__)



def home(request):
    """Home page view"""


    categories = list(Category.objects.all())

    return render(request, 'home/home.html', {
        'categories': categories
    })

def faq(request):
    """FAQ page view for SEO"""
    return render(request, 'home/faq.html')
