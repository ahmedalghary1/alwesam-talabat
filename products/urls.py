from django.urls import path 
from . import views

app_name = 'products'



urlpatterns = [
    path('', views.all_categories, name='all_categories'),
    path('search/', views.search_products, name='search'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('product/<str:slug>/', views.product_detail, name='product_detail'),
]