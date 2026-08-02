import django.db.models.deletion
from django.db import migrations, models


def copy_existing_sizes(apps, schema_editor):
    Color = apps.get_model('products', 'Color')
    Product = apps.get_model('products', 'Product')
    ProductVariant = apps.get_model('products', 'ProductVariant')
    ProductSize = apps.get_model('products', 'ProductSize')
    VariantSize = apps.get_model('products', 'VariantSize')
    VariantAttribute = apps.get_model('products', 'VariantAttribute')
    VariantAttributeValue = apps.get_model('products', 'VariantAttributeValue')

    # Preserve the legacy color relation before its model/field are removed.
    color_attribute, _ = VariantAttribute.objects.get_or_create(name='لون')
    color_values = {}
    for color in Color.objects.all().iterator():
        value, _ = VariantAttributeValue.objects.get_or_create(
            attribute=color_attribute,
            value=color.name,
            defaults={'hex_code': color.hex_code},
        )
        if not value.hex_code and color.hex_code:
            value.hex_code = color.hex_code
            value.save(update_fields=['hex_code'])
        color_values[color.pk] = value.pk

    for variant in ProductVariant.objects.exclude(color_id=None).iterator():
        value_id = color_values.get(variant.color_id)
        if value_id:
            variant.attributes.add(value_id)

    product_links = []
    for product in Product.objects.all().iterator():
        product_links.extend(
            ProductSize(product_id=product.pk, size_id=size_id, pcs_carton=product.pcs_carton)
            for size_id in product.sizes.values_list('pk', flat=True)
        )
    ProductSize.objects.bulk_create(product_links, ignore_conflicts=True)

    variant_links = []
    for variant in ProductVariant.objects.all().iterator():
        variant_links.extend(
            VariantSize(variant_id=variant.pk, size_id=size_id, pcs_carton=variant.pcs_carton)
            for size_id in variant.sizes.values_list('pk', flat=True)
        )
    VariantSize.objects.bulk_create(variant_links, ignore_conflicts=True)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_alter_variantattributevalue_options_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='productvariant',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='code',
            field=models.CharField(
                blank=True,
                help_text='كود/SKU الخاص بالنمط',
                max_length=50,
                null=True,
                unique=True,
            ),
        ),
        migrations.CreateModel(
            name='ProductSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pcs_carton', models.PositiveIntegerField(default=24, verbose_name='عدد القطع في الكرتونة')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='size_prices', to='products.product')),
                ('size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_prices', to='products.size')),
            ],
            options={
                'verbose_name': 'مقاس المنتج المباشر',
                'verbose_name_plural': 'مقاسات المنتج المباشرة',
                'unique_together': {('product', 'size')},
            },
        ),
        migrations.CreateModel(
            name='VariantSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pcs_carton', models.PositiveIntegerField(default=24, verbose_name='عدد القطع في الكرتونة')),
                ('size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variant_prices', to='products.size')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='size_prices', to='products.productvariant')),
            ],
            options={
                'verbose_name': 'مقاس النمط',
                'verbose_name_plural': 'مقاسات النمط',
                'unique_together': {('variant', 'size')},
            },
        ),
        migrations.RunPython(copy_existing_sizes, migrations.RunPython.noop),
        migrations.RemoveField(model_name='product', name='sizes'),
        migrations.AddField(
            model_name='product',
            name='sizes',
            field=models.ManyToManyField(
                blank=True,
                help_text='أضف أطوال مباشرة إذا لم يكن للمنتج أنماط. يمكن تحديد الكمية لكل مقاس عبر الواجهة المخصصة.',
                related_name='products',
                through='products.ProductSize',
                through_fields=('product', 'size'),
                to='products.size',
                verbose_name='الأطوال المتاحة للمنتج',
            ),
        ),
        migrations.RemoveField(model_name='productvariant', name='sizes'),
        migrations.AddField(
            model_name='productvariant',
            name='sizes',
            field=models.ManyToManyField(
                blank=True,
                help_text='اختر المقاسات وحدد الكمية لكل مقاس عبر الواجهة المخصصة',
                related_name='variants',
                through='products.VariantSize',
                through_fields=('variant', 'size'),
                to='products.size',
                verbose_name='المقاسات المتاحة',
            ),
        ),
        migrations.RemoveField(model_name='productvariant', name='color'),
        migrations.RemoveField(model_name='productvariant', name='variant_type'),
        migrations.DeleteModel(name='Color'),
    ]
