from django.db import migrations, models
from django.db.models import Count


def reject_duplicate_phones(apps, schema_editor):
    CustomUser = apps.get_model('accounts', 'CustomUser')
    duplicate_count = CustomUser.objects.values('phone').annotate(
        users=Count('id'),
    ).filter(users__gt=1).count()
    if duplicate_count:
        raise RuntimeError(
            'Cannot make phone numbers unique: duplicate phone numbers exist. '
            'Resolve the duplicate accounts, then run migrate again.'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_customuser_options'),
    ]

    operations = [
        migrations.RunPython(
            reject_duplicate_phones,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.CharField(
                max_length=20,
                unique=True,
                verbose_name='رقم الهاتف',
            ),
        ),
    ]
