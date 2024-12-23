# Generated by Django 4.2.6 on 2024-03-27 03:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0041_scenario_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datatable',
            name='docType',
            field=models.TextField(choices=[('Schedule', 'Schedule'), ('Depot', 'Depot'), ('Terminal', 'Terminal'), ('Scenario', 'Scenario'), ('Scenario_Schedule', 'Scenario_Schedule'), ('Discom_station', 'Dscmstn'), ('Ebus_schedule', 'Ebsscdl')], default=None, max_length=100),
        ),
        migrations.CreateModel(
            name='Scenario_Schedule',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('schedule_id', models.CharField(blank=True, null=True)),
                ('trip_number', models.CharField(blank=True, null=True)),
                ('route_number', models.CharField(blank=True, null=True)),
                ('direction', models.CharField(blank=True, null=True)),
                ('start_terminal', models.CharField(blank=True, null=True)),
                ('end_terminal', models.CharField(blank=True, null=True)),
                ('start_time', models.CharField(blank=True, null=True)),
                ('travel_time', models.CharField(blank=True, null=True)),
                ('trip_distance', models.FloatField(blank=True, null=True)),
                ('crew_id', models.CharField(blank=True, null=True)),
                ('event_type', models.CharField(blank=True, null=True)),
                ('operator', models.CharField(blank=True, null=True)),
                ('ac_non_ac', models.CharField(blank=True, null=True)),
                ('brt_non_brt', models.CharField(blank=True, null=True)),
                ('service_type', models.CharField(blank=True, null=True)),
                ('fuel_type', models.CharField(blank=True, null=True)),
                ('bus_type', models.CharField(blank=True, null=True)),
                ('depot_id', models.CharField(blank=True, null=True)),
                ('project_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.project')),
                ('scenario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scenario_schedule', to='main.scenario')),
            ],
        ),
    ]
