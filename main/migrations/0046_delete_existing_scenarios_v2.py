from django.db import migrations


def delete_data(apps, schema_editor):
    Scenario = apps.get_model("main", "Scenario")
    Scenario_Schedule = apps.get_model("main", "Scenario_Schedule")

    Scenario.objects.all().delete()
    Scenario_Schedule.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0045_alter_scenario_assignment_preferences_and_more"),
    ]

    operations = [
        migrations.RunPython(delete_data),
    ]
