# Generated by Django 4.2.6 on 2024-03-05 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_remove_depot_short_name_remove_depot_type_of_service_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='is_submitted',
            field=models.BooleanField(default=False),
        ),
    ]
