# Generated by Django 4.2.6 on 2024-04-06 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_delete_existing_scenarios'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scenario',
            name='assignment_preferences',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='exclusions',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='result',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
