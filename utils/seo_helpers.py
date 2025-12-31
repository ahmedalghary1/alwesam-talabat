"""
SEO Helper Functions
دوال مساعدة لتحسين محركات البحث
"""
import json
from django.utils.safestring import mark_safe


def generate_product_schema(product):
    """
    Generate Product Schema Markup (JSON-LD)
    إنشاء Schema Markup للمنتج
    """
    schema = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": product.name,
        "description": product.description if product.description else f"{product.name} - متوفر بالجملة من الوسام",
        "sku": str(product.id),
        "brand": {
            "@type": "Brand",
            "name": "الوسام"
        },
        "offers": {
            "@type": "Offer",
            "priceCurrency": "EGP",
            "availability": "https://schema.org/InStock" if product.is_available else "https://schema.org/OutOfStock",
            "itemCondition": "https://schema.org/NewCondition",
            "seller": {
                "@type": "Organization",
                "name": "الوسام طلبات"
            }
        },
        "additionalProperty": {
            "@type": "PropertyValue",
            "name": "القطع في الكرتونة",
            "value": str(product.pcs_carton)
        }
    }
    
    # Add image if available
    if product.image:
        schema["image"] = product.image.url
    
    # Add category if available
    if product.category:
        schema["category"] = product.category.name
    
    return mark_safe(json.dumps(schema, ensure_ascii=False, indent=2))


def generate_organization_schema(request):
    """
    Generate Organization/LocalBusiness Schema Markup
    إنشاء Schema Markup للأعمال المحلية
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": request.build_absolute_uri('/'),
        "name": "الوسام - أدوات كهربائية بالجملة",
        "alternateName": "Alwesam Electrical Wholesale",
        "description": "موزع معتمد للأدوات والمستلزمات الكهربائية بالجملة في مصر. أسعار تنافسية للتجار، توصيل سريع، منتجات أصلية مضمونة.",
        "image": request.build_absolute_uri('/static/images/ELWSAM.png'),
        "logo": request.build_absolute_uri('/static/images/ELWSAM.png'),
        "url": request.build_absolute_uri('/'),
        "telephone": "01001252900",
        "priceRange": "جملة",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "شارع مستجد ١٢ والجمال",
            "addressLocality": "المطرية",
            "addressRegion": "الدقهلية",
            "addressCountry": "EG"
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": "31.1656",
            "longitude": "31.4913"
        },
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Saturday",
                    "Sunday"
                ],
                "opens": "09:00",
                "closes": "18:00"
            }
        ],
        "sameAs": [
            "https://www.facebook.com/people/Elwsam-Electric/61575621072046/",
            "https://wa.me/201001252900",
            "https://www.instagram.com/elwsamelectric/"
        ]
    }
    
    return mark_safe(json.dumps(schema, ensure_ascii=False, indent=2))


def generate_breadcrumb_schema(breadcrumbs):
    """
    Generate BreadcrumbList Schema Markup
    إنشاء Schema Markup لمسار التنقل
    
    Args:
        breadcrumbs: list of dicts with 'name' and 'url' keys
        Example: [
            {'name': 'الرئيسية', 'url': '/'},
            {'name': 'الأقسام', 'url': '/products/'},
            {'name': 'كابلات كهربائية', 'url': '/products/category/cables/'}
        ]
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": []
    }
    
    for index, crumb in enumerate(breadcrumbs, start=1):
        schema["itemListElement"].append({
            "@type": "ListItem",
            "position": index,
            "name": crumb['name'],
            "item": crumb['url']
        })
    
    return mark_safe(json.dumps(schema, ensure_ascii=False, indent=2))


def generate_faq_schema(faq_list):
    """
    Generate FAQ Schema Markup
    إنشاء Schema Markup للأسئلة الشائعة
    
    Args:
        faq_list: list of dicts with 'question' and 'answer' keys
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    }
    
    for faq in faq_list:
        schema["mainEntity"].append({
            "@type": "Question",
            "name": faq['question'],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq['answer']
            }
        })
    
    return mark_safe(json.dumps(schema, ensure_ascii=False, indent=2))


def get_meta_description(page_type, **kwargs):
    """
    Generate optimized meta descriptions
    توليد وصف meta محسّن
    """
    templates = {
        'home': 'الوسام - موزع معتمد للأدوات والمستلزمات الكهربائية بالجملة في مصر. أسعار تنافسية للتجار، توصيل سريع، منتجات أصلية مضمونة. اطلب الآن!',
        'category': 'تسوق {category_name} بالجملة بأفضل الأسعار في مصر. جودة عالية، توريد للمحلات والمقاولين. احصل على عرض سعر مخصص الآن!',
        'product': 'اشتري {product_name} بالجملة بأفضل الأسعار في مصر. {pcs_carton} قطعة/كرتون. جودة عالية، توصيل سريع. اطلب الآن!',
        'all_categories': 'تصفح جميع أقسام الأدوات الكهربائية بالجملة من الوسام. منتجات أصلية، أسعار تنافسية، خدمة ممتازة. اطلب الآن!',
    }
    
    template = templates.get(page_type, '')
    return template.format(**kwargs) if template else ''


def get_page_title(page_type, **kwargs):
    """
    Generate optimized page titles
    توليد عنوان صفحة محسّن
    """
    templates = {
        'home': 'الوسام - أدوات كهربائية بالجملة | مستلزمات كهرباء للتجار في مصر 2025',
        'category': '{category_name} بالجملة | أسعار مميزة للتجار - الوسام',
        'product': '{product_name} بالجملة | أسعار مميزة للتجار - الوسام',
        'all_categories': 'جميع الأقسام - أدوات كهربائية بالجملة | الوسام',
    }
    
    template = templates.get(page_type, 'الوسام طلبات')
    return template.format(**kwargs) if template else 'الوسام طلبات'
