# Generated by Django 4.2.6 on 2023-10-27 18:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='name',
            new_name='project_name',
        ),
        migrations.AddField(
            model_name='project',
            name='created_by',
            field=models.CharField(default=None),
        ),
        migrations.AddField(
            model_name='project',
            name='created_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
    ]
