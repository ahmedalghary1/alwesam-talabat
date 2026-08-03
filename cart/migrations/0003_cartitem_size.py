from django.db import migrations, models
import django.db.models.deletion


def populate_cart_item_sizes(apps, schema_editor):
    CartItem = apps.get_model('cart', 'CartItem')
    ProductSize = apps.get_model('products', 'ProductSize')
    VariantSize = apps.get_model('products', 'VariantSize')

    for item in CartItem.objects.exclude(size_name='').iterator():
        if item.variant_id:
            size_ids = VariantSize.objects.filter(
                variant_id=item.variant_id,
                size__name=item.size_name,
            ).values_list('size_id', flat=True)[:2]
        else:
            size_ids = ProductSize.objects.filter(
                product_id=item.product_id,
                size__name=item.size_name,
            ).values_list('size_id', flat=True)[:2]
        size_ids = list(size_ids)
        if len(size_ids) == 1:
            item.size_id = size_ids[0]
            item.save(update_fields=['size'])


class Migration(migrations.Migration):
    dependencies = [
        ('cart', '0002_alter_cart_options_alter_cartitem_options'),
        ('products', '0010_sync_product_variant_and_size_schema'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='size',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='cart_items',
                to='products.size',
            ),
        ),
        migrations.RunPython(populate_cart_item_sizes, migrations.RunPython.noop),
    ]
