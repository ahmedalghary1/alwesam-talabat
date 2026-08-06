from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_sync_orderitem_carton_snapshot'),
        ('products', '0010_sync_product_variant_and_size_schema'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to='products.product',
            ),
        ),
    ]
