# Generated by Django 4.2.6 on 2023-10-28 19:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_remove_datatable_doc_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datatable',
            name='created_date',
        ),
    ]
