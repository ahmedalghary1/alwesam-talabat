
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from home.sitemaps import StaticViewSitemap, CategorySitemap, ProductSitemap
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Sitemaps configuration
sitemaps = {
    'static': StaticViewSitemap,
    'categories': CategorySitemap,
    'products': ProductSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('', include('products.urls')),

    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('cart/', include('cart.urls')),
    path('support/', include('support.urls')),  # Customer support
    path('admin-panel/', include('home.admin_urls')),  # Admin panel routes
    path('admin-panel/support/', include('support.admin_urls')),  # Support admin routes
    
    # REST API
    path('api/', include('api.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # SEO: Sitemap
    #path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    # SEO: Robots.txt
    #path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

# Serve media files in development
if settings.DEBUG:
    
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
