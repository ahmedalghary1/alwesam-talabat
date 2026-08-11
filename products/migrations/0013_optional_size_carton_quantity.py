from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0012_product_length_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productsize',
            name='pcs_carton',
            field=models.PositiveIntegerField(
                blank=True,
                default=None,
                help_text='اختياري. اتركه فارغاً إذا كان الخيار يباع بالطول مباشرة.',
                null=True,
                verbose_name='عدد القطع في الكرتونة',
            ),
        ),
        migrations.AlterField(
            model_name='variantsize',
            name='pcs_carton',
            field=models.PositiveIntegerField(
                blank=True,
                default=None,
                help_text='اختياري. اتركه فارغاً إذا كان الخيار يباع بالطول مباشرة.',
                null=True,
                verbose_name='عدد القطع في الكرتونة',
            ),
        ),
    ]
