# Generated by Django 4.2.6 on 2023-11-04 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_alter_datatable_doc_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='datatable',
            name='docType',
            field=models.TextField(default=None, max_length=100),
        ),
    ]
