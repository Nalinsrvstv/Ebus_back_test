# Generated by Django 4.2.6 on 2024-03-21 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0040_alter_datatable_doctype'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenario',
            name='created_by',
            field=models.CharField(blank=True, null=True),
        ),
    ]