# Generated by Django 4.2.6 on 2023-12-26 15:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_rename_operator_depot_operator_alter_depot_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='depot',
            old_name='operator',
            new_name='operator1',
        ),
    ]
