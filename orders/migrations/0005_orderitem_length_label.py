from django.db import migrations, models


def populate_length_labels(apps, schema_editor):
    OrderItem = apps.get_model('orders', 'OrderItem')
    for item in OrderItem.objects.select_related('variant', 'product').iterator():
        label = ''
        if item.variant_id:
            label = item.variant.length_label or ''
        if not label:
            label = getattr(item.product, 'length_label', '') or 'المقاس'
        item.length_label = label
        item.save(update_fields=['length_label'])


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0012_product_length_label'),
        ('orders', '0004_alter_orderitem_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='length_label',
            field=models.CharField(
                blank=True,
                default='',
                max_length=50,
                verbose_name='اسم خيار الطول/المقاس وقت الطلب',
            ),
        ),
        migrations.RunPython(populate_length_labels, migrations.RunPython.noop),
    ]
