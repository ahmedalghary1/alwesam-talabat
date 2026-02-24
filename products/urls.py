from django.urls import path, re_path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.all_categories, name='all_categories'),
    path('search/', views.search_products, name='search'),

    # يدعم slug عربي وانجليزي بدون مشاكل
    re_path(
        r'^category/(?P<slug>[-\wء-ي]+)/$',
        views.category_products,
        name='category_products'
    ),

    re_path(
        r'^product/(?P<slug>[-\wء-ي]+)/$',
        views.product_detail,
        name='product_detail'
    ),
]