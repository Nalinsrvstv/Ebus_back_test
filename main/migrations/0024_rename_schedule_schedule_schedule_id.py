# Generated by Django 4.2.6 on 2023-12-26 08:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_terminal_schedule_depot'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schedule',
            old_name='schedule',
            new_name='schedule_id',
        ),
    ]
