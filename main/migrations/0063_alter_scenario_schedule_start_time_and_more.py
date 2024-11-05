# Generated by Django 4.2.6 on 2024-08-23 22:38

from django.db import migrations, models
import django.db.models.deletion
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0062_designebusscenario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scenario_schedule',
            name='start_time',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='scenario_schedule',
            name='travel_time',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='scenario_schedule',
            name='trip_number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='DepotAllocationScenario',
            fields=[
                ('scenario_id', models.AutoField(primary_key=True, serialize=False)),
                ('scenario_name', models.CharField(blank=True, null=True)),
                ('description', models.CharField(blank=True, null=True)),
                ('depot_requestdata', picklefield.fields.PickledObjectField(blank=True, editable=False, null=True)),
                ('depot_result', picklefield.fields.PickledObjectField(blank=True, editable=False, null=True)),
                ('project_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='depot_allocation_scenario', to='main.project')),
            ],
        ),
        migrations.CreateModel(
            name='DepotAllocation_Schedule',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('schedule_id', models.CharField(blank=True, null=True)),
                ('trip_number', models.IntegerField(blank=True, null=True)),
                ('route_number', models.CharField(blank=True, null=True)),
                ('direction', models.CharField(blank=True, null=True)),
                ('start_terminal', models.CharField(blank=True, null=True)),
                ('end_terminal', models.CharField(blank=True, null=True)),
                ('start_time', models.IntegerField(blank=True, null=True)),
                ('travel_time', models.IntegerField(blank=True, null=True)),
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
                ('scenario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='depotallocation_schedule', to='main.depotallocationscenario')),
            ],
        ),
    ]