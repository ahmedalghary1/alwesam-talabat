"""
Django Sitemaps Configuration
إعدادات Sitemap لمحركات البحث
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Product, Category


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['home:home', 'products:all_categories']

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    """Sitemap for product categories"""
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Category.objects.all()

    def lastmod(self, obj):
        # Return the last modification time if you have a field for it
        return None

    def location(self, obj):
        return f'/products/category/{obj.slug}/'


class ProductSitemap(Sitemap):
    """Sitemap for products"""
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Product.objects.filter(is_available=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/products/{obj.slug}/'
