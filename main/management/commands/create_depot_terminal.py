import csv
from django.core.management.base import BaseCommand
from main.models import Depot, Terminal


class Command(BaseCommand):
    help = "Create Depot and Terminal instances from CSV files"

    def handle(self, *args, **kwargs):
        with open("main/resources/base_depots.csv", "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                (
                    depot_id,
                    depot_name,
                    latitude,
                    longitude,
                    capacity,
                    operator,
                    ac_non_ac,
                    brt_non_brt,
                    fuel_type,
                    service_type,
                    bus_type,
                ) = row
                Depot.objects.create(
                    depot_id=depot_id,
                    depot_name=depot_name,
                    latitude=latitude,
                    longitude=longitude,
                    capacity=capacity,
                    operator=operator,
                    ac_non_ac=ac_non_ac,
                    brt_non_brt=brt_non_brt,
                    fuel_type=fuel_type,
                    service_type=service_type,
                    bus_type=bus_type,
                )

        with open("main/resources/base_terminals.csv", "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                terminal_id, terminal_name, latitude, longitude, terminal_area = row
                Terminal.objects.create(
                    terminal_id=terminal_id,
                    terminal_name=terminal_name,
                    latitude=latitude,
                    longitude=longitude,
                    terminal_area=terminal_area,
                )
