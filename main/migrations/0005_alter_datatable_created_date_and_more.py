# Generated by Django 4.2.6 on 2023-10-28 19:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_project_project_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datatable',
            name='created_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='datatable',
            name='doc_data',
            field=models.DateTimeField(),
        ),
    ]
