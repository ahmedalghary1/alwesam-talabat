from django.db import migrations, models


def populate_carton_snapshots(apps, schema_editor):
    CartItem = apps.get_model('cart', 'CartItem')
    ProductSize = apps.get_model('products', 'ProductSize')
    VariantSize = apps.get_model('products', 'VariantSize')

    for item in CartItem.objects.select_related('product', 'variant').iterator():
        pcs_carton = None
        if item.variant_id:
            if item.size_id:
                pcs_carton = VariantSize.objects.filter(
                    variant_id=item.variant_id,
                    size_id=item.size_id,
                ).values_list('pcs_carton', flat=True).first()
            if pcs_carton is None:
                pcs_carton = item.variant.pcs_carton
        else:
            if item.size_id:
                pcs_carton = ProductSize.objects.filter(
                    product_id=item.product_id,
                    size_id=item.size_id,
                ).values_list('pcs_carton', flat=True).first()
            if pcs_carton is None:
                pcs_carton = item.product.pcs_carton

        CartItem.objects.filter(pk=item.pk).update(
            pcs_carton_snapshot=max(1, pcs_carton or 24),
        )


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_cartitem_size'),
        ('products', '0010_sync_product_variant_and_size_schema'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='pcs_carton_snapshot',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.RunPython(
            populate_carton_snapshots,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='pcs_carton_snapshot',
            field=models.PositiveIntegerField(
                default=0,
                verbose_name='عدد القطع في الكرتونة وقت الإضافة للسلة',
            ),
        ),
    ]
