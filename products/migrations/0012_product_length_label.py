from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0011_productsizeimage_variantsizeimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='length_label',
            field=models.CharField(
                blank=True,
                default='',
                help_text='مثال: الطول، مقاس السلك، طول الإصبع. يترك فارغاً لاستخدام كلمة المقاس.',
                max_length=50,
                verbose_name='اسم خيار الطول/المقاس',
            ),
        ),
    ]
