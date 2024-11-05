# Generated by Django 4.2.6 on 2023-10-28 19:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_remove_datatable_doc_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='datatable',
            name='created_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='datatable',
            name='doc_data',
            field=models.JSONField(default={}),
        ),
        migrations.AddField(
            model_name='datatable',
            name='doc_name',
            field=models.TextField(default=None, max_length=100),
        ),
    ]