# Generated by Django 4.2.6 on 2024-10-17 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0063_alter_scenario_schedule_start_time_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectiveFunctions',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('object_value', models.FloatField(blank=True, null=True)),
                ('project_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='_objectfunction', to='main.project')),
            ],
        ),
    ]