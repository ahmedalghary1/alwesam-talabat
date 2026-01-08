
import os
import django
from django.template.loader import render_to_string
from django.test import RequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from products.models import Product, Category, ProductVariant

def verify_template_render():
    try:
        # Create dummy data
        category, _ = Category.objects.get_or_create(name="Test Category")
        product, _ = Product.objects.get_or_create(name="Test Product", category=category)
        
        variant_name = "Test Variant Length Label"
        length_label = "Wire Gauge Test"
        
        variant, _ = ProductVariant.objects.get_or_create(
            product=product,
            name=variant_name,
            defaults={
                'variant_type': 'color',
                'length_label': length_label
            }
        )
        variant.length_label = length_label
        variant.save()

        # Test base.html
        # rendered_base = render_to_string('base.html', context)
        # print("Base HTML rendered successfully")
        
        # Define context first
        request = RequestFactory().get('/')
        context = {
            'product': product,
            'variants': [variant],
            'request': request
        }

        # Test simple inheritance
        simple_template = """
        {% extends 'base.html' %}
        {% block content %}
        <h1>Test</h1>
        {% endblock %}
        """
        from django.template import Template, Context
        t = Template(simple_template)
        # Context() requires dict or nothing, but Template.render takes Context or dict (in newer Django)
        # In modern Django, render takes context dict directly usually?
        # Let's use simple render(context)
        ren = t.render(Context(context))
        print("Simple inheritance rendered successfully")
        
        rendered = render_to_string('products/product_detail.html', context)
        
        # Check for lengthLabel in JS object
        expected_js_substring = f"lengthLabel: '{length_label}'"
        
        if expected_js_substring in rendered:
            print(f"SUCCESS: Template rendered with '{expected_js_substring}'")
        else:
            print(f"FAILURE: Could not find '{expected_js_substring}' in rendered template.")
            # print(rendered) # Too long to print

        # Clean up
        variant.delete()
        product.delete()
        category.delete()

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    verify_template_render()
