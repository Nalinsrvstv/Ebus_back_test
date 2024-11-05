# Generated by Django 4.2.6 on 2024-05-23 18:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0052_busmodel_chargermodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='TerminalSummary',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('base_no_of_chargers', models.IntegerField(null=True)),
                ('charger_model_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='terminal_summaries', to='main.chargermodel')),
                ('terminal_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='terminal_summaries', to='main.terminal')),
            ],
        ),
        migrations.CreateModel(
            name='DepotTerminalMap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('depot_summary_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='depot_terminal_sum', to='main.depot')),
                ('terminal_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='depot_terminal_sum', to='main.terminal')),
            ],
        ),
        migrations.CreateModel(
            name='DepotSummary',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('base_no_of_chargers', models.IntegerField(null=True)),
                ('bus_model_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='depot_summaries', to='main.busmodel')),
                ('charger_model_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='depot_summaries', to='main.chargermodel')),
                ('depot_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='depot_summaries', to='main.depot')),
            ],
        ),
    ]