from django.urls import path , register_converter
from . import views

app_name = 'products'

class UnicodeSlugConverter:
    regex = '[\w-]+'  # يشمل العربية واللاتينية والأرقام والشرطات
    def to_python(self, value):
        return value
    def to_url(self, value):
        return value

register_converter(UnicodeSlugConverter, 'uslug')

urlpatterns = [
    path('', views.all_categories, name='all_categories'),
    path('search/', views.search_products, name='search'),
    path('category/<uslug:slug>/', views.category_products, name='category_products'),
    path('product/<str:slug>/', views.product_detail, name='product_detail'),
]