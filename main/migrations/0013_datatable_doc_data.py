# Generated by Django 4.2.6 on 2023-10-28 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_remove_datatable_doc_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='datatable',
            name='doc_data',
            field=models.JSONField(default={}),
        ),
    ]
