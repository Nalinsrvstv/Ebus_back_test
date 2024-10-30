# Generated by Django 4.2.6 on 2024-05-09 02:59

from django.db import migrations
import csv
from main.models import (
    Depot,
    Terminal,
    DepotTerminalDistanceMatrix,
    TerminalDepotDistanceMatrix,
    DistanceMatrix,
)


def populate_distance_data(apps, schema_editor):
    # Specify paths for CSV files
    depot_terminal_path = "main/resources/depot_terminal_matrix.csv"
    terminal_depot_path = "main/resources/terminal_depot_matrix.csv"

    # Get counts of terminals and depots
    no_of_terminals = Terminal.objects.filter(project_id_id__isnull=True).count()
    no_of_depots = Depot.objects.filter(project_id_id__isnull=True).count()

    # Read data from depotTerminalMatrix.csv
    with open(depot_terminal_path, "r") as file:
        depot_terminal_data = list(csv.reader(file))[1:]  # Skip header

        # Create or update instances of DepotTerminalMatrix model and save to database
        for row in depot_terminal_data:
            depot_id, _, _, _, terminal_id, _, _, _, distance = row

            # Find the corresponding depot and terminal objects
            try:
                depot = Depot.objects.get(depot_id=depot_id, project_id_id__isnull=True)
                terminal = Terminal.objects.get(
                    terminal_id=terminal_id, project_id_id__isnull=True
                )

                # Create or update DepotTerminalDistanceMatrix instance
                DepotTerminalDistanceMatrix.objects.update_or_create(
                    depot_id=depot.id,
                    terminal_id=terminal.id,
                    defaults={"distance": distance},
                )

                # Create or update DistanceMatrix instance
                DistanceMatrix.objects.update_or_create(
                    start_latitude=depot.latitude,
                    start_longitude=depot.longitude,
                    end_latitude=terminal.latitude,
                    end_longitude=terminal.longitude,
                    distance=distance,
                )
            except (Depot.DoesNotExist, Terminal.DoesNotExist) as e:
                print(f"Error: {e}, Depot ID: {depot_id}, Terminal ID: {terminal_id}")

    # Check count of depot terminal distance records
    depot_terminal_count = DepotTerminalDistanceMatrix.objects.count()
    expected_depot_terminal_count = no_of_terminals * no_of_depots
    if depot_terminal_count != expected_depot_terminal_count:
        raise ValueError(
            f"Depot terminal distance records count mismatch. Expected {expected_depot_terminal_count}, found {depot_terminal_count}"
        )

    # Read data from terminalDepotMatrix.csv
    with open(terminal_depot_path, "r") as file:
        terminal_depot_data = list(csv.reader(file))[1:]  # Skip header

        # Create or update instances of TerminalDepotMatrix model and save to database
        for row in terminal_depot_data:
            terminal_id, _, _, _, depot_id, _, _, _, distance = row

            # Find the corresponding depot and terminal objects
            try:
                depot = Depot.objects.get(depot_id=depot_id, project_id_id__isnull=True)
                terminal = Terminal.objects.get(
                    terminal_id=terminal_id, project_id_id__isnull=True
                )

                # Create or update TerminalDepotDistanceMatrix instance
                TerminalDepotDistanceMatrix.objects.update_or_create(
                    terminal_id=terminal.id,
                    depot_id=depot.id,
                    defaults={"distance": distance},
                )

                # Create or update DistanceMatrix instance
                DistanceMatrix.objects.update_or_create(
                    start_latitude=terminal.latitude,
                    start_longitude=terminal.longitude,
                    end_latitude=depot.latitude,
                    end_longitude=depot.longitude,
                    distance=distance,
                )
            except (Depot.DoesNotExist, Terminal.DoesNotExist) as e:
                print(f"Error: {e}, Depot ID: {depot_id}, Terminal ID: {terminal_id}")

    # Check count of terminal depot distance records
    terminal_depot_count = TerminalDepotDistanceMatrix.objects.count()
    expected_terminal_depot_count = no_of_terminals * no_of_depots
    if terminal_depot_count != expected_terminal_depot_count:
        raise ValueError(
            f"Terminal depot distance records count mismatch. Expected {expected_terminal_depot_count}, found {terminal_depot_count}"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0050_distancematrix"),
    ]

    operations = [
        migrations.RunPython(populate_distance_data),
    ]
