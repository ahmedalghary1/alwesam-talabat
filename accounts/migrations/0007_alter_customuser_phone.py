from django.db import migrations, models

import accounts.validators


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_make_email_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.CharField(
                max_length=20,
                unique=True,
                validators=[accounts.validators.validate_phone_number],
                verbose_name='رقم الهاتف',
            ),
        ),
    ]
