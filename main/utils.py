from django.db.models import Q
from .models import (
    Depot,
    Terminal,
    Schedule,
    Scenario,
    Scenario_Schedule,
    DistanceMatrix,
)
import openrouteservice
from decimal import Decimal
from collections import defaultdict

api_keys = [
    "5b3ce3597851110001cf62480eea0dff56474e318761a2f5ed35ba3c",  # Rohit's key
    "5b3ce3597851110001cf62485641e3aa26dc4ae99b922a40df232436",  # Tejaswini's key
]


def calculate_distance(from_lat, from_lon, to_lat, to_lon):
    for api_key in api_keys:
        try:
            # Call OpenRouteService API to calculate distance
            client = openrouteservice.Client(key=api_key)
            coords = ((from_lon, from_lat), (to_lon, to_lat))
            response = client.directions(
                coordinates=coords,
                profile="driving-car",
                units="km",  # specify units as kilometers
            )

            # Extract distance in kilometers from the response
            distance = response["routes"][0]["summary"]["distance"]
            return distance
        except openrouteservice.exceptions.ApiError as e:
            print(f"[ORS] error occurred while calculating distance: {e}")
            print(f"Trying with another API key: {e}")
            continue
        except Exception as e:
            print(f"An error occurred while calculating distance: {e}")
            return 0
    return 0


def calculate_existing_data(project):
    existing_data = []

    schedules = Schedule.objects.filter(
        Q(project_id=project) & Q(event_type="Non-revenue trip")
    )
    depots = Depot.objects.filter(project_id=project)
    terminals = Terminal.objects.filter(project_id=project)

    # Get unique route_numbers and NoOfSchedules
    existing_depot_route_data = {}

    for depot in depots:
        depot_route_schedules = schedules.filter(depot_id=depot.depot_name)
        depot_id = depot.depot_name
        depot_name = depot.depot_name
        existing_depot_route_data[depot_id] = {
            "depot_name": depot_name,
            "depot_id": depot.depot_id,
            "route_data": [],
        }

        route_numbers = set()

        for route in depot_route_schedules:
            route_number = route.route_number
            if route_number not in route_numbers:
                route_numbers.add(route_number)
                route_data = {"route_number": route_number, "NoOfSchedules": 0}

                # Count schedules for the route number
                route_schedules = depot_route_schedules.filter(
                    route_number=route_number
                )
                unique_schedule_ids = set()
                for schedule in route_schedules:
                    unique_schedule_ids.add(schedule.schedule_id)

                route_data["NoOfSchedules"] = len(unique_schedule_ids)
                existing_depot_route_data[depot_id]["route_data"].append(route_data)

    # Get the DeadKm for depots
    total_dead_km_init = 0

    for depot in depots:
        depot_data = {
            "depot_id": depot.depot_id,
            "depot_name": depot.depot_name,
            "NoOfSchedules": 0,
            "DeadKilometers": 0,
        }

        unique_schedule_ids = set()

        # Count schedules and calculate dead kilometers for the depot
        depot_schedules = schedules.filter(depot_id=depot.depot_name)

        for schedule in depot_schedules:
            unique_schedule_ids.add(schedule.schedule_id)

        depot_data["NoOfSchedules"] = len(unique_schedule_ids)
        depot_data["DeadKilometers"] = calculate_dead_km(
            depot_schedules, depots, terminals
        )

        # Sum of Total DeadKm of all the depots
        total_dead_km_init += depot_data["DeadKilometers"]

        existing_data.append(depot_data)

    return existing_data, total_dead_km_init, existing_depot_route_data


def calculate_optimized_data(project, scenario_id):
    optimized_data = []

    scenario = Scenario.objects.get(project_id=project, scenario_id=scenario_id)

    # Get schedules from the Scenario_Schedule model for the latest scenario
    scenario_schedules = Scenario_Schedule.objects.filter(
        Q(scenario_id=scenario)
        & Q(project_id=project)
        & Q(event_type="Non-revenue trip")
    )
    depots = Depot.objects.filter(project_id=project)
    terminals = Terminal.objects.filter(project_id=project)

    # Get unique route_numbers and NoOfSchedules
    optimized_depot_route_data = {}

    for depot in depots:
        depot_route_scenario_schedules = scenario_schedules.filter(
            depot_id=depot.depot_name
        )
        depot_id = depot.depot_name
        depot_name = depot.depot_name
        optimized_depot_route_data[depot_id] = {
            "depot_name": depot_name,
            "depot_id": depot.depot_id,
            "route_data": [],
        }

        route_numbers = set()

        for route in depot_route_scenario_schedules:
            route_number = route.route_number
            if route_number not in route_numbers:
                route_numbers.add(route_number)
                route_data = {"route_number": route_number, "NoOfSchedules": 0}

                # Count schedules for the route number
                route_schedules = depot_route_scenario_schedules.filter(
                    route_number=route_number
                )
                unique_schedule_ids = set()
                for schedule in route_schedules:
                    unique_schedule_ids.add(schedule.schedule_id)

                route_data["NoOfSchedules"] = len(unique_schedule_ids)
                optimized_depot_route_data[depot_id]["route_data"].append(route_data)

    # Get the DeadKm for depots
    total_dead_km_optimized = 0

    for depot in depots:
        depot_data = {
            "depot_id": depot.depot_id,
            "depot_name": depot.depot_name,
            "NoOfSchedules": 0,
            "DeadKilometers": 0,
        }

        unique_schedule_ids = set()

        # Count schedules and calculate dead kilometers for the depot
        depot_scenario_schedules = scenario_schedules.filter(depot_id=depot.depot_name)

        for schedule in depot_scenario_schedules:
            unique_schedule_ids.add(schedule.schedule_id)

        depot_data["NoOfSchedules"] = len(unique_schedule_ids)
        depot_data["DeadKilometers"] = calculate_dead_km(
            depot_scenario_schedules, depots, terminals
        )

        # Sum of Total DeadKm of all the depots
        total_dead_km_optimized += depot_data["DeadKilometers"]

        optimized_data.append(depot_data)

    return optimized_data, total_dead_km_optimized, optimized_depot_route_data


def calculate_dead_km(schedules, depots, terminals):

    depot_name_to_location_map = get_depot_name_to_location_map(depots)
    terminal_name_to_location_map = get_terminal_name_to_location_map(terminals)

    total_dead_km = 0

    grouped_records = defaultdict(list)
    for schedule in schedules:
        grouped_records[schedule.schedule_id].append(schedule)

    for schedule_id, records in grouped_records.items():
        if len(records) < 2:
            err_msg = "ERROR: there should be atleast two records for a schedule"
            print(err_msg, schedule_id)
            raise Exception(err_msg + " schedule_id: " + schedule_id)

        sorted_records = sorted(records, key=lambda x: int(x.trip_number))

        start_record = sorted_records[0]
        end_record = sorted_records[-1]

        start_dead_km = fetch_distance_from_depot_terminal_matrix(
            start_record.start_terminal,
            start_record.end_terminal,
            depot_name_to_location_map,
            terminal_name_to_location_map,
        )

        end_dead_km = fetch_distance_from_terminal_depot_matrix(
            end_record.start_terminal,
            end_record.end_terminal,
            depot_name_to_location_map,
            terminal_name_to_location_map,
        )

        total_dead_km += start_dead_km + end_dead_km

    # for schedule in schedules:
    #     # Get list of trip numbers for the current schedule ID
    #     trip_numbers = [
    #         int(s.trip_number)
    #         for s in schedules
    #         if s.schedule_id == schedule.schedule_id and s.trip_number.isdigit()
    #     ]

    #     min_trip_number = (
    #         min(trip_numbers) if trip_numbers else int(schedule.trip_number)
    #     )
    #     max_trip_number = (
    #         max(trip_numbers) if trip_numbers else int(schedule.trip_number)
    #     )

    #     # Calculate distances based on min and max trip numbers
    #     if int(schedule.trip_number) == min_trip_number:
    #         distance = fetch_distance_from_depot_terminal_matrix(
    #             schedule.start_terminal,
    #             schedule.end_terminal,
    #             depot_name_to_location_map,
    #             terminal_name_to_location_map,
    #         )
    #     elif int(schedule.trip_number) == max_trip_number:
    #         distance = fetch_distance_from_terminal_depot_matrix(
    #             schedule.start_terminal,
    #             schedule.end_terminal,
    #             depot_name_to_location_map,
    #             terminal_name_to_location_map,
    #         )
    #     else:
    #         distance = 0

    #     total_dead_km += distance

    return total_dead_km


def fetch_distance_from_depot_terminal_matrix(
    depot_name, terminal_name, depot_name_to_location_map, terminal_name_to_location_map
):
    depot_lat, depot_lon = depot_name_to_location_map[depot_name]
    terminal_lat, terminal_lon = terminal_name_to_location_map[terminal_name]

    distance_obj = DistanceMatrix.objects.filter(
        start_latitude=depot_lat,
        start_longitude=depot_lon,
        end_latitude=terminal_lat,
        end_longitude=terminal_lon,
    ).first()

    if distance_obj is not None:
        distance = distance_obj.distance
    else:
        distance = 0

    # distance = DepotTerminalDistanceMatrix.objects.get(
    #     depot__depot_name=depot_name, terminal__terminal_name=terminal_name
    # ).distance
    return distance


def fetch_distance_from_terminal_depot_matrix(
    terminal_name, depot_name, depot_name_to_location_map, terminal_name_to_location_map
):
    depot_lat, depot_lon = depot_name_to_location_map[depot_name]
    terminal_lat, terminal_lon = terminal_name_to_location_map[terminal_name]

    distance_obj = DistanceMatrix.objects.filter(
        start_latitude=terminal_lat,
        start_longitude=terminal_lon,
        end_latitude=depot_lat,
        end_longitude=depot_lon,
    ).first()

    if distance_obj is not None:
        distance = distance_obj.distance
    else:
        distance = 0

    # distance = TerminalDepotDistanceMatrix.objects.get(
    #     terminal__terminal_name=terminal_name, depot__depot_name=depot_name
    # ).distance
    return distance


def format_decimal(value, decimal_places=6):
    return round(Decimal(value), decimal_places)


def print_warning_message_in_red(message):
    RED = "\033[91m"
    RESET = "\033[0m"
    print(RED + message + RESET)


def get_depot_name_to_location_map(depots):
    depot_name_to_location = {
        depot.depot_name: (
            format_decimal(depot.latitude),
            format_decimal(depot.longitude),
        )
        for depot in depots
    }
    return depot_name_to_location


def get_terminal_name_to_location_map(terminals):
    terminal_name_to_location = {
        terminal.terminal_name: (
            format_decimal(terminal.latitude),
            format_decimal(terminal.longitude),
        )
        for terminal in terminals
    }
    return terminal_name_to_location


def fetch_distance_matrices(depots, terminals):
    depot_locations = {
        (
            format_decimal(depot.latitude),
            format_decimal(depot.longitude),
        ): depot.depot_id
        for depot in depots
    }

    terminal_locations = {
        (
            format_decimal(terminal.latitude),
            format_decimal(terminal.longitude),
        ): terminal.terminal_id
        for terminal in terminals
    }

    depotTerminalDist = defaultdict(dict)
    terminalDepotDist = defaultdict(dict)

    for (depot_lat, depot_lon), depot_id in depot_locations.items():
        for (
            terminal_lat,
            terminal_lon,
        ), terminal_id in terminal_locations.items():
            depotTerminalDist[depot_id][terminal_id] = {"distance": 0}

        distances = DistanceMatrix.objects.filter(
            start_latitude=depot_lat, start_longitude=depot_lon
        )

        for distance in distances:
            if distance.distance != 0:
                terminal_location = (distance.end_latitude, distance.end_longitude)
                if terminal_location in terminal_locations:
                    terminal_id = terminal_locations[terminal_location]
                    depotTerminalDist[depot_id][terminal_id] = {
                        "distance": distance.distance
                    }

    for (terminal_lat, terminal_lon), terminal_id in terminal_locations.items():
        for (depot_lat, depot_lon), depot_id in depot_locations.items():
            terminalDepotDist[terminal_id][depot_id] = {"distance": 0}

        distances = DistanceMatrix.objects.filter(
            start_latitude=terminal_lat, start_longitude=terminal_lon
        )

        for distance in distances:
            if distance.distance != 0:
                depot_location = (distance.end_latitude, distance.end_longitude)
                if depot_location in depot_locations:
                    depot_id = depot_locations[depot_location]
                    terminalDepotDist[terminal_id][depot_id] = {
                        "distance": distance.distance
                    }

    # check if the distance matrix still contain zero distances
    is_outdated = _is_outdated(depotTerminalDist, terminalDepotDist)

    if is_outdated:
        message = "WARNING: Distance Matrix is outdated, and can lead to incorrect results."
        print_warning_message_in_red(message)

    return is_outdated, depotTerminalDist, terminalDepotDist


def _is_outdated(depotTerminalDist, terminalDepotDist):
    flag = False

    # Check for zero distances in depotTerminalDist
    for depot in depotTerminalDist.values():
        for terminal in depot.values():
            if terminal["distance"] == 0:
                flag = True
                break
        if flag:
            break

    # Check for zero distances in terminalDepotDist
    for terminal in terminalDepotDist.values():
        for depot in terminal.values():
            if depot["distance"] == 0:
                flag = True
                break
        if flag:
            break

    return flag
