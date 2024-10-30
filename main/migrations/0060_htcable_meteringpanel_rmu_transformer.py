# Generated by Django 4.2.6 on 2024-08-08 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0059_alter_depot_capacity_alter_project_workflow_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HTCable',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cable_type', models.CharField(null=True)),
                ('voltage', models.IntegerField(null=True)),
                ('max_current_carrying_capacity', models.IntegerField(null=True)),
                ('total_cost', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MeteringPanel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('component_name', models.CharField(null=True)),
                ('voltage', models.IntegerField(null=True)),
                ('amount', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RMU',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('component_name', models.CharField(null=True)),
                ('specification', models.CharField(null=True)),
                ('voltage', models.IntegerField(null=True)),
                ('capacity_kva', models.IntegerField(null=True)),
                ('cost', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transformer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('transformer', models.CharField(null=True)),
                ('voltage', models.IntegerField(null=True)),
                ('capacity_kva', models.IntegerField(null=True)),
                ('total_cost', models.IntegerField(null=True)),
            ],
        ),
    ]
