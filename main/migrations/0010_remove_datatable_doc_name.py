# Generated by Django 4.2.6 on 2023-10-28 19:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_remove_datatable_created_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datatable',
            name='doc_name',
        ),
    ]
