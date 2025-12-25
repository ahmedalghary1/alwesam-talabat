from django.shortcuts import render
from products.models import Category


def home(request):
    """الصفحة الرئيسية - عرض الأقسام"""
    categories = Category.objects.all()[:10]  # أول 10 أقسام
    return render(request, 'home/home.html', {
        'categories': categories
    })
