from django.core.management.base import BaseCommand
import csv
from main.utils import calculate_distance


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Read depot data from CSV
        with open("main/resources/base_depots.csv", "r") as file:
            depot_data = list(csv.reader(file))
            if len(depot_data) > 1:
                depot_data = depot_data[1:]

        # Read terminal data from CSV
        with open("main/resources/base_terminals.csv", "r") as file:
            terminal_data = list(csv.reader(file))
            if len(terminal_data) > 1:
                terminal_data = terminal_data[1:]

        # Specify paths for CSV files
        depot_terminal_path = "main/resources/depot_terminal_matrix.csv"
        terminal_depot_path = "main/resources/terminal_depot_matrix.csv"

        # Check if the data lists are empty
        if not depot_data or not terminal_data:
            print("No data found in one or both of the CSV files.")
            return

        # Check existing depot-terminal distances in CSV file
        existing_depot_terminal_distances = set()
        with open(depot_terminal_path, "r") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                existing_depot_terminal_distances.add(
                    (row[0], row[4])
                )  # Depot ID, Terminal ID

        # Calculate and write distances from depots to terminals
        with open(depot_terminal_path, mode="a", newline="") as depot_terminal_file:
            depot_terminal_writer = csv.writer(depot_terminal_file)

            for depot_row in depot_data:
                depot_id, depot_name, d_latitude, d_longitude, *_ = depot_row
                for terminal_row in terminal_data:
                    terminal_id, terminal_name, t_latitude, t_longitude, *_ = (
                        terminal_row
                    )

                    # Check if the distance already exists in CSV file
                    if (depot_id, terminal_id) in existing_depot_terminal_distances:
                        print(
                            f"Distance from {depot_name} to {terminal_name} already exists in the CSV."
                        )
                        continue

                    distance = calculate_distance(
                        float(d_latitude),
                        float(d_longitude),
                        float(t_latitude),
                        float(t_longitude),
                    )
                    depot_terminal_writer.writerow(
                        [
                            depot_id,
                            depot_name,
                            d_latitude,
                            d_longitude,
                            terminal_id,
                            terminal_name,
                            t_latitude,
                            t_longitude,
                            distance,
                        ]
                    )
                    print(
                        f"Distance calculated from {depot_name} to {terminal_name}: {distance} km"
                    )
                    existing_depot_terminal_distances.add((depot_id, terminal_id))

        # Check existing terminal-depot distances in CSV file
        existing_terminal_depot_distances = set()
        with open(terminal_depot_path, "r") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                existing_terminal_depot_distances.add(
                    (row[0], row[4])
                )  # Terminal ID, Depot ID

        # Calculate and write distances from terminals to depots
        with open(terminal_depot_path, mode="a", newline="") as terminal_depot_file:
            terminal_depot_writer = csv.writer(terminal_depot_file)

            for terminal_row in terminal_data:
                terminal_id, terminal_name, t_latitude, t_longitude, *_ = terminal_row
                for depot_row in depot_data:
                    depot_id, depot_name, d_latitude, d_longitude, *_ = depot_row

                    # Check if the distance already exists in CSV file
                    if (terminal_id, depot_id) in existing_terminal_depot_distances:
                        print(
                            f"Distance from {terminal_name} to {depot_name} already exists in the CSV."
                        )
                        continue

                    distance = calculate_distance(
                        float(t_latitude),
                        float(t_longitude),
                        float(d_latitude),
                        float(d_longitude),
                    )
                    terminal_depot_writer.writerow(
                        [
                            terminal_id,
                            terminal_name,
                            t_latitude,
                            t_longitude,
                            depot_id,
                            depot_name,
                            d_latitude,
                            d_longitude,
                            distance,
                        ]
                    )
                    print(
                        f"Distance calculated from {terminal_name} to {depot_name}: {distance} km"
                    )
                    existing_terminal_depot_distances.add((terminal_id, depot_id))
