from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0005_orderitem_length_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='is_length_only',
            field=models.BooleanField(default=False, verbose_name='بيع بالطول مباشرة وقت الطلب'),
        ),
    ]
