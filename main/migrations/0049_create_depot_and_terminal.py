from django.db import migrations
from django.core.management import call_command


def create_depot_terminal(apps, schema_editor):
    # Call the management command to create Depot and Terminal instances
    call_command('create_depot_terminal')


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0048_alter_datatable_doctype_terminaldepotdistancematrix_and_more'),
    ]

    operations = [
        migrations.RunPython(create_depot_terminal),
    ]
