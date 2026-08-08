from django.db import migrations, models


def convert_blank_emails_to_null(apps, schema_editor):
    CustomUser = apps.get_model('accounts', 'CustomUser')
    CustomUser.objects.filter(email='').update(email=None)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_customuser_phone'),
    ]

    operations = [
        migrations.RunPython(
            convert_blank_emails_to_null,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(
                blank=True,
                null=True,
                unique=True,
                verbose_name='البريد الإلكتروني',
            ),
        ),
    ]
