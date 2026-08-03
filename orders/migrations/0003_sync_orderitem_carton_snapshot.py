from django.db import migrations, models


def ensure_pcs_carton_column(apps, schema_editor):
    """Add the snapshot column unless an older deployment added it manually."""
    OrderItem = apps.get_model('orders', 'OrderItem')
    table_name = OrderItem._meta.db_table
    with schema_editor.connection.cursor() as cursor:
        columns = {
            column.name
            for column in schema_editor.connection.introspection.get_table_description(
                cursor, table_name
            )
        }
    if 'pcs_carton' in columns:
        return

    field = models.PositiveIntegerField(
        default=24,
        verbose_name='عدد القطع في الكرتونة وقت الطلب',
    )
    field.set_attributes_from_name('pcs_carton')
    field.model = OrderItem
    schema_editor.add_field(OrderItem, field)


def copy_legacy_carton_quantity(apps, schema_editor):
    OrderItem = apps.get_model('orders', 'OrderItem')
    OrderItem.objects.filter(
        variant_pcs_carton__isnull=False,
    ).update(pcs_carton=models.F('variant_pcs_carton'))


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0002_alter_order_options_alter_orderitem_options'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    ensure_pcs_carton_column,
                    migrations.RunPython.noop,
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='orderitem',
                    name='pcs_carton',
                    field=models.PositiveIntegerField(
                        default=24,
                        verbose_name='عدد القطع في الكرتونة وقت الطلب',
                    ),
                ),
            ],
        ),
        migrations.RunPython(copy_legacy_carton_quantity, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='orderitem',
            name='variant_info',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='variant_pcs_carton',
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='color_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='size_name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
