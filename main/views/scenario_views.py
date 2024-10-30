from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from ..serializer import (
    GetAllScenariosSerializer,
    CreateScenarioSerializer,
    ScheduleSerializer,
    DepotSerializer,
    TerminalSerializer,
    ScenarioSerializer,
    UpdateScenarioSerializer,
    ScenarioDeleteSerializer,
    IsOutdatedSerializer
)
from rest_framework import status
from ..models import (
    Project,
    Schedule,
    Depot,
    DistanceMatrix,
    Terminal,
    Scenario,
    Scenario_Schedule,
    DepotTerminalDistanceMatrix,
    TerminalDepotDistanceMatrix,
)
from ..utils import (
    print_warning_message_in_red,
    calculate_existing_data,
    calculate_optimized_data,
    format_decimal,
    fetch_distance_matrices
)
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from collections import defaultdict
from ..halfdead import optimize_deadkm
import traceback


class ListScenario(APIView):
    def get(self, request, *args, **kwargs):
        params = {
            "project_id": request.GET.get("project_id"),
            "pageNumber": request.GET.get("pageNumber"),
            "pageSize": request.GET.get("pageSize"),
        }
        serializer_class = GetAllScenariosSerializer(data=params)
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            project_id = params["project_id"]
            try:
                # scenarios = list(Scenario.objects)
                scenarios = (
                    Scenario.objects.filter(project_id=project_id)
                    .order_by("-scenario_id")
                    .values()
                )
                paginator = Paginator(scenarios, params["pageSize"])
                page = paginator.page(params["pageNumber"])

                return Response(
                    {
                        "status": True,
                        "total_scenarios": paginator.count,
                        "message": "Scenario list",
                        "scenarios": list(page),
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                # Convert exception message to string
                error_message = str(e)
                return Response(
                    {"message": error_message}, status=status.HTTP_404_NOT_FOUND
                )


class CreateScenarioView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = CreateScenarioSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                projectDetails = request.data.get("projectDetails")
                scenario_name = request.data.get("scenario_name")
                description = request.data.get("description")

                project_id = projectDetails.get("project_id")
                project_name = projectDetails.get("project_name")
                created_by = projectDetails.get("created_by")

                # Retrieve the project details
                project = Project.objects.get(
                    project_id=project_id,
                    created_by=created_by,
                    project_name=project_name,
                )

                # Fetch depot data
                depots = Depot.objects.filter(project_id=project)
                depot_data = {
                    depot.depot_id: DepotSerializer(depot).data for depot in depots
                }

                # Fetch terminal data
                terminals = Terminal.objects.filter(project_id=project)
                terminal_data = {
                    terminal.terminal_id: TerminalSerializer(terminal).data
                    for terminal in terminals
                }

                location_map = {}
                for depot in depots:
                    location_map[depot.depot_name] = depot.depot_id

                for terminal in terminals:
                    location_map[terminal.terminal_name] = terminal.terminal_id

                depot_id_to_name_map = {}
                for depot in depots:
                    depot_id_to_name_map[depot.depot_id] = depot.depot_name

                # Fetch schedule data
                schedules = Schedule.objects.filter(project_id=project)

                # Serialize schedule data
                schedule_data = ScheduleSerializer(schedules, many=True).data

                # Group records based on schedule id and sort data within each group by trip_number
                grouped_records = defaultdict(list)
                for record in schedule_data:
                    grouped_records[record["schedule_id"]].append(record)

                # Organize schedule data
                organized_schedule_data = {}
                for schedule_id, records in grouped_records.items():
                    if len(records) < 2:
                        err_msg = (
                            "ERROR: there should be atleast two records for a schedule"
                        )
                        print(err_msg, schedule_id)
                        raise Exception(err_msg + " schedule_id: " + schedule_id)

                    sorted_records = sorted(
                        records, key=lambda x: int(x["trip_number"])
                    )

                    start_record = sorted_records[0]
                    end_record = sorted_records[-1]

                    # to convert the names to ids
                    start_record["start_terminal"] = location_map.get(
                        start_record["start_terminal"]
                    )
                    start_record["end_terminal"] = location_map.get(
                        start_record["end_terminal"]
                    )
                    end_record["start_terminal"] = location_map.get(
                        end_record["start_terminal"]
                    )
                    end_record["end_terminal"] = location_map.get(
                        end_record["end_terminal"]
                    )
                    
                    for record in sorted_records:
                        record["depot_id"] = location_map.get(record["depot_id"], record["depot_id"])

                    organized_schedule_data[schedule_id] = {
                        "start_shuttle": start_record,
                        "end_shuttle": end_record,
                    }

                # Calculate distance matrix with depot and terminal names
                is_outdated, depotTerminalDist, terminaldepotDist = (
                    fetch_distance_matrices(depots, terminals)
                )

                exclns = request.data.get("exclusions")
                assignPrefer = request.data.get("assignmentPreferences")
                
                # Creating a new dictionary to hold the response data
                data = {
                    "project_details": projectDetails,
                    "schedule_data": organized_schedule_data,
                    "depot_data": depot_data,
                    "terminal_data": terminal_data,
                    "depot_terminal_matrix": depotTerminalDist,
                    "terminal_depot_matrix": terminaldepotDist,
                    "exclusions": exclns,
                    "assignment_preferences": assignPrefer,
                }

                formatted_data = []

                result, feasibility_status, feasibility_check = optimize_deadkm(data)

                if feasibility_status != 1:
                    return Response(
                        {
                            "status": True,
                            "message": "solution infeasible",
                            "feasibility_status": feasibility_status,
                            "feasibility_check": feasibility_check,
                            "is_outdated": is_outdated,
                        },
                        status=status.HTTP_200_OK,
                    )

                for item in result:
                    item_dict = {
                        "Schedule": item[0],
                        "Depot": depot_id_to_name_map.get(item[1]),
                    }
                    formatted_data.append(item_dict)

                # Create and save the Scenario instance with the formatted data
                scenario = Scenario.objects.create(
                    scenario_name=scenario_name,
                    description=description,
                    result=formatted_data,
                    project_id=project,
                    exclusions=exclns,
                    assignment_preferences=assignPrefer,
                )

                # Create Scenario_Schedule instances and replace fields with scenario result
                self.create_scenario_schedules(scenario, schedules, formatted_data)

                # Return the formatted_data dictionary as the response
                response_data = (ScenarioSerializer(scenario).data,)

                return Response(
                    {
                        "status": True,
                        "message": "scenario created",
                        "scenario": response_data,
                        "feasibility_status": feasibility_status,
                        "feasibility_check": feasibility_check,
                        "is_outdated": is_outdated,
                    },
                    status=status.HTTP_200_OK,
                )

        except ObjectDoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # added for debugging purpose
            traceback.print_exc()
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create_scenario_schedules(self, scenario, schedules, formatted_data):
        scenario_to_depot_map = {}
        for item in formatted_data:
            schedule_id = item["Schedule"]
            allocated_depot_id = item["Depot"]

            scenario_to_depot_map[schedule_id] = allocated_depot_id

        for schedule in schedules:
            start_terminal = schedule.start_terminal
            end_terminal = schedule.end_terminal
            allocated_depot_id = schedule.depot_id
            if schedule.schedule_id in scenario_to_depot_map:
                allocated_depot_id = scenario_to_depot_map.get(schedule.schedule_id)
                if schedule.start_terminal == schedule.depot_id:
                    start_terminal = allocated_depot_id
                    end_terminal = schedule.end_terminal
                elif schedule.end_terminal == schedule.depot_id:
                    start_terminal = schedule.start_terminal
                    end_terminal = allocated_depot_id
                else:
                    start_terminal = schedule.start_terminal
                    end_terminal = schedule.end_terminal

            # Create Scenario_Schedule instances and replace fields with scenario result
            Scenario_Schedule.objects.create(
                scenario=scenario,
                project_id=schedule.project_id,
                schedule_id=schedule.schedule_id,
                trip_number=schedule.trip_number,
                route_number=schedule.route_number,
                direction=schedule.direction,
                start_terminal=start_terminal,
                end_terminal=end_terminal,
                start_time=schedule.start_time,
                travel_time=schedule.travel_time,
                trip_distance=schedule.trip_distance,
                crew_id=schedule.crew_id,
                event_type=schedule.event_type,
                operator=schedule.operator,
                ac_non_ac=schedule.ac_non_ac,
                brt_non_brt=schedule.brt_non_brt,
                service_type=schedule.service_type,
                fuel_type=schedule.fuel_type,
                bus_type=schedule.bus_type,
                depot_id=allocated_depot_id,
            )

    # old function
    def fetch_distance(self, depots, terminals):
        depot_names = {depot.depot_name: depot.depot_id for depot in depots}
        terminal_names = {
            terminal.terminal_name: terminal.terminal_id for terminal in terminals
        }

        depotTerminalDist = defaultdict(dict)
        terminalDepotDist = defaultdict(dict)

        # Fetch distances from DepotTerminalMatrix
        for depot_name in depot_names:
            distances = DepotTerminalDistanceMatrix.objects.filter(
                depot__depot_name=depot_name
            )
            for distance in distances:
                terminal_name = distance.terminal.terminal_name
                if terminal_name in terminal_names:
                    depotTerminalDist[depot_names[depot_name]][
                        terminal_names[terminal_name]
                    ] = {"distance": distance.distance}

        # Fetch distances from TerminalDepotMatrix
        for terminal_name in terminal_names:
            distances = TerminalDepotDistanceMatrix.objects.filter(
                terminal__terminal_name=terminal_name
            )
            for distance in distances:
                depot_name = distance.depot.depot_name
                if depot_name in depot_names:
                    terminalDepotDist[terminal_names[terminal_name]][
                        depot_names[depot_name]
                    ] = {"distance": distance.distance}

        return depotTerminalDist, terminalDepotDist


class DeadKmVisualOptimizeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = CreateScenarioSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_details = request.data.get("projectDetails")
            project_id = project_details.get("project_id")
            created_by = project_details.get("created_by")
            project_name = project_details.get("project_name")
            scenario_id = request.data.get("scenario_id")

            # Retrieve the project details
            project = Project.objects.get(
                project_id=project_id, created_by=created_by, project_name=project_name
            )

            # Calculate existing and optimized dead kilometers data
            existing_data, totalDeadkm_init, existing_route_data = (
                calculate_existing_data(project)
            )
            optimized_data, totalDeadkm_optmzd, optimized_route_data = (
                calculate_optimized_data(project, scenario_id)
            )

            # Calculate the difference between existing and optimized deadKm of depots
            diff = []
            for existing_item, optimized_item in zip(existing_data, optimized_data):
                deadKm_diff = (
                    existing_item["DeadKilometers"] - optimized_item["DeadKilometers"]
                )
                diff.append(
                    {
                        "depot_name": existing_item["depot_name"],
                        "depot_id": existing_item["depot_id"],
                        "deadKmDiff": deadKm_diff,
                    }
                )
            sorted_diff = sorted(diff, key=lambda x: x["deadKmDiff"], reverse=True)

            # Response of total deadKm of overall depots
            total_dead_km_response = {
                "ExistingTotalDeadKm": totalDeadkm_init,
                "OptimizedTotalDeadKm": totalDeadkm_optmzd,
                "PercentageReduction": (totalDeadkm_init - totalDeadkm_optmzd)
                / totalDeadkm_init,
            }

            # Response of the allocation of schedules for route_numbers
            route_data_response = {
                "ExistingRouteData": existing_route_data,
                "OptimizedRouteData": optimized_route_data,
            }

            # Final response including all the deadKm visualization data
            deadKm_init_optimized = {
                "ExistingData": existing_data,
                "OptimizedData": optimized_data,
                "DifferenceDeadKm": sorted_diff,
                "TotalDeadKm": total_dead_km_response,
                "RouteAllocationData": route_data_response,
            }
            return Response(deadKm_init_optimized, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeadKmScenarioCompareView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = CreateScenarioSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_details = request.data.get("projectDetails")
            project_id = project_details.get("project_id")
            created_by = project_details.get("created_by")
            project_name = project_details.get("project_name")
            scenario_ids = request.data.get("scenario_ids")

            # Check if at least 2 scenario IDs are provided
            if len(scenario_ids) < 2:
                return Response(
                    {"error": "At least 2 scenario IDs are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Retrieve the project details
            project = Project.objects.get(
                project_id=project_id, created_by=created_by, project_name=project_name
            )

            # Calculate data for each scenario
            scenario_data = []
            for scenario_id in scenario_ids:
                data = self.calculate_scenario_data(project, scenario_id)
                scenario_data.append(data)

            return Response(scenario_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def calculate_scenario_data(self, project, scenario_id):
        existing_data, totalDeadkm_init, existing_route_data = calculate_existing_data(
            project
        )
        optimized_data, totalDeadkm_optmzd, optimized_route_data = (
            calculate_optimized_data(project, scenario_id)
        )

        # Calculate the difference between existing and optimized deadKm of depots
        diff = []
        for existing_item, optimized_item in zip(existing_data, optimized_data):
            deadKm_diff = (
                existing_item["DeadKilometers"] - optimized_item["DeadKilometers"]
            )
            diff.append(
                {
                    "depot_name": existing_item["depot_name"],
                    "depot_id": existing_item["depot_id"],
                    "deadKmDiff": deadKm_diff,
                }
            )

        # Response of total deadKm of overall depots
        total_dead_km_response = {
            "ExistingTotalDeadKm": totalDeadkm_init,
            "OptimizedTotalDeadKm": totalDeadkm_optmzd,
            "PercentageReduction": (totalDeadkm_init - totalDeadkm_optmzd)
            / totalDeadkm_init,
        }

        # Response of the allocation of schedules for route_numbers
        route_data_response = {
            "ExistingRouteData": existing_route_data,
            "OptimizedRouteData": optimized_route_data,
        }

        # Final response including all the deadKm visualization data
        scenario_visualization_data = {
            "ScenarioID": scenario_id,
            "ExistingData": existing_data,
            "OptimizedData": optimized_data,
            "DifferenceDeadKm": diff,
            "TotalDeadKm": total_dead_km_response,
            "RouteAllocationData": route_data_response,
        }

        return scenario_visualization_data


class UpdateScenarioView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = UpdateScenarioSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            scenario_name = serializer_class.validated_data["name"]
            description = serializer_class.validated_data["description"]
            scenario_id = serializer_class.validated_data["scenario_id"]

            try:
                existing_scenario = Scenario.objects.get(scenario_id=scenario_id)
                existing_scenario.scenario_name = scenario_name
                existing_scenario.description = description

                existing_scenario.save()

                return Response(
                    {"status": True, "message": "scenario updated"},
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                return Response(
                    {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


class DeleteScenarioView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = ScenarioDeleteSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            scenario_id = serializer_class.validated_data["scenario_id"]

            # Check if the scenario exists
            scenario = Scenario.objects.get(scenario_id=scenario_id)

            existing_scenario_Data = Scenario_Schedule.objects.filter(scenario=scenario)

            # Delete the scenario and related scenario schedules
            scenario.delete()
            existing_scenario_Data.delete()

            return Response(
                {"status": True, "message": "Scenario and Scenario_data deleted"},
                status=status.HTTP_200_OK,
            )

        except Scenario.DoesNotExist:
            return Response(
                {"status": False, "message": "Scenario not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CheckIsOutdatedView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = IsOutdatedSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = request.data.get("project_id")
            project_name = request.data.get("project_name")
            created_by = request.data.get("created_by")

            # Retrieve the project details
            project = Project.objects.get(
                project_id=project_id,
                created_by=created_by,
                project_name=project_name,
            )

            # Fetch depot data
            depots = Depot.objects.filter(project_id=project)

            # Fetch terminal data
            terminals = Terminal.objects.filter(project_id=project)

            # Calculate distance matrix with depot and terminal names
            is_outdated ,depotTerminalDist, terminalDepotDist = (
                fetch_distance_matrices(depots, terminals)
            )

            if is_outdated:
                return Response(
                    {
                        "status": True,
                        "message": "Distance matrix is outdated",
                        "is_outdated": is_outdated,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "status": True,
                        "message": "Distance matrix is updated",
                        "is_outdated": is_outdated,
                    },
                    status=status.HTTP_200_OK,
                )

        except ObjectDoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # added for debugging purpose
            traceback.print_exc()
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
