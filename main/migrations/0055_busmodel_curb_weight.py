# Generated by Django 4.2.6 on 2024-06-03 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_alter_depotterminalmap_depot_summary_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='busmodel',
            name='curb_weight',
            field=models.FloatField(null=True),
        ),
    ]
