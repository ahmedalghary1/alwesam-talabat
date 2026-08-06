from django.urls import path
from . import admin_views

app_name = 'admin_app'

urlpatterns = [
    path('dashboard/', admin_views.admin_dashboard, name='dashboard'),
    path('products/', admin_views.admin_products, name='admin_products'),
    path('products/add/', admin_views.admin_product_add, name='admin_product_add'),
    path('products/<int:product_id>/edit/', admin_views.admin_product_edit, name='admin_product_edit'),
    path(
        'products/<int:product_id>/images/<int:image_id>/delete/',
        admin_views.admin_product_image_delete,
        name='admin_product_image_delete',
    ),
    path(
        'products/<int:product_id>/variant-images/<int:image_id>/delete/',
        admin_views.admin_variant_image_delete,
        name='admin_variant_image_delete',
    ),
    path('products/<int:product_id>/delete/', admin_views.admin_product_delete, name='admin_product_delete'),
    path('categories/', admin_views.admin_categories, name='admin_categories'),
    path('categories/add/', admin_views.admin_category_add, name='admin_category_add'),
    path('categories/<int:category_id>/edit/', admin_views.admin_category_edit, name='admin_category_edit'),
    path('categories/<int:category_id>/delete/', admin_views.admin_category_delete, name='admin_category_delete'),
    path('orders/', admin_views.admin_orders, name='admin_orders'),
    path('orders/<int:order_id>/', admin_views.admin_order_detail, name='admin_order_detail'),
    # User Management
    path('users/pending/', admin_views.admin_pending_users, name='pending_users'),
    path('users/', admin_views.admin_all_users, name='all_users'),
    path('users/export/excel/', admin_views.admin_export_users_excel, name='export_users_excel'),
    path('users/<int:user_id>/approve/', admin_views.admin_approve_user, name='approve_user'),
    path('users/<int:user_id>/reject/', admin_views.admin_reject_user, name='reject_user'),
    path('users/<int:user_id>/toggle/', admin_views.admin_toggle_user_status, name='toggle_user_status'),
]
