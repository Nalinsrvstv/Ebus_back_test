# Generated by Django 4.2.6 on 2023-12-26 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_rename_operator_depot_operator1'),
    ]

    operations = [
        migrations.RenameField(
            model_name='depot',
            old_name='operator1',
            new_name='optor1',
        ),
    ]
