from django.shortcuts import render
from products.models import Category


def home(request):
    """Home page view"""
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'home/home.html', context)


def faq(request):
    """FAQ page view for SEO"""
    return render(request, 'home/faq.html')
