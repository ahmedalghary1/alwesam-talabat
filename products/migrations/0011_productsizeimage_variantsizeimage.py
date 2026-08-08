from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_sync_product_variant_and_size_schema'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductSizeImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/product-sizes/')),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product_size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.productsize')),
            ],
            options={'ordering': ['order', 'created_at']},
        ),
        migrations.CreateModel(
            name='VariantSizeImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/variant-sizes/')),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('variant_size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.variantsize')),
            ],
            options={'ordering': ['order', 'created_at']},
        ),
    ]
