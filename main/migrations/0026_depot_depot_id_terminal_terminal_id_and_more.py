# Generated by Django 4.2.6 on 2023-12-26 10:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_alter_schedule_project_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='depot',
            name='depot_id',
            field=models.CharField(null=True),
        ),
        migrations.AddField(
            model_name='terminal',
            name='terminal_id',
            field=models.CharField(null=True),
        ),
        migrations.AlterField(
            model_name='depot',
            name='project_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.project'),
        ),
        migrations.AlterField(
            model_name='terminal',
            name='project_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.project'),
        ),
    ]
