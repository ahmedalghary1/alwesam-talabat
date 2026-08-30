import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='customermessage',
            name='admin_user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='initiated_support_messages',
                to=settings.AUTH_USER_MODEL,
                verbose_name='المسؤول المرسل',
            ),
        ),
        migrations.AddField(
            model_name='customermessage',
            name='sent_by_admin',
            field=models.BooleanField(default=False, verbose_name='مرسلة من الإدارة'),
        ),
    ]
