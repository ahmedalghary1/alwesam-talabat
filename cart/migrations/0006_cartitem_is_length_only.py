from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0013_optional_size_carton_quantity'),
        ('cart', '0005_cartitem_length_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='is_length_only',
            field=models.BooleanField(default=False, verbose_name='يباع بالطول مباشرة'),
        ),
    ]
