# migrate_colors.py

import os
import django

# تأكد من أن Django جاهز
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")  # عدل اسم settings إذا مختلف
django.setup()

from products.models import VariantAttribute, VariantAttributeValue, Color, ProductVariant

# إنشاء نوع خاصية "لون"
color_attr, _ = VariantAttribute.objects.get_or_create(name="لون")

# نقل كل لون وربطه بالـ variants
for color in Color.objects.all():
    value, _ = VariantAttributeValue.objects.get_or_create(
        attribute=color_attr,
        value=color.name,
        defaults={"hex_code": color.hex_code}
    )

    variants = ProductVariant.objects.filter(color=color)
    for variant in variants:
        variant.attributes.add(value)

print("Migration completed successfully.")