from rest_framework.views import APIView
from rest_framework.response import Response
from ..serializer import (
    FileSerializer,
    ValidateFileSerializer,
    ProjectSummarySerializer,
    DepotSerializer,
    TerminalSerializer,
    ScenarioSchedulesDownloadSerializer,
    NewDepotTerminalUpdateSerializer,
    DepotTerminalSerializer,
    GetDepotsByIdSerializer,
    GetTerminalsByIdSerializer,
    BusModelSerializer,
    ChargerModelSerializer,
    DynamicPowerConsumptionSerializer,
    BusDeleteSerializer,
    ChargerDeleteSerializer,
    DynamicFileUploadSerializer,
    HistoryPowerConsumptionSerializer,
    CreateChargingScenarioSerializer,
    ChargingScenarioSerializer,
    ChargingAnalysisResultsSerializer,
    GetAllScenariosSerializer,
    ScenarioDeleteSerializer,
    SuggestedBusModelSerializer,
    ExistingDepotAllocationDataSerializer,
    GetDepotSerializer, GetScheduleSerializer, GetTerminalSerializer, GetSubstationSerializer,
    ProposedDepotAllocationSerializer,
    DepotAllocationScenarioSerializer,
    TransformerSerializer, HTCableSerializer, RMUSerializer, MeteringPanelSerializer, LTPanelSerializer,
    TransformerDeleteSerializer, HtCableDeleteSerializer, RMUDeleteSerializer, MeteringPanelDeleteSerializer, LTPanelDeleteSerializer,
    CompareScenarioSerializer,
    GetComponentsByDepotSerializer, CalculateDistanceAndTransformersSerializer,
    BatteryReplacementSerializer,
    SalvageCostEstimationSerializer,
    CreateDesignEbusScenarioSerializer,
    DesignEbusScenarioSerializer,
    UpdateScenarioSerializer,
    ProjectNameValidationSerializer, ScenarioNameValidationSerializer, SubmitProjectSerializer

)
from rest_framework import status
from ..models import (
    Project,
    Datatable,
    DistanceMatrix,
    Schedule,
    Depot,
    Terminal,
    Substation,
    Scenario,
    Scenario_Schedule,
    DepotTerminalDistanceMatrix,
    TerminalDepotDistanceMatrix,
    BusModel,
    ChargerModel,
    HistoryPowerConsumptionModel,
    PowerScenario,
    ChargingAnalysisScenario,
    Transformer, HTCable, RMU, MeteringPanel, LTPanel,
    DepotAllocationScenario,
    DepotAllocation_Schedule,
    DesignEbusScenario,
    ObjectiveFunctions
)
from main.utils import calculate_distance, format_decimal
from ..powerconsumption import get_pc_profile
from ..charge_max import run_algorithm
from ..data_analytics import data_analytics
from ..depot_allocation import ebus_depot_allocation
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
import csv
import base64
from ..filevalidate import schema
import jsonschema
from collections import defaultdict, Counter
from django.http import HttpResponse
import traceback
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from django.db.models import Q
import math
from decimal import Decimal, InvalidOperation


class FileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = FileSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            try:
                file = request.data["file"]
                filename = "test.csv"
                projectId = request.data["projectId"]
                # Step 1: Decode Base64 to bytes
                decoded_bytes = base64.b64decode(file)

                project = Project.objects.get(project_id=projectId)
                datatablerow = Datatable(
                    doc_id=project, doc_name=filename, doc_data=list(decoded_bytes)
                )
                datatablerow.save()

                return Response(
                    {"status": True, "message": "file uploaded and saved "},
                    status=status.HTTP_200_OK,
                )
            except Project.DoesNotExist:
                return Response(
                    {"status": False, "message": "Project not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )


class ValidateFile(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = ValidateFileSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            fileType = request.data["type"]
            fileData = request.data["fileData"]
            try:
                jsonschema.validate(fileData, schema[fileType])
                return Response(
                    {"status": True, "message": "file uploaded and saved "},
                    status=status.HTTP_200_OK,
                )

            except jsonschema.ValidationError as e:
                print(e)
                return Response(
                    {"status": True, "message": "file uploaded and saved "},
                    status=status.HTTP_200_OK,
                )


class ScenarioSchedulesDownload(APIView):
    def get(self, request, *args, **kwargs):
        serializer_class = ScenarioSchedulesDownloadSerializer(
            data=request.query_params
        )
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            scenario_id = serializer_class.validated_data["scenario_id"]

            scenario = Scenario.objects.get(scenario_id=scenario_id)

            scenario_schedules = Scenario_Schedule.objects.filter(scenario=scenario)

            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="{scenario_id}_{scenario.scenario_name}_scenario_schedules.csv"'
            )

            writer = csv.writer(response)
            writer.writerow(
                [
                    "Schedule ID",
                    "Trip Number",
                    "Route Number",
                    "Direction",
                    "Start Terminal",
                    "End Terminal",
                    "Start Time",
                    "Travel Time",
                    "Trip Distance",
                    "Crew ID",
                    "Event Type",
                    "Operator",
                    "AC/Non-AC",
                    "BRT/Non-BRT",
                    "Service Type",
                    "Fuel Type",
                    "Bus Type",
                    "Depot ID",
                ]
            )
            for schedule in scenario_schedules:
                writer.writerow(
                    [
                        schedule.schedule_id,
                        schedule.trip_number,
                        schedule.route_number,
                        schedule.direction,
                        schedule.start_terminal,
                        schedule.end_terminal,
                        schedule.start_time,
                        schedule.travel_time,
                        schedule.trip_distance,
                        schedule.crew_id,
                        schedule.event_type,
                        schedule.operator,
                        schedule.ac_non_ac,
                        schedule.brt_non_brt,
                        schedule.service_type,
                        schedule.fuel_type,
                        schedule.bus_type,
                        schedule.depot_id,
                    ]
                )

            return response

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


class UniqueValuesView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = ProjectSummarySerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = request.data.get("project_id")
            project_name = request.data.get("project_name")
            created_by = request.data.get("created_by")

            project = Project.objects.get(
                project_id=project_id, created_by=created_by, project_name=project_name
            )

            schedules = Schedule.objects.filter(project_id=project)
            depots = Depot.objects.filter(project_id=project)

            operators = schedules.values_list("operator", flat=True).distinct()

            ac_non_ac = schedules.values_list("ac_non_ac", flat=True).distinct()

            brt_non_brt = schedules.values_list("brt_non_brt", flat=True).distinct()

            fuel_type = schedules.values_list("fuel_type", flat=True).distinct()

            bus_type = schedules.values_list("bus_type", flat=True).distinct()

            service_type = schedules.values_list("service_type", flat=True).distinct()

            # Fetch depot names and their corresponding depot IDs as a list of dictionaries 
            depot_data = depots.values("depot_id", "depot_name").distinct()
            depot_list = [{"depot_name": depot["depot_name"], "depot_id": depot["depot_id"]} for depot in depot_data]

            response_data = {
                "status": "success",
                "uniqueValues": {
                    "operator": list(operators),
                    "ac_non_ac": list(ac_non_ac),
                    "brt_non_brt": list(brt_non_brt),
                    "fuel_type": list(fuel_type),
                    "bus_type": list(bus_type),
                    "service_type": list(service_type),
                    "depots": depot_list,
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CheckNewDepotsAndTerminalsView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = ProjectSummarySerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = request.data.get("project_id")
            project_name = request.data.get("project_name")
            created_by = request.data.get("created_by")

            # Fetch the project
            project = Project.objects.get(
                project_id=project_id, created_by=created_by, project_name=project_name
            )

            # Fetch depots and terminals for the project
            depots = Depot.objects.filter(project_id=project)
            terminals = Terminal.objects.filter(project_id=project)

            # Prepare a list of depot and terminal coordinates, rounding to 6 decimal places
            depot_locations = [(round(float(depot.latitude), 6), round(float(depot.longitude), 6)) for depot in depots]
            terminal_locations = [(round(float(terminal.latitude), 6), round(float(terminal.longitude), 6)) for terminal in terminals]

            # Step 1: Check for new depots in DistanceMatrix
            new_depots_count = 0
            for depot_location in depot_locations:
                depot_exists = DistanceMatrix.objects.filter(
                    Q(start_latitude=depot_location[0], start_longitude=depot_location[1]) |
                    Q(end_latitude=depot_location[0], end_longitude=depot_location[1])
                ).exists()

                if not depot_exists:
                    new_depots_count += 1

            # Step 2: Check for new terminals in DistanceMatrix
            new_terminals_count = 0
            for terminal_location in terminal_locations:
                terminal_exists = DistanceMatrix.objects.filter(
                    Q(start_latitude=terminal_location[0], start_longitude=terminal_location[1]) |
                    Q(end_latitude=terminal_location[0], end_longitude=terminal_location[1])
                ).exists()

                if not terminal_exists:
                    new_terminals_count += 1

            total_count = new_depots_count + new_terminals_count
            depot_calculations = new_depots_count * len(terminals)
            terminal_calculations = new_terminals_count * len(depots)
            total_number_calculations = depot_calculations + terminal_calculations

            # Return the counts of new depots and terminals
            response_data = {
                "status": "success",
                "new_depots_count": new_depots_count,
                "new_terminals_count": new_terminals_count,
                "total_count": total_count,
                "total_number_calculations": total_number_calculations
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response(
                {"status": False, "message": "Project not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# old view
class DepotTerminalDistanceUpdateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = NewDepotTerminalUpdateSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            project_id = request.data.get("project_id")
            created_by = request.data.get("created_by")

            project = Project.objects.get(
                project_id=project_id,
                created_by=created_by,
            )

            depots = Depot.objects.filter(project_id=project)
            depot_data = {
                depot.depot_id: DepotSerializer(depot).data for depot in depots
            }

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

            unique_depots, unique_terminals = self.get_unique_depots_and_terminals(
                depots, terminals
            )

            # Find new depots and terminals
            new_depots = set(depot_data.keys()) - set(unique_depots.keys())
            new_terminals = set(terminal_data.keys()) - set(unique_terminals.keys())

            # Fetch details of new depots and terminals
            new_depots_data = {
                depot_id: depot_data[depot_id] for depot_id in new_depots
            }
            new_terminals_data = {
                terminal_id: terminal_data[terminal_id] for terminal_id in new_terminals
            }

            if new_depots or new_terminals:
                self.update_distance_matrix(
                    new_depots_data, new_terminals_data, project_id
                )

            return Response(
                {
                    "status": True,
                    "message": "Updated new_depots and terminals",
                },
                status=status.HTTP_200_OK,
            )

        except ObjectDoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_unique_depots_and_terminals(self, depots, terminals):
        depot_names = {depot.depot_name: depot.depot_id for depot in depots}
        terminal_names = {
            terminal.terminal_name: terminal.terminal_id for terminal in terminals
        }

        unique_depots = set()
        unique_terminals = set()

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
                    unique_depots.add(depot_names[depot_name])
                    unique_terminals.add(terminal_names[terminal_name])
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
                    unique_depots.add(depot_names[depot_name])
                    unique_terminals.add(terminal_names[terminal_name])
                    terminalDepotDist[terminal_names[terminal_name]][
                        depot_names[depot_name]
                    ] = {"distance": distance.distance}

        unique_depots_data = {
            depot.depot_id: DepotSerializer(depot).data
            for depot in Depot.objects.filter(depot_id__in=unique_depots)
        }
        unique_terminals_data = {
            terminal.terminal_id: TerminalSerializer(terminal).data
            for terminal in Terminal.objects.filter(terminal_id__in=unique_terminals)
        }

        return unique_depots_data, unique_terminals_data

    def update_distance_matrix(self, new_depots_data, new_terminals_data, project_id):
        # Calculate distance from new depot to all terminals (existing and new)
        for depot_id, depot_data in new_depots_data.items():
            depot_latitude = depot_data["latitude"]
            depot_longitude = depot_data["longitude"]

            depots = Depot.objects.get(project_id=project_id, depot_id=depot_id)
            terminals = Terminal.objects.filter(project_id=project_id)

            for terminal in terminals:
                distance = calculate_distance(
                    depot_latitude,
                    depot_longitude,
                    terminal.latitude,
                    terminal.longitude,
                )

                DepotTerminalDistanceMatrix.objects.create(
                    depot_id=depots.id, terminal_id=terminal.id, distance=distance
                )

                print(
                    f"Distance from Depot {depot_id} to Terminal {terminal.terminal_id}: {distance}"
                )

        # Calculate distance from all depots to new terminal
        for depot in Depot.objects.filter(project_id=project_id):
            for terminal_id, terminal_data in new_terminals_data.items():
                terminal_latitude = terminal_data["latitude"]
                terminal_longitude = terminal_data["longitude"]

                terminals = Terminal.objects.get(
                    project_id=project_id, terminal_id=terminal_id
                )

                distance = calculate_distance(
                    depot.latitude,
                    depot.longitude,
                    terminal_latitude,
                    terminal_longitude,
                )
                DepotTerminalDistanceMatrix.objects.create(
                    depot_id=depot.id, terminal_id=terminals.id, distance=distance
                )

            print(
                f"Distance from Depot {depot.depot_id} to Terminal {terminal_id}: {distance}"
            )

        # Calculate distance from new terminal to all depots (existing and new)
        for terminal_id, terminal_data in new_terminals_data.items():
            terminal_latitude = terminal_data["latitude"]
            terminal_longitude = terminal_data["longitude"]

            terminals = Terminal.objects.get(
                project_id=project_id, terminal_id=terminal_id
            )

            for depot in Depot.objects.filter(project_id=project_id):
                distance = calculate_distance(
                    terminal_latitude,
                    terminal_longitude,
                    depot.latitude,
                    depot.longitude,
                )
                TerminalDepotDistanceMatrix.objects.create(
                    terminal_id=terminals.id, depot_id=depot.id, distance=distance
                )

                print(
                    f"Distance from Terminal {terminal_id} to Depot {depot.depot_id}: {distance}"
                )

        # Calculate distance from all terminals to new depot
        for terminal in Terminal.objects.filter(project_id=project_id):
            for depot_id, depot_data in new_depots_data.items():
                depot_latitude = depot_data["latitude"]
                depot_longitude = depot_data["longitude"]

                depots = Depot.objects.get(project_id=project_id, depot_id=depot_id)

                distance = calculate_distance(
                    terminal.latitude,
                    terminal.longitude,
                    depot_latitude,
                    depot_longitude,
                )
                TerminalDepotDistanceMatrix.objects.create(
                    terminal_id=terminal.id, depot_id=depots.id, distance=distance
                )

                print(
                    f"Distance from Terminal {terminal.terminal_id} to Depot {depot_id}: {distance}"
                )


class DistanceMatrixUpdateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = NewDepotTerminalUpdateSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            project_id = request.data.get("project_id")
            created_by = request.data.get("created_by")

            # Retrieve the project details
            project = Project.objects.get(
                project_id=project_id,
                created_by=created_by,
            )

            depots = Depot.objects.filter(project_id=project)
            terminals = Terminal.objects.filter(project_id=project)

            self.update_distance_matrix(depots, terminals)

            print("DONE: updating distance matrix")

            return Response(
                {
                    "status": True,
                    "message": "Updated distance matrix",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            traceback.print_exc()
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update_distance_matrix(self, depots, terminals):

        print("updating distance matrix")

        for depot in depots:
            depot_lat = format_decimal(depot.latitude)
            depot_lon = format_decimal(depot.longitude)
            for terminal in terminals:
                terminal_lat = format_decimal(terminal.latitude)
                terminal_lon = format_decimal(terminal.longitude)
                if not DistanceMatrix.objects.filter(
                    start_latitude=depot_lat,
                    start_longitude=depot_lon,
                    end_latitude=terminal_lat,
                    end_longitude=terminal_lon,
                ).exists():
                    _distance = calculate_distance(
                        depot.latitude,
                        depot.longitude,
                        terminal.latitude,
                        terminal.longitude,
                    )

                    DistanceMatrix.objects.create(
                        start_latitude=depot_lat,
                        start_longitude=depot_lon,
                        end_latitude=terminal_lat,
                        end_longitude=terminal_lon,
                        distance=_distance,
                    )

                    print(
                        f"Distance from Depot {depot.depot_id} to Terminal {terminal.terminal_id}: {_distance}"
                    )

                if not DistanceMatrix.objects.filter(
                    start_latitude=terminal_lat,
                    start_longitude=terminal_lon,
                    end_latitude=depot_lat,
                    end_longitude=depot_lon,
                ).exists():
                    _distance = calculate_distance(
                        terminal.latitude,
                        terminal.longitude,
                        depot.latitude,
                        depot.longitude,
                    )

                    DistanceMatrix.objects.create(
                        start_latitude=terminal_lat,
                        start_longitude=terminal_lon,
                        end_latitude=depot_lat,
                        end_longitude=depot_lon,
                        distance=_distance,
                    )
                    print(
                        f"Distance from Terminal {terminal.terminal_id} to Depot {depot.depot_id}: {_distance}"
                    )


class GetAllDepotsView(APIView):
    def get(self, request, *args, **kwargs):
        params = {
            "project_id": request.GET.get("project_id"),
            "created_by": request.GET.get("created_by")
        }
        serializer_class = DepotTerminalSerializer(data=params)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            project_id = params["project_id"]
            created_by = params["created_by"]

            try:
                project = Project.objects.get(
                    project_id=project_id, created_by=created_by
                )

                depots = Depot.objects.filter(project_id=project)

                depot_serializer = DepotSerializer(depots, many=True)

                response_data = {
                    "status": "success",
                    "data": depot_serializer.data,
                }
                return Response(response_data, status=status.HTTP_200_OK)

            except Project.DoesNotExist:
                return Response(
                    {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
                )

            except Exception as e:
                return Response(
                    {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                ) 


class GetAllTerminalsView(APIView):
    def get(self, request, *args, **kwargs):
        params = {
            "project_id": request.GET.get("project_id"),
            "created_by": request.GET.get("created_by")
        }
        serializer_class = DepotTerminalSerializer(data=params)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            project_id = params["project_id"]
            created_by = params["created_by"]

            try:
                project = Project.objects.get(
                    project_id=project_id, created_by=created_by
                )

                terminals = Terminal.objects.filter(project_id=project)

                terminal_serializer = TerminalSerializer(terminals, many=True)

                response_data = {
                    "status": "success",
                    "data": terminal_serializer.data,
                }
                return Response(response_data, status=status.HTTP_200_OK)

            except Project.DoesNotExist:
                return Response(
                    {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
                )

            except Exception as e:
                return Response(
                    {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )                             


class GetDepotsByProjectIdView(APIView):
    def get(self, request, *args, **kwargs):
        params = {
            "project_id": request.GET.get("project_id"),
            "created_by": request.GET.get("created_by")
        }
        serializer_class = GetDepotsByIdSerializer(data=params)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            project_id = params["project_id"]
            created_by = params["created_by"]

            try:
                project = Project.objects.get(
                    project_id=project_id, created_by=created_by
                )

                schedules = Schedule.objects.filter(project_id=project)

                depot_names = schedules.values_list("depot_id", flat=True).distinct()
                depots = Depot.objects.filter(depot_name__in=depot_names, project_id=project).distinct()

                depot_serializer = DepotSerializer(depots, many=True)

                response_data = {
                    "status": "success",
                    "data": depot_serializer.data,
                }
                return Response(response_data, status=status.HTTP_200_OK)

            except Project.DoesNotExist:
                return Response(
                    {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
                )

            except Exception as e:
                return Response(
                    {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        
class GetTerminalsByProjectIdView(APIView):
    def get(self, request, *args, **kwargs):
        params = {
            "project_id": request.GET.get("project_id"),
            "created_by": request.GET.get("created_by"),
            "depot_id": request.GET.get("depot_id")
        }
        serializer_class = GetTerminalsByIdSerializer(data=params)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            project_id = params["project_id"]
            created_by = params["created_by"]
            depot_id = params["depot_id"]

            try:
                project = Project.objects.get(
                    project_id=project_id, created_by=created_by
                )

                schedules = Schedule.objects.filter(project_id=project, depot_id=depot_id)

                terminal_names = set()
                for schedule in schedules:
                    if schedule.start_terminal:
                        terminal_names.add(schedule.start_terminal)
                    if schedule.end_terminal:
                        terminal_names.add(schedule.end_terminal)

                terminals = Terminal.objects.filter(terminal_name__in=terminal_names,project_id=project).distinct()

                terminal_serializer = TerminalSerializer(terminals, many=True)

                response_data = {
                    "status": "success",
                    "data": terminal_serializer.data,
                }
                return Response(response_data, status=status.HTTP_200_OK)

            except Project.DoesNotExist:
                return Response(
                    {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
                )

            except Exception as e:
                return Response(
                    {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


class BusModelCreateView(APIView):
    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response(
                {"status": False, "message": "Expected a list of bus models"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = BusModelSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            bus_models = serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Bus models created successfully",
                    "data": BusModelSerializer(bus_models, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class BusModelListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            bus_models = BusModel.objects.all()
            bus_serializer = BusModelSerializer(bus_models, many=True)
            return Response(
                {
                    "status": True,
                    "message": "Bus models retrieved successfully",
                    "data": bus_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

class ChargerModelListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            charger_models = ChargerModel.objects.all()
            charger_serializer = ChargerModelSerializer(charger_models, many=True)
            return Response(
                {
                    "status": True,
                    "message": "Charger models retrieved successfully",
                    "data": charger_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChargerModelCreateView(APIView):
    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response(
                {"status": False, "message": "Expected a list of charger models"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = ChargerModelSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            charger_models = serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Charger models created successfully",
                    "data": ChargerModelSerializer(charger_models, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DeleteBusModelView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = BusDeleteSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            short_name = serializer_class.validated_data["short_name"]

            busmodel = BusModel.objects.get(short_name=short_name)

            busmodel.delete()
            return Response(
                {"status": True, "message": "Bus model deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except BusModel.DoesNotExist:
            return Response(
                {"status": False, "message": "Bus model not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
    
class DeleteChargerModelView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = ChargerDeleteSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            short_name = serializer_class.validated_data["short_name"]

            chargermodel = ChargerModel.objects.get(short_name=short_name)

            chargermodel.delete()
            return Response(
                {"status": True, "message": "Charger model deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except ChargerModel.DoesNotExist:
            return Response(
                {"status": False, "message": "Charger model not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateBusModelView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            bus_model_id = request.data.get("id")
            existing_bus_model = BusModel.objects.get(id=bus_model_id)
        except BusModel.DoesNotExist:
            return Response(
                {"status": False, "message": "Bus model not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BusModelSerializer(existing_bus_model, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer.save()
        
        return Response(
            {"status": True, "message": "Bus model updated"},
            status=status.HTTP_200_OK,
        )


class UpdateChargerModelView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            charger_model_id = request.data.get("id")
            existing_charger_model = ChargerModel.objects.get(id=charger_model_id)
        except ChargerModel.DoesNotExist:
            return Response(
                {"status": False, "message": "Charger model not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ChargerModelSerializer(existing_charger_model, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer.save()
        
        return Response(
            {"status": True, "message": "Charger model updated"},
            status=status.HTTP_200_OK,
        )
    

class BusModelPowerConsumptionView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            short_names_str = request.query_params.get('short_names', '')
            if not short_names_str:
                return Response(
                    {
                        "status": False,
                        "message": "No short names provided",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            short_names = short_names_str.split(',')
            bus_models = BusModel.objects.filter(short_name__in=short_names)
            found_short_names = set(bus.short_name for bus in bus_models)
            not_found_short_names = set(short_names) - found_short_names

            bus_data = [
                {"short_name": bus.short_name, "power_consumption": bus.power_consumption}
                for bus in bus_models
            ]
            
            response_data = {
                "status": True,
                "message": "Bus models retrieved successfully",
                "data": bus_data,
            }
            
            if not_found_short_names:
                response_data["not_found"] = list(not_found_short_names)
                response_data["message"] = "Some bus models were not found"

            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

class DynamicFileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = DynamicFileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project_id = serializer.validated_data["project_id"]
        power_consp_data = serializer.validated_data["power_consp_data"]
        scenario_name = serializer.validated_data.get("scenario_name", "Default Scenario Name")
        description = serializer.validated_data.get("description", "")

        if not power_consp_data:
            return Response(
                {"status": False, "message": "Power consumption data cannot be empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.objects.get(project_id=project_id)

            scenario = PowerScenario.objects.create(
                scenario_name=scenario_name,
                description=description,
                project_id=project,
            )
            scenario.save()

            for power_object in power_consp_data:
                bus_model = BusModel.objects.get(short_name=power_object['short_name'])
                
                HistoryPowerConsumptionModel.objects.create(
                    project_id=project,
                    scenario=scenario,  
                    route_no=power_object['route_no'],
                    start_min=power_object['start_min'],
                    end_min=power_object['end_min'],
                    start_odo=power_object['start_odo'],
                    end_odo=power_object['end_odo'],
                    start_soc=power_object['start_soc'],
                    end_soc=power_object['end_soc'],
                    passenger_load=power_object['passenger_load'],
                    short_name=bus_model,
                )

            response_data = {
                "scenario_id" : scenario.scenario_id,
                "scenario_name" : scenario_name,
            }   

            return Response(
                {
                    "status": True,
                    "message": "Power model and scenario created successfully",
                    "response": response_data
                },
                status=status.HTTP_200_OK,
            )

        except Project.DoesNotExist:
            return Response(
                {"status": False, "message": "Project does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except BusModel.DoesNotExist:
            return Response(
                {"status": False, "message": f"BusModel with short_name {power_object['short_name']} does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )  


class DynamicPowerConsumptionView(APIView):
    def post(self, request, *args, **kwargs):
        serializer =  DynamicPowerConsumptionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = request.data.get("project_id")
            project_name = request.data.get("project_name")
            created_by = request.data.get("created_by")
            scenario_id = request.data.get("scenario_id")

            project = Project.objects.get(project_id=project_id, created_by=created_by, project_name=project_name)

            hist_powers = HistoryPowerConsumptionModel.objects.filter(project_id=project, scenario_id=scenario_id)
            if not hist_powers.exists():
                return Response(
                    {"status": False, "message": "Scenario not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            historical_data = []
            for power in hist_powers:
                power_data = HistoryPowerConsumptionSerializer(power).data
                power_data['short_name'] = power.short_name.short_name  
                historical_data.append(power_data)

            bus_models = BusModel.objects.all()
            bus_model_data = {bus.short_name: BusModelSerializer(bus).data for bus in bus_models}

            historical_df = pd.DataFrame(historical_data)
            bus_model_df = pd.DataFrame.from_dict(bus_model_data, orient='index')

            base_percentage = request.data.get("basePercentage")

            PC_per_tonnekm_route_model_dict, PC_per_tonnekm_model_dict = get_pc_profile(historical_df, bus_model_df, base_percentage)

            response_data = {
                "PC_per_tonnekm_route_model_dict": [],
                "PC_per_tonnekm_model_dict": []
            }

            for key, value in PC_per_tonnekm_route_model_dict.items():
                item_dict = {
                    "route": key,
                    "result": value,
                }
                response_data["PC_per_tonnekm_route_model_dict"].append(item_dict)

            for key, value in PC_per_tonnekm_model_dict.items():
                item_dict = {
                    "model": key,
                    "result": value,
                }
                response_data["PC_per_tonnekm_model_dict"].append(item_dict)

            return Response(
                {
                    "status": True,
                    "message": "Data fetched successfully",
                    "data": response_data,
                },
                status=status.HTTP_200_OK,
            )

        except ObjectDoesNotExist as e:
            return Response(
                {"status": False, "message": str(e)}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class CreateChargingScenarioView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CreateChargingScenarioSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "false", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = serializer.validated_data["project_id"]
            created_by = serializer.validated_data["created_by"]
            project = Project.objects.get(project_id=project_id, created_by=created_by)

            scenario_name = serializer.validated_data["scenario_name"]
            description = serializer.validated_data["description"]

            data = {
                "project": project,
                "workflow_type": serializer.validated_data["workflow_type"],
                "depot_list": serializer.validated_data["depot_list"],
                "bus_models_list": serializer.validated_data["bus_models_list"],
                "charger_model_list": serializer.validated_data["charger_model_list"],
                "opportunity_charging": serializer.validated_data["opportunity_charging"],
                "static_pc_per_km": serializer.validated_data["static_pc_per_km"],
               
                "candidate_terminal_charging_location_list": request.data.get("candidate_terminal_charging_location_list", []),
                "base_chargers_list":serializer.validated_data["base_chargers_list"],
                "simulation_parameters": serializer.validated_data["simulation_parameters"],
                "advance_settings": serializer.validated_data["advance_settings"],
                "depotallocation_scenario_id": request.data.get("depotallocation_scenario_id"),
            }

            IsFeasible, result = run_algorithm(
                data["project"],
                data["workflow_type"],
                data["depot_list"],
                data["bus_models_list"],
                data["charger_model_list"],
                data["opportunity_charging"],
                data["static_pc_per_km"],
                
                data["candidate_terminal_charging_location_list"],
                data["base_chargers_list"],
                data["simulation_parameters"],
                data["advance_settings"],
                data["depotallocation_scenario_id"],
            )

            if IsFeasible=="NO":
                return Response(
                        {
                            "status": True,
                            "message": "scenario isn't feasible.!",
                            "IsFeasible": IsFeasible,
                            "result": result
                        },
                        status=status.HTTP_200_OK,
                    )
            
            elif IsFeasible=="YES":
                requestdata={
                    "workflow_type": data["workflow_type"],
                    "depot_list": data["depot_list"],
                    "bus_models_list":  data["bus_models_list"],
                    "charger_model_list": data["charger_model_list"],
                    "opportunity_charging": data["opportunity_charging"],
                    "static_pc_per_km": data["static_pc_per_km"],
                   
                    "candidate_terminal_charging_location_list": data["candidate_terminal_charging_location_list"],
                    "base_chargers_list" :data["base_chargers_list"],
                    "simulation_parameters": data["simulation_parameters"],
                    "advance_settings": data["advance_settings"],
                    "depotallocation_scenario_id": data["depotallocation_scenario_id"],
                }

                scenario = ChargingAnalysisScenario.objects.create(
                    scenario_name=scenario_name,
                    description=description,
                    requestdata=requestdata,
                    result=result,
                    project_id=project,
                    )
                scenario.save()

                response_data = (ChargingScenarioSerializer(scenario).data,)

                return Response(
                        {
                            "status": True,
                            "message": "scenario created successfully",
                            "scenario_id": scenario.scenario_id,
                            "IsFeasible": IsFeasible,
                            "scenario": response_data,
                        },
                        status=status.HTTP_200_OK,
                    )

            return Response(
                {
                    "status": False,
                    "message": "Unknown feasibility status",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChargingAnalysisResultsView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ChargingAnalysisResultsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "false", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = serializer.validated_data["project_id"]
            created_by = serializer.validated_data["created_by"]
            scenario_id = serializer.validated_data["scenario_id"]

            project = Project.objects.get(project_id=project_id, created_by=created_by)

            scenario_data = ChargingAnalysisScenario.objects.get(project_id=project, scenario_id=scenario_id)

            result_data = scenario_data.result

            inputdata = {
                "IsFeasible": result_data["IsFeasible"],
                "charger_system": result_data["charger_system"],
                "charging_schedule_df": result_data["charging_schedule_df"],
                "power_consumption_per_km": result_data["power_consumption_per_km"],
                "schedule_df": result_data["schedule_df"],
                "gvw": result_data["gvw"],
                "np_bc": result_data["np_bc"],
                "depot_df": result_data["depot_df"],
                "terminal_df": result_data["terminal_df"],
                "y_depot_dead_dict": result_data["y_depot_dead_dict"]
            }

            analytics_response_data = data_analytics(
                inputdata["charger_system"],
                inputdata["charging_schedule_df"],
                inputdata["power_consumption_per_km"],
                inputdata["schedule_df"],
                inputdata["gvw"],
                inputdata["np_bc"],
                inputdata["depot_df"],
                inputdata["terminal_df"],
                inputdata["y_depot_dead_dict"]
            )

            return Response(
                {
                    "status": True,
                    "message": "Results fetched successfully",
                    "IsFeasible": inputdata["IsFeasible"],
                    "scenario_id": scenario_id,
                    "ScenarioResults": analytics_response_data,
                },
                status=status.HTTP_200_OK,
            )

        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        except ChargingAnalysisScenario.DoesNotExist:
            return Response(
                {"error": "Scenario not found."}, status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListChargingScenarios(APIView):
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
                scenarios = (
                    ChargingAnalysisScenario.objects.filter(project_id=project_id)
                    .order_by("-scenario_id")
                    .values()
                )
                paginator = Paginator(scenarios, params["pageSize"])
                page = paginator.page(params["pageNumber"])

                return Response(
                    {
                        "status": True,
                        "total_scenarios": paginator.count,
                        "message": "Charging Scenario list",
                        "scenarios": list(page),
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                error_message = str(e)
                return Response(
                    {"message": error_message}, status=status.HTTP_404_NOT_FOUND
                )


class UpdateChargingScenarioView(APIView):
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
                existing_scenario = ChargingAnalysisScenario.objects.get(scenario_id=scenario_id)
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


class DeleteChargingScenario(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = ScenarioDeleteSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            scenario_id = serializer_class.validated_data["scenario_id"]

            scenario = ChargingAnalysisScenario.objects.get(scenario_id=scenario_id)

            scenario.delete()

            return Response(
                {"status": True, "message": "Charging Scenario deleted"},
                status=status.HTTP_200_OK,
            )

        except ChargingAnalysisScenario.DoesNotExist:
            return Response(
                {"status": False, "message": "Charging Scenario not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilteredCCSBusModelListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            bus_models_ccs = BusModel.objects.filter(charger_type__icontains='CCS2')
            bus_serializer = BusModelSerializer(bus_models_ccs, many=True)
            return Response(
                {
                    "status": True,
                    "message": "Bus models retrieved successfully",
                    "data": bus_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilteredGBTBusModelListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            bus_models_gbt = BusModel.objects.filter(charger_type__icontains="GB")
            bus_serializer = BusModelSerializer(bus_models_gbt, many=True)
            return Response(
                {
                    "status": True,
                    "message": "Bus models retrieved successfully",
                    "data": bus_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SuggestedBusModelView(APIView):
     def post(self, request, *args, **kwargs):
        serializer_class = SuggestedBusModelSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            depot_night_charging_strategy = serializer_class.validated_data["depot_night_charging_strategy"]
            assured_km = serializer_class.validated_data["assured_km"]
            opportunity_charging_duration = serializer_class.validated_data["opportunity_charging_duration"]
            reserve_charge = serializer_class.validated_data["reserve_charge"]
            bus_length = serializer_class.validated_data["bus_length"]

            reserve_charge = reserve_charge / 100
            buses = BusModel.objects.all()
            bus_models = pd.DataFrame(list(buses.values()))
            
            chargers = ChargerModel.objects.all()
            charger_models = pd.DataFrame(list(chargers.values()))

            filtered_bus_modelsdf = bus_models[bus_models['bus_dimension'] == bus_length]
            filtered_bus_modelsdf = filtered_bus_modelsdf[filtered_bus_modelsdf['charger_type'].str.contains('CCS2|GB', na=False, regex=True)]


            if depot_night_charging_strategy:
                filtered_bus_modelsdf['total_range'] = (filtered_bus_modelsdf['battery_capacity']/filtered_bus_modelsdf['power_consumption'])*(1-reserve_charge)

            else:
                ccs2_charger_models = charger_models.copy()[charger_models['charger_type'].str.contains('CCS2', na=False, regex=False)] # Charger CCS2
                ccs2_charger_models = ccs2_charger_models.sort_values(by=['charger_capacity'], ascending=False).reset_index(drop=True) # sort highest charger capacity
                ccs2_charger_capacity = ccs2_charger_models['charger_capacity'].tolist()[0] #select highest charger capacity

                gbbyt_charger_models = charger_models[charger_models['charger_type'].str.contains('GB', na=False)] # Charger GBBYT
                gbbyt_charger_models = gbbyt_charger_models.sort_values(by=['charger_capacity'], ascending=False).reset_index(drop=True) # sort highest charger capacity
                gbbyt_charger_capacity = gbbyt_charger_models['charger_capacity'].tolist()[0] #select highest charger capacity

                filtered_bus_modelsdf['top_up'] = [min(ccs2_charger_capacity*(opportunity_charging_duration/60), 0.85*(1-reserve_charge) * bc) if 'CCS2' in ct else min(gbbyt_charger_capacity*(opportunity_charging_duration/60), 0.85*(1-reserve_charge) * bc) for bc, ct in zip(filtered_bus_modelsdf['battery_capacity'], filtered_bus_modelsdf['charger_type'])] #top up for opportunity charging
                filtered_bus_modelsdf['range'] = (filtered_bus_modelsdf['battery_capacity']*(1-reserve_charge))/filtered_bus_modelsdf['power_consumption']
                filtered_bus_modelsdf['topup_range'] = filtered_bus_modelsdf['top_up']/filtered_bus_modelsdf['power_consumption']
                filtered_bus_modelsdf['total_range'] = filtered_bus_modelsdf['range'] + filtered_bus_modelsdf['topup_range']

            filtered_bus_modelsdf = filtered_bus_modelsdf.sort_values(by=['total_range'], ascending=False).reset_index(drop=True)
    
            suggested_bus_model = filtered_bus_modelsdf.to_dict(orient='records')

            return Response(
                {
                    "status": True,
                    "message": "Bus model retrieved successfully",
                    "data": suggested_bus_model,
                },
                status=status.HTTP_200_OK,
            )
        
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ExistingDepotAllocationDataView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ExistingDepotAllocationDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = serializer.validated_data["project_id"]
            created_by = serializer.validated_data["created_by"]
            project = Project.objects.get(project_id=project_id, created_by=created_by)

            depot_list = serializer.validated_data["depot_list"]
            
            depots = Depot.objects.filter(depot_name__in=depot_list, project_id=project).distinct()
            schedules = Schedule.objects.filter(project_id=project, depot_id__in=depot_list)

            terminal_names = set()
            for schedule in schedules:
                if schedule.start_terminal:
                    terminal_names.add(schedule.start_terminal)
                if schedule.end_terminal:
                    terminal_names.add(schedule.end_terminal)

            terminals = Terminal.objects.filter(terminal_name__in=terminal_names, project_id=project).distinct()

            substations = Substation.objects.filter(project_id=project)
                                        
            depot_schedule_counts = []
            depot_terminal_schedule_counts = []
            for depot in depots:
                unique_schedule_ids = set()
                depot_schedules = schedules.filter(depot_id=depot.depot_name)
                for schedule in depot_schedules:
                    unique_schedule_ids.add(schedule.schedule_id)

                terminal_names = set()
                for schedule in depot_schedules:
                    if schedule.start_terminal:
                        terminal_names.add(schedule.start_terminal)
                    if schedule.end_terminal:
                        terminal_names.add(schedule.end_terminal)
                
                depot_schedule_counts.append({
                    "depot_id": depot.depot_id,
                    "depot_name": depot.depot_name,
                    "latitude": depot.latitude,
                    "longitude":depot.longitude,
                    "NoOfSchedules": len(unique_schedule_ids),
                    "NoOfterminals": len(terminal_names),
                    "terminals_list": list(terminal_names),
                })

                for terminal in terminal_names:
                    terminal_schedules = depot_schedules.filter(start_terminal=terminal) | depot_schedules.filter(end_terminal=terminal)
                    unique_terminal_schedule_ids = {schedule.schedule_id for schedule in terminal_schedules}

                    depot_terminal_schedule_counts.append({
                        "depot": depot.depot_name,
                        "terminal": terminal,
                        "no_of_unique_schedules": len(unique_terminal_schedule_ids),
                    })

            depot_serializer = GetDepotSerializer(depots, many=True)
            schedule_serializer = GetScheduleSerializer(schedules, many=True)
            terminal_serializer = GetTerminalSerializer(terminals, many=True)
            substation_serializer = GetSubstationSerializer(substations, many=True)
            
            response_data = {
                "depot_schedule_counts": depot_schedule_counts,
                "depot_terminal_schedule_counts": depot_terminal_schedule_counts,
                "terminal_data": terminal_serializer.data,
                "substation_data": substation_serializer.data
            }

            return Response(
                {
                    "status": True, 
                    "message": "Data Fetched Successfully",
                    "response_Data":response_data
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProposedDepotAllocationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ProposedDepotAllocationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "false", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = serializer.validated_data["project_id"]
            created_by = serializer.validated_data["created_by"]

            project = Project.objects.get(project_id=project_id, created_by=created_by)

            scenario_name = serializer.validated_data["scenario_name"]
            description = serializer.validated_data["description"]

            data = {
                "project": project,
                "candidate_depots": serializer.validated_data["candidate_depots"],
                "candidate_depots_cost": serializer.validated_data["candidate_depots_cost"],
                "busmodel_suggestion": serializer.validated_data["busmodel_suggestion"],
                "depot_allocation_inputs": serializer.validated_data["depot_allocation_inputs"],
                "suggested_busmodel": serializer.validated_data["suggested_busmodel"],
            }

            depot_list = data["candidate_depots"]
            depots = Depot.objects.filter(depot_name__in=depot_list, project_id=project).distinct()
            depot_df = pd.DataFrame(list(depots.values()))

            total_capacity = depot_df['capacity'].sum()
            number_of_buses = data["depot_allocation_inputs"]["number_of_buses"]

            if total_capacity < number_of_buses:
                return Response(
                    {
                        "status": True,
                        "IsFeasible": "NO",
                        "message": "Number of buses is more than given depot's capacity ",
                        "response_Data": total_capacity
                        
                    },
                    status=status.HTTP_200_OK,
                )

            else:
                IsFeasible, depot_result = ebus_depot_allocation(
                    data["project"],
                    data["candidate_depots"],
                    data["candidate_depots_cost"],
                    data["busmodel_suggestion"],
                    data["depot_allocation_inputs"],
                    data["suggested_busmodel"],
                
                )

                if IsFeasible=="NO":
                    return Response(
                            {
                                "status": True,
                                "IsFeasible": IsFeasible,
                                "message": "Scenario isn't feasible.!",
                            },
                            status=status.HTTP_200_OK,
                        )
            
                elif IsFeasible=="YES":
                    depot_requestdata={
                        "candidate_depots": data["candidate_depots"],
                        "candidate_depots_cost": data["candidate_depots_cost"],
                        "busmodel_suggestion":  data["busmodel_suggestion"],
                        "depot_allocation_inputs": data["depot_allocation_inputs"],
                        "suggested_busmodel": data["suggested_busmodel"],
                    }

                    scenario = DepotAllocationScenario.objects.create(
                        scenario_name=scenario_name,
                        description=description,
                        depot_requestdata=depot_requestdata,
                        depot_result=depot_result,
                        project_id=project,
                        )
                    scenario.save()
                    
                    new_schedule_df = depot_result["new_schedule_df"]
                    for _, schedule in new_schedule_df.iterrows():
                        DepotAllocation_Schedule.objects.create(
                            scenario=scenario,
                            project_id=project,
                            schedule_id=schedule['schedule_id'],
                            trip_number=schedule['trip_number'],
                            route_number=schedule['route_number'],
                            direction=schedule['direction'],
                            start_terminal=schedule['start_terminal'],
                            end_terminal=schedule['end_terminal'],
                            start_time=schedule['start_time'],
                            travel_time=schedule['travel_time'],
                            trip_distance=schedule['trip_distance'],
                            crew_id=schedule['crew_id'],
                            event_type=schedule['event_type'],
                            operator=schedule['operator'],
                            ac_non_ac=schedule['ac_non_ac'],
                            brt_non_brt=schedule['brt_non_brt'],
                            service_type=schedule['service_type'],
                            fuel_type=schedule['fuel_type'],
                            bus_type=schedule['bus_type'],
                            depot_id=schedule['depot_id'],
                        )

                    response_data = (DepotAllocationScenarioSerializer(scenario).data,)

                    return Response(
                        {
                            "status": True,
                            "IsFeasible":"YES",
                            "message": "Depot Allocation Scenario Created successfully",
                            "scenario_id": scenario.scenario_id,
                            "response_Data": response_data
                        },
                        status=status.HTTP_200_OK,
                    )

        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DepotAllocationScenarioResultsView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ChargingAnalysisResultsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "false", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = serializer.validated_data["project_id"]
            created_by = serializer.validated_data["created_by"]
            scenario_id = serializer.validated_data["scenario_id"]

            project = Project.objects.get(project_id=project_id, created_by=created_by)
            depot_scenario_data = DepotAllocationScenario.objects.get(project_id=project, scenario_id=scenario_id)

            scenario_name = depot_scenario_data.scenario_name
            description = depot_scenario_data.description
            depot_results = depot_scenario_data.depot_result

            schedule_qs = DepotAllocation_Schedule.objects.filter(scenario=depot_scenario_data)
            new_schedule_df = pd.DataFrame.from_records(schedule_qs.values())

            depot_df = depot_results['depot_df']
            terminal_df = depot_results['terminal_df']
            substation_df = depot_results['substation_df']

            depot_list = new_schedule_df['depot_id'].unique()
            depot_list = list(depot_list)
            depots = depot_df[depot_df['depot_name'].isin(depot_list)]

            schedules = new_schedule_df[new_schedule_df['depot_id'].isin(depot_list)]

            all_terminals_list = set()
            for _, schedule in schedules.iterrows():
                if schedule['start_terminal']:
                    all_terminals_list.add(schedule['start_terminal'])
                if schedule['end_terminal']:
                    all_terminals_list.add(schedule['end_terminal'])

            all_terminals = terminal_df[terminal_df['terminal_name'].isin(all_terminals_list)]

            terminal_names = set()
            for _, schedule in schedules.iterrows():
                if schedule['trip_number'] == 0 and schedule['end_terminal']:
                    terminal_names.add(schedule['end_terminal'])

            terminals = terminal_df[terminal_df['terminal_name'].isin(terminal_names)]
            substations = substation_df

            depot_schedule_counts = []
            depot_terminal_schedule_counts = []
            depot_route_schedule_counts = []

            for _, depot in depots.iterrows():
                unique_schedule_ids = set()
                depot_schedules = schedules[schedules['depot_id'] == depot['depot_name']]
                
                for _, schedule in depot_schedules.iterrows():
                    unique_schedule_ids.add(schedule['schedule_id'])

                terminal_names = set()
                for _, schedule in depot_schedules.iterrows():
                    if schedule['trip_number'] == 0 and schedule['end_terminal']:
                        terminal_names.add(schedule['end_terminal'])

                depot_schedule_counts.append({
                    "depot_id": depot['depot_id'],
                    "depot_name": depot['depot_name'],
                    "latitude": depot['latitude'],
                    "longitude": depot['longitude'],
                    "NoOfSchedules": len(unique_schedule_ids),
                    "NoOfterminals": len(terminal_names),
                    "terminals_list": list(terminal_names),
                })

                for terminal in terminal_names:
                    terminal_schedules = depot_schedules[
                        (depot_schedules['end_terminal'] == terminal) & 
                        (depot_schedules['trip_number'] == 0)
                    ]   
                    unique_terminal_schedule_ids = terminal_schedules['schedule_id'].unique()

                    depot_terminal_schedule_counts.append({
                        "depot": depot['depot_name'],
                        "terminal": terminal,
                        "no_of_unique_schedules": len(unique_terminal_schedule_ids),
                    })

                route_numbers = depot_schedules['route_number'].unique()
                for route_number in route_numbers:
                    route_schedules = depot_schedules[depot_schedules['route_number'] == route_number]
                    unique_route_schedule_ids = route_schedules['schedule_id'].unique()

                    depot_route_schedule_counts.append({
                        "depot": depot['depot_name'],
                        "route_number": route_number,
                        "no_of_unique_schedules": len(unique_route_schedule_ids),
                    })

            depot_serializer = depots.to_dict(orient='records')
            schedule_serializer = schedules.to_dict(orient='records')
            terminal_serializer = terminals.to_dict(orient='records')
            all_terminals_serializer = all_terminals.to_dict(orient='records')
            substation_serializer = substations.to_dict(orient='records')
            
            response_data = {
                "scenario_name": scenario_name,
                "description": description,
                "depot_schedule_counts": depot_schedule_counts,
                "depot_terminal_schedule_counts": depot_terminal_schedule_counts,
                "depot_route_schedule_counts": depot_route_schedule_counts,
                "terminal_data": terminal_serializer,
                "all_terminal_data": all_terminals_serializer, 
                "schedules_data": schedule_serializer,
                "substation_data": substation_serializer
            }
            
            return Response(
                {
                    "status": True,
                    "message": "results fetched successfully",
                    "scenario_id": scenario_id,
                    "response_data": response_data
                },
                status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response(
                {"status": "false", "message": "Project not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        except DepotAllocationScenario.DoesNotExist:
            return Response(
                {"status": "false", "message": "Depot Allocation Scenario not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        except Exception as e:
            return Response(
                {"status": "false", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TransformerCreateView(APIView):
    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response(
                {"status": False, "message": "Expected a list of Transformer"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = TransformerSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            transformers = serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Transformer created successfully",
                    "data": TransformerSerializer(transformers, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TransformerListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            transformers = Transformer.objects.all()
            transformer_serializer = TransformerSerializer(transformers, many=True)
            return Response(
                {
                    "status": True,
                    "message": "Transformer retrieved successfully",
                    "data": transformer_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DeleteTransformerView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = TransformerDeleteSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            id = serializer_class.validated_data["id"]
            transformer = serializer_class.validated_data["transformer"]

            transformer_model = Transformer.objects.get(id=id,transformer=transformer)

            transformer_model.delete()
            return Response(
                {"status": True, "message": "Transformer deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except Transformer.DoesNotExist:
            return Response(
                {"status": False, "message": "Transformer not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateTransformerView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            transformer_id = request.data.get("id")
            existing_transformer = Transformer.objects.get(id=transformer_id)
        except Transformer.DoesNotExist:
            return Response(
                {"status": False, "message": "Transformer not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TransformerSerializer(existing_transformer, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer.save()
        
        return Response(
            {"status": True, "message": "Transformer updated"},
            status=status.HTTP_200_OK,
        )


class HTCableCreateView(APIView):
    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response(
                {"status": False, "message": "Expected a list of HTCable"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = HTCableSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            htcables = serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "HTCable created successfully",
                    "data": HTCableSerializer(htcables, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class HTCableListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            htcables = HTCable.objects.all()
            htcable_serializer = HTCableSerializer(htcables, many=True)
            return Response(
                {
                    "status": True,
                    "message": "HT Cables retrieved successfully",
                    "data": htcable_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DeleteHTCableView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = HtCableDeleteSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            id = serializer_class.validated_data["id"]
            cable_type = serializer_class.validated_data["cable_type"]

            htcable = HTCable.objects.get(id=id,cable_type=cable_type)

            htcable.delete()
            return Response(
                {"status": True, "message": "HTCable deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except HTCable.DoesNotExist:
            return Response(
                {"status": False, "message": "HTCable not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateHTCableView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            htcable_id = request.data.get("id")
            existing_htcable = HTCable.objects.get(id=htcable_id)
        except HTCable.DoesNotExist:
            return Response(
                {"status": False, "message": "HTCable not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = HTCableSerializer(existing_htcable, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer.save()
        
        return Response(
            {"status": True, "message": "HTCable updated"},
            status=status.HTTP_200_OK,
        )
  

class RMUCreateView(APIView):
    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response(
                {"status": False, "message": "Expected a list of RMU"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = RMUSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            rmus = serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "RMU created successfully",
                    "data": RMUSerializer(rmus, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

class RMUListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            rmus = RMU.objects.all()
            rmu_serializer = RMUSerializer(rmus, many=True)
            return Response(
                {
                    "status": True,
                    "message": "RMU retrieved successfully",
                    "data": rmu_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DeleteRMUView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = RMUDeleteSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            id = serializer_class.validated_data["id"]
            component_name = serializer_class.validated_data["component_name"]

            rmu = RMU.objects.get(id=id,component_name=component_name)

            rmu.delete()
            return Response(
                {"status": True, "message": "RMU deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except RMU.DoesNotExist:
            return Response(
                {"status": False, "message": "RMU not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateRMUView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            rmu_id = request.data.get("id")
            existing_rmu = RMU.objects.get(id=rmu_id)
        except RMU.DoesNotExist:
            return Response(
                {"status": False, "message": "RMU not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RMUSerializer(existing_rmu, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer.save()
        
        return Response(
            {"status": True, "message": "RMU updated"},
            status=status.HTTP_200_OK,
        )


class MeteringPanelCreateView(APIView):
    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response(
                {"status": False, "message": "Expected a list of MeteringPanel"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = MeteringPanelSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            meteringpanels = serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "MeteringPanel created successfully",
                    "data": MeteringPanelSerializer(meteringpanels, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

class MeteringPanelListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            meteringpanels = MeteringPanel.objects.all()
            meteringpanel_serializer = MeteringPanelSerializer(meteringpanels, many=True)
            return Response(
                {
                    "status": True,
                    "message": "Metering Panels retrieved successfully",
                    "data": meteringpanel_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DeleteMeteringPanelView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = MeteringPanelDeleteSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            id = serializer_class.validated_data["id"]
            component_name = serializer_class.validated_data["component_name"]

            meteringpanel = MeteringPanel.objects.get(id=id,component_name=component_name)

            meteringpanel.delete()
            return Response(
                {"status": True, "message": "MeteringPanel deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except MeteringPanel.DoesNotExist:
            return Response(
                {"status": False, "message": "MeteringPanel not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateMeteringPanelView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            meteringpanel_id = request.data.get("id")
            existing_meteringpanel = MeteringPanel.objects.get(id=meteringpanel_id)
        except MeteringPanel.DoesNotExist:
            return Response(
                {"status": False, "message": "MeteringPanel not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MeteringPanelSerializer(existing_meteringpanel, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer.save()
        
        return Response(
            {"status": True, "message": "MeteringPanel updated"},
            status=status.HTTP_200_OK,
        )
        

class LTPanelCreateView(APIView):
    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response(
                {"status": False, "message": "Expected a list of LTPanel"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = LTPanelSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            ltpanels = serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "LTPanel created successfully",
                    "data": LTPanelSerializer(ltpanels, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

class LTPanelListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            ltpanels = LTPanel.objects.all()
            ltpanel_serializer = LTPanelSerializer(ltpanels, many=True)
            return Response(
                {
                    "status": True,
                    "message": "LT Panels retrieved successfully",
                    "data": ltpanel_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DeleteLTPanelView(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = LTPanelDeleteSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            id = serializer_class.validated_data["id"]
            description_of_item = serializer_class.validated_data["description_of_item"]

            ltpanel = LTPanel.objects.get(id=id,description_of_item=description_of_item)

            ltpanel.delete()
            return Response(
                {"status": True, "message": "LTPanel deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except LTPanel.DoesNotExist:
            return Response(
                {"status": False, "message": "LTPanel not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateLTPanelView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            ltpanel_id = request.data.get("id")
            existing_ltpanel = LTPanel.objects.get(id=ltpanel_id)
        except LTPanel.DoesNotExist:
            return Response(
                {"status": False, "message": "LTPanel not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LTPanelSerializer(existing_ltpanel, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer.save()
        
        return Response(
            {"status": True, "message": "LTPanel updated"},
            status=status.HTTP_200_OK,
        )
 

class ChargingScenarioCompareView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CompareScenarioSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "false", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = serializer.validated_data["project_id"]
            created_by = serializer.validated_data["created_by"]
            scenario_ids = serializer.validated_data["scenario_ids"]

            if len(scenario_ids) < 2:
                return Response(
                    {"error": "At least 2 scenario IDs are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            project = Project.objects.get(project_id=project_id, created_by=created_by)

            scenario_data = []
            for scenario_id in scenario_ids:
                data = self.calculate_scenario_data(project, scenario_id)
                scenario_data.append(data)

            return Response(
                {
                    "status": True,
                    "message": "Results fetched successfully",
                    "ScenarioResults": scenario_data,
                },
                status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def calculate_scenario_data(self, project, scenario_id):
        scenario_data = ChargingAnalysisScenario.objects.get(project_id=project, scenario_id=scenario_id)

        result_data = scenario_data.result

        inputdata = {
            "IsFeasible": result_data["IsFeasible"],
            "charger_system": result_data["charger_system"],
            "charging_schedule_df": result_data["charging_schedule_df"],
            "power_consumption_per_km": result_data["power_consumption_per_km"],
            "schedule_df": result_data["schedule_df"],
            "gvw": result_data["gvw"],
            "np_bc": result_data["np_bc"],
            "depot_df": result_data["depot_df"],
            "terminal_df": result_data["terminal_df"],
            "y_depot_dead_dict": result_data["y_depot_dead_dict"]
        }

        analytics_response_data = data_analytics(
            inputdata["charger_system"],
            inputdata["charging_schedule_df"],
            inputdata["power_consumption_per_km"],
            inputdata["schedule_df"],
            inputdata["gvw"],
            inputdata["np_bc"],
            inputdata["depot_df"],
            inputdata["terminal_df"],
            inputdata["y_depot_dead_dict"]
        )

        scenario_response_data = {
            "ScenarioID": scenario_id,
            "result_data": analytics_response_data
        }

        return scenario_response_data


class GetComponentsByDepotView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = GetComponentsByDepotSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "false", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            apparent_power = serializer.validated_data["apparent_power"]

            max_capacity = Transformer.objects.order_by('-capacity_kva').values_list('capacity_kva', flat=True).first()
            
            if max_capacity >= apparent_power:
            
                transformers = Transformer.objects.filter(
                    capacity_kva__gte=apparent_power
                ).order_by('capacity_kva')[:5]

            else:
                transformers = Transformer.objects.order_by('-capacity_kva')[:5]

            # if transformers.count() < 5:
            #     additional_transformers = Transformer.objects.exclude(
            #         id__in=transformers.values_list('id', flat=True)
            #     ).order_by('-capacity_kva')[:5 - transformers.count()]
            #     transformers = list(transformers) + list(additional_transformers)

            if not transformers:
                return Response(
                    {"message": "No suitable transformers found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            response_data = {"status": "success", "data": []}

            for transformer in transformers:
                current_capacity = apparent_power / transformer.voltage

                transmission_cable = HTCable.objects.filter(
                    voltage=transformer.voltage,
                    max_current_carrying_capacity__gte=current_capacity
                ).order_by('-max_current_carrying_capacity').last()

                rmu_component = RMU.objects.filter(
                    voltage=transformer.voltage,
                    capacity_kva__gte=apparent_power
                ).order_by('-capacity_kva').last()

                metering_panel_component = MeteringPanel.objects.filter(
                    voltage=transformer.voltage
                ).order_by('-amount').last()

                lt_panel_item = LTPanel.objects.filter(
                    current__gte=current_capacity
                ).order_by('current').first()

                transformer_data = TransformerSerializer(transformer).data
                transmission_cable_data = HTCableSerializer(transmission_cable).data if transmission_cable else None
                rmu_component_data = RMUSerializer(rmu_component).data if rmu_component else None
                metering_panel_component_data = MeteringPanelSerializer(metering_panel_component).data if metering_panel_component else None
                lt_panel_item_data = LTPanelSerializer(lt_panel_item).data if lt_panel_item else None

                response_data["data"].append({
                    "transformer": transformer_data,
                    "related_components": {
                        "transmission_cable": transmission_cable_data,
                        "rmu_component": rmu_component_data,
                        "metering_panel_component": metering_panel_component_data,
                        "lt_panel_item": lt_panel_item_data
                    }
                })

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalculateDistanceAndTransformersView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CalculateDistanceAndTransformersSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "false", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = serializer.validated_data["project_id"]
            created_by = serializer.validated_data["created_by"]
            depot_name = serializer.validated_data["depot_name"]
            apparent_power = serializer.validated_data["apparent_power"]
            substation_short_name = serializer.validated_data["substation_short_name"]
            transformer_name = serializer.validated_data["transformer_name"]
            htcable_name = serializer.validated_data["htcable_name"]
            rmu_name = serializer.validated_data["rmu_name"]
            meteringpanel_name = serializer.validated_data["meteringpanel_name"]
            ltpanel_name = serializer.validated_data["ltpanel_name"]
            busmodel_short_name = serializer.validated_data["busmodel_short_name"]
            no_of_buses  = serializer.validated_data["no_of_buses"]
            charger_short_name = serializer.validated_data["charger_short_name"]
            chargers = serializer.validated_data["chargers"]
            number_of_years = serializer.validated_data["number_of_years"]
        
            project = Project.objects.get(project_id=project_id, created_by=created_by)

            try:
                depot_or_terminal = Depot.objects.get(depot_name=depot_name, project_id=project)
            except Depot.DoesNotExist:
                depot_or_terminal = Terminal.objects.get(terminal_name=depot_name, project_id=project)

            substation = Substation.objects.get(short_name=substation_short_name, project_id=project)

            depot_coords = (depot_or_terminal.latitude, depot_or_terminal.longitude)
            substation_coords = (substation.latitude, substation.longitude)
            distance_km = geodesic(depot_coords, substation_coords).kilometers
            distance_m = distance_km * 1000 
            
            transformer = Transformer.objects.get(transformer=transformer_name)
            transformer_capacity = transformer.capacity_kva
            number_of_transformers = math.ceil(apparent_power / transformer_capacity)

            htcable = math.ceil(distance_m)
            cable_covering_tiles = math.ceil(distance_m)
            cable_laying = math.ceil(distance_m)
            route_joint_indicators = math.ceil(distance_m / 500)
            sand = math.ceil(0.06 * distance_m)
            rmu = number_of_transformers * 2
            metering_cubicle = number_of_transformers
            ltpanels = number_of_transformers
            ltcables = math.ceil(distance_m / 10)

            transformer_cost = math.ceil(transformer.total_cost * number_of_transformers)
            
            ht_cable = HTCable.objects.get(cable_type=htcable_name)
            ht_cable_cost = math.ceil(ht_cable.total_cost * (htcable/1000)) if ht_cable else 0
            
            rmu_model = RMU.objects.get(component_name=rmu_name)
            rmu_cost = math.ceil(rmu_model.cost * rmu) if rmu_model else 0
            
            metering_panel = MeteringPanel.objects.get(component_name=meteringpanel_name)
            metering_cubicle_cost = math.ceil(metering_panel.amount * metering_cubicle) if metering_panel else 0
            
            lt_panel_item = LTPanel.objects.get(description_of_item=ltpanel_name)
            lt_cable_cost = math.ceil(lt_panel_item.total * ltpanels) if lt_panel_item else 0
            
            charger_model = ChargerModel.objects.get(short_name=charger_short_name)
            chargers_cost = math.ceil(charger_model.charger_cost * chargers)

            bus_model = BusModel.objects.get(short_name=busmodel_short_name)
            buses_cost = math.ceil(bus_model.bus_cost * no_of_buses)

            capital_investment_estimate = math.ceil(
                transformer_cost + ht_cable_cost + rmu_cost +
                metering_cubicle_cost + lt_cable_cost + chargers_cost 
                )
            upstream = math.ceil(transformer_cost + ht_cable_cost + rmu_cost + metering_cubicle_cost)
            downstream = math.ceil(lt_cable_cost + chargers_cost)

            # Calculate percentages
            # buses_cost_percentage = math.ceil((buses_cost / capital_investment_estimate) * 100) if capital_investment_estimate else 0
            # upstream_percentage = math.ceil((upstream / capital_investment_estimate) * 100) if capital_investment_estimate else 0
            # downstream_percentage = math.ceil((downstream / capital_investment_estimate) * 100) if capital_investment_estimate else 0

            # annuity = math.ceil(capital_investment_estimate/number_of_years)

            infrastructure_require_response_data = {
                "no_of_buses": no_of_buses,
                "number_of_transformers_required": number_of_transformers,
                "distance_m": distance_m,
                "htcable": htcable,
                "cable_covering_tiles": cable_covering_tiles,
                "cable_laying": cable_laying,
                "route_joint_indicators": route_joint_indicators,
                "sand": sand,
                "rmu": rmu,
                "metering_cubicle": metering_cubicle,
                "chargers": chargers,
                "ltpanels": ltpanels,
                "ltcables": ltcables
            }

            inventory_cost_response_data = {
                "buses_cost": buses_cost,
                "transformer_cost": transformer_cost,
                "ht_cable_cost": ht_cable_cost,
                "rmu_cost": rmu_cost,
                "metering_cubicle_cost": metering_cubicle_cost,
                "lt_cable_cost": lt_cable_cost,
                "chargers_cost": chargers_cost,
                "capital_investment_estimate": capital_investment_estimate,
                "upstream": upstream,
                "downstream": downstream,
            }
            
            return Response(
                {
                    "status": True,
                    "message": "Results fetched successfully",
                    "infrastructure_require_response_data": infrastructure_require_response_data,
                    "inventory_cost_response_data": inventory_cost_response_data,
                },
                status=status.HTTP_200_OK)
        
        except Depot.DoesNotExist:
            return Response({"message": "Depot not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Substation.DoesNotExist:
            return Response({"message": "Substation not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Transformer.DoesNotExist:
            return Response({"message": "Transformer not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except ChargerModel.DoesNotExist:
            return Response({"message": "Charger model not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except BusModel.DoesNotExist:
            return Response({"message": "Bus model not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BatteryReplacementView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = BatteryReplacementSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "false", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = serializer.validated_data["project_id"]
            created_by = serializer.validated_data["created_by"]
            depotallocation_scenario_id = serializer.validated_data["depotallocation_scenario_id"]

            project = Project.objects.get(project_id=project_id, created_by=created_by)
            depot_scenario_data = DepotAllocationScenario.objects.get(project_id=project, scenario_id=depotallocation_scenario_id)

            schedules = DepotAllocation_Schedule.objects.filter(scenario=depot_scenario_data)
            new_schedule_df = pd.DataFrame.from_records(schedules.values())

            battery_cycles =serializer.validated_data["battery_cycles"]
            power_consumption_per_km =serializer.validated_data["power_consumption_per_km"]
            busmodel_short_name = serializer.validated_data["busmodel_short_name"]
            number_of_years =serializer.validated_data["number_of_years"]
            bus_crew_ratio = request.data.get('bus_crew_ratio')
            charger_crew_ratio = request.data.get('charger_crew_ratio')
            
            vehicle_utilization_data = []
            total_power_consumption = 0 
            
            for schedule_id in new_schedule_df['schedule_id'].unique():
                schedule = new_schedule_df[new_schedule_df['schedule_id'] == schedule_id]
                
                shuttle_trips = schedule[schedule['event_type'] == 'Non-revenue trip']
                total_shuttle_distance = sum(shuttle_trips['trip_distance'])
                
                revenue_trips = schedule[schedule['event_type'] != 'Non-revenue trip']
                total_revenue_distance = sum(revenue_trips['trip_distance'])
                
                total_distance = total_shuttle_distance + total_revenue_distance
                power_consumed = total_distance * power_consumption_per_km
                
                total_power_consumption += power_consumed 
                
                vehicle_utilization_data.append({
                    'schedule_id': schedule_id,
                    'dead_km': total_shuttle_distance,
                    'vehicle_utilization': total_distance,
                    'power_consumed': power_consumed
                })
            
            vehicle_utilization_df = pd.DataFrame(vehicle_utilization_data)

            bus_model = BusModel.objects.get(short_name=busmodel_short_name)
            name_plate_battery_capacity = bus_model.battery_capacity

            equivalent_distance = battery_cycles * name_plate_battery_capacity * power_consumption_per_km
            
            vehicle_utilization_df['replacement_year'] = round(equivalent_distance / vehicle_utilization_df['vehicle_utilization'] / 365, 1)
            vehicle_utilization_df['replacement_years'] = [
                np.arange(i, number_of_years + i, i) for i in vehicle_utilization_df['replacement_year']
            ]
            
            all_replacement_years = [year for sublist in vehicle_utilization_df['replacement_years'].tolist() for year in sublist]
            
            year_counts = Counter(all_replacement_years)

            # Round the years and sum the counts
            rounded_year_counts = Counter()
            for year, count in year_counts.items():
                rounded_year = str(math.ceil(float(year)))  # Round up the year
                rounded_year_counts[rounded_year] += count  # Sum the battery replacements

            # Determine the maximum year (either from data or the specified number_of_years)
            max_year = max(int(max(rounded_year_counts.keys())), number_of_years)

            # Ensure all years from 1 to max_year are included, with 0 for missing years
            complete_year_counts = {str(year): 0 for year in range(1, max_year + 1)}
            for year, count in rounded_year_counts.items():
                complete_year_counts[year] = count  

            # Convert to a sorted dictionary
            sorted_rounded_year_counts = dict(sorted(complete_year_counts.items(), key=lambda item: int(item[0])))

            filtered_sorted_rounded_year_counts = {
                year: count for year, count in sorted_rounded_year_counts.items() if int(year) <= number_of_years
            }

            filtered_sorted_years = list(filtered_sorted_rounded_year_counts.keys())
            filtered_sorted_battery_replacements = list(filtered_sorted_rounded_year_counts.values())
            
            total_dead_km = math.ceil(vehicle_utilization_df['dead_km'].sum())
            total_vehicle_utilization = math.ceil(vehicle_utilization_df['vehicle_utilization'].sum())
            total_power_consumption = math.ceil(total_power_consumption)
            
            response_data = {
                "year_counts": year_counts,
                "sorted_rounded_year_counts": sorted_rounded_year_counts,
                "years": filtered_sorted_years, 
                "battery_replacements": filtered_sorted_battery_replacements,
                "total_dead_km": total_dead_km,
                "total_vehicle_utilization": total_vehicle_utilization,
                "total_power_consumption": total_power_consumption,
                "schedule_power_consumption": vehicle_utilization_df[['schedule_id', 'vehicle_utilization', 'power_consumed']].to_dict(orient='records'),
            }
            
            return Response(
                {
                    "status": True,
                    "message": "results fetched successfully",
                    "response_data": response_data
                },
                status=status.HTTP_200_OK)
        
        except Project.DoesNotExist:
            return Response(
                {"status": "false", "message": "Project not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        except DepotAllocationScenario.DoesNotExist:
            return Response(
                {"status": "false", "message": "Depot Allocation Scenario not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        except Exception as e:
            return Response(
                {"status": "false", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

class OperationalCostCalculationView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            years = int(request.data.get("years"))
            bus_crew_size = int(request.data.get("bus_crew_size"))
            
            bus_crew_cost_per_day_value = request.data.get("bus_crew_cost_per_day")
            bus_crew_cost_per_day = float(bus_crew_cost_per_day_value) if bus_crew_cost_per_day_value is not None else 0.0

            bus_inflation_value = request.data.get("bus_inflation")
            bus_inflation = float(bus_inflation_value) / 100 if bus_inflation_value is not None else 0.0

            bus_insurance_per_year_value = request.data.get("bus_insurance_per_year")
            bus_insurance_per_year = float(bus_insurance_per_year_value) if bus_insurance_per_year_value is not None else 0.0

            charger_crew_size = int(request.data.get("charger_crew_size"))
            
            charger_crew_cost_per_day_value = request.data.get("charger_crew_cost_per_day")
            charger_crew_cost_per_day = float(charger_crew_cost_per_day_value) if charger_crew_cost_per_day_value is not None else 0.0

            charger_inflation_value = request.data.get("charger_inflation")
            charger_inflation = float(charger_inflation_value) / 100 if charger_inflation_value is not None else 0.0

            charger_insurance_per_year_value = request.data.get("charger_insurance_per_year")
            charger_insurance_per_year = float(charger_insurance_per_year_value) if charger_insurance_per_year_value is not None else 0.0

            bus_model_short_name = request.data.get("bus_model_short_name")
            batteries_per_year = request.data.get("batteries_per_year")
            
            battery_inflation_value = request.data.get("battery_inflation")
            battery_inflation = float(battery_inflation_value) / 100 if battery_inflation_value is not None else 0.0

            power_consumption_per_day = float(request.data.get("power_consumption_per_day"))
            power_rate_per_unit = float(request.data.get("power_rate_per_unit"))

            power_inflation_value = request.data.get("power_inflation")
            power_inflation = float(power_inflation_value) / 100 if power_inflation_value is not None else 0.0

            total_distance = float(request.data.get("total_distance"))

            maintenance_cost_per_km_value = request.data.get("maintenance_cost_per_km")
            maintenance_cost_per_km = float(maintenance_cost_per_km_value) if maintenance_cost_per_km_value is not None else 0.0

            maintenance_inflation_value = request.data.get("maintenance_inflation")
            maintenance_inflation = float(maintenance_inflation_value) / 100 if maintenance_inflation_value is not None else 0.0

            no_of_buses = request.data.get("no_of_buses")
            
            bus_model = BusModel.objects.get(short_name=bus_model_short_name)
            battery_cost = float(bus_model.battery_cost)  

            result = self.calculate_costs(
                years, bus_crew_size, bus_crew_cost_per_day, bus_inflation, 
                bus_insurance_per_year, charger_crew_size, charger_crew_cost_per_day, 
                charger_inflation, charger_insurance_per_year, battery_cost, 
                batteries_per_year, battery_inflation, power_consumption_per_day, 
                power_rate_per_unit, power_inflation, total_distance, 
                maintenance_cost_per_km, maintenance_inflation, no_of_buses
            )

            return Response(result, status=status.HTTP_200_OK)
        
        except KeyError as e:
            return Response({"error": f"Missing key: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def calculate_costs(self, years, bus_crew_size, bus_crew_cost_per_day, bus_inflation, 
                    bus_insurance_per_year, charger_crew_size, charger_crew_cost_per_day, 
                    charger_inflation, charger_insurance_per_year, battery_cost, 
                    batteries_per_year, battery_inflation, power_consumption_per_day, 
                    power_rate_per_unit, power_inflation, total_distance, 
                    maintenance_cost_per_km, maintenance_inflation, no_of_buses):         
    
        results = []
        for year in range(1, years + 1):
        
            bus_crew_cost = bus_crew_size * bus_crew_cost_per_day * 365 * (1 + bus_inflation) ** (year - 1)
            charger_crew_cost = charger_crew_size * charger_crew_cost_per_day * 365 * (1 + charger_inflation) ** (year - 1)
            crew_cost = bus_crew_cost + charger_crew_cost 

            battery_yearly_cost = float(batteries_per_year.get(str(year), 0)) * battery_cost * (1 + battery_inflation) ** (year - 1)
            
            power_cost = power_consumption_per_day * power_rate_per_unit * 365 * (1 + power_inflation) ** (year - 1)
                        
            maintenance_cost = 365 * total_distance * maintenance_cost_per_km * (1 + maintenance_inflation) ** (year - 1)
            maintenance_cost += bus_insurance_per_year * no_of_buses 
            
            total_cost = crew_cost + battery_yearly_cost + power_cost + maintenance_cost
            
            results.append({
                'Year': year,
                'Crew Cost': int(crew_cost),
                'Battery Cost': int(battery_yearly_cost),
                'Power Cost': int(power_cost),
                'Maintenance Cost': int(maintenance_cost),
                'Total Cost': int(total_cost)
            })
        
        return results


class SalvageCostEstimationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SalvageCostEstimationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "false", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            components = serializer.validated_data["components"]
            deflation_rate = serializer.validated_data["deflation_rate"]
            total_years = serializer.validated_data["total_years"]

            yearly_costs = {}

            for year in range(1, total_years + 1):
                yearly_costs[year] = {}

                if "Buses" in components:
                    bus_model = BusModel.objects.get(short_name=components["Buses"]["bus_name"])
                    bus_initial_cost = Decimal(bus_model.bus_cost)

                    if year == total_years:
                        number_of_units = Decimal(components["Buses"]["number_of_units"])
                        cost_at_year = self.calculate_replacement_cost(
                            bus_initial_cost,
                            number_of_units,
                            deflation_rate["Buses"],
                            year
                        )
                        yearly_costs[year]["Buses"] = cost_at_year
                    else: 
                        yearly_costs[year]["Buses"] = 0

                if "Transformers" in components:
                    transformer_total_cost = 0

                    for transformer_name, number_of_units in components["Transformers"]["transformer_data"].items():
                        transformer_model = Transformer.objects.get(transformer=transformer_name)
                        transformer_initial_cost = Decimal(transformer_model.total_cost)

                        if year == total_years:

                            cost_at_year = self.calculate_replacement_cost(
                                transformer_initial_cost,
                                number_of_units,
                                deflation_rate["Transformers"],
                                year
                            )
                            transformer_total_cost += cost_at_year
                        else:
                            transformer_total_cost = 0

                    yearly_costs[year]["Transformers"] = transformer_total_cost

                if "Chargers" in components:
                    charger_total_cost = 0

                    for charger_name, number_of_units in components["Chargers"]["charger_data"].items():
                        charger_model = ChargerModel.objects.get(short_name=charger_name)
                        charger_initial_cost = Decimal(charger_model.charger_cost)

                        if year == total_years:
                        
                            cost_at_year = self.calculate_replacement_cost(
                                charger_initial_cost,
                                number_of_units,
                                deflation_rate["Chargers"],
                                year
                            )
                            charger_total_cost += cost_at_year
                        else:
                            charger_total_cost = 0

                    yearly_costs[year]["Chargers"] = charger_total_cost

                if "Batteries" in components:
                    bus_model = BusModel.objects.get(short_name=components["Batteries"]["bus_name"])  
                    battery_initial_cost = Decimal(bus_model.battery_cost)
                    
                    number_of_units_per_year = components["Batteries"]["number_of_units_per_year"]
                    number_of_units = number_of_units_per_year[str(year)]

                    cost_at_year = self.calculate_replacement_cost(
                        battery_initial_cost,
                        number_of_units,
                        deflation_rate["Batteries"],
                        year
                    )
                    yearly_costs[year]["Batteries"] = cost_at_year

                yearly_costs[year]["total_salvage_cost"] = yearly_costs[year]["Buses"] + yearly_costs[year]["Transformers"] + yearly_costs[year]["Chargers"] + yearly_costs[year]["Batteries"]

            return Response(
                {
                    "status": True,
                    "message": "results fetched successfully",
                    "yearly_costs": yearly_costs
                },
                status=status.HTTP_200_OK)

        except KeyError as e:
            return Response({"error": f"Missing key: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def calculate_replacement_cost(self, initial_cost_per_unit, number_of_units, deflation_rate_percent, year):
      
        initial_cost_per_unit = Decimal(initial_cost_per_unit)
        number_of_units = Decimal(number_of_units)

        try:
            deflation_rate_percent = Decimal(deflation_rate_percent) / Decimal('100.0') if deflation_rate_percent is not None else Decimal('0.0')
        except InvalidOperation:
            deflation_rate_percent = Decimal('0.0')

        initial_cost = initial_cost_per_unit * number_of_units

        replacement_cost = initial_cost * (deflation_rate_percent) 
        replacement_cost = math.ceil(replacement_cost) 
        return replacement_cost


class CreateDesignEbusScenarioView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CreateDesignEbusScenarioSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "false", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = serializer.validated_data["project_id"]
            created_by = serializer.validated_data["created_by"]
            project = Project.objects.get(project_id=project_id, created_by=created_by)

            scenario_name = serializer.validated_data["scenario_name"]
            description = serializer.validated_data["description"]
            inventory_indicators = serializer.validated_data["inventory_indicators"]
            performance_indicators = serializer.validated_data["performance_indicators"]
            financial_indicators = serializer.validated_data["financial_indicators"]
            charging_scenario_id = serializer.validated_data["charging_scenario_id"]
            cashflow_inputs = serializer.validated_data["cashflow_inputs"]

            no_of_years = int(cashflow_inputs["no_of_years"])
            operational_costs = cashflow_inputs["operational_costs"]
            annuity_per_year = float(cashflow_inputs["annuity_per_year"])
            battery_replacements = cashflow_inputs["battery_replacements"]
            salvage_costs = cashflow_inputs["salvage_costs"]

            cashflow_results = []

            for year in range(1, no_of_years + 1):
                outflow_operational_costs = int(next(
                    (cost['total_cost'] for cost in operational_costs if cost['year'] == year), 0))
                outflow_annuity = int(annuity_per_year)

                total_outflow_cash = int(outflow_operational_costs + outflow_annuity)

                batteries_replaced = battery_replacements.get(str(year), 0)
                inflow_residual = 0
                if batteries_replaced > 0:
                    inflow_residual = int(next(
                        (sv['total_salvage_cost'] for sv in salvage_costs if sv['year'] == year), 0))

                netflow_cash = int(total_outflow_cash - inflow_residual)

                cashflow_results.append({
                    'year': year,
                    'outflow_operational_costs': outflow_operational_costs,
                    'outflow_annuity': outflow_annuity,
                    'inflow_residual': inflow_residual,
                    'total_outflow_cash': total_outflow_cash,
                    'netflow_cash': netflow_cash,

                })

            design_requestdata={
                "inventory_indicators": inventory_indicators,
                "performance_indicators": performance_indicators,
                "financial_indicators":  financial_indicators,
                "charging_scenario_id": charging_scenario_id,
                "cashflow_inputs": cashflow_inputs
            }

            design_result = {
                "inventory_indicators": inventory_indicators,
                "performance_indicators": performance_indicators,
                "financial_indicators":  financial_indicators, 
                "charging_scenario_id": charging_scenario_id,                   
                "cashflow_results": cashflow_results,
            }

            scenario = DesignEbusScenario.objects.create(
                scenario_name=scenario_name,
                description=description,
                design_requestdata=design_requestdata,
                design_result=design_result,
                project_id=project,
                )
            scenario.save()

            response_data = (DesignEbusScenarioSerializer(scenario).data,)

            return Response(
                {
                    "status": True,
                    "message": "scenario created successfully",
                    "scenario_id": scenario.scenario_id,
                    "scenario": response_data,
                },status=status.HTTP_200_OK)


        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        except BusModel.DoesNotExist:
            return Response(
                {"error": "Bus model not found."}, status=status.HTTP_404_NOT_FOUND
                )        

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DesignEbusScenarioResultsView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ChargingAnalysisResultsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "false", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = serializer.validated_data["project_id"]
            created_by = serializer.validated_data["created_by"]
            project = Project.objects.get(project_id=project_id, created_by=created_by)

            scenario_id = serializer.validated_data["scenario_id"]

            design_scenario_data = DesignEbusScenario.objects.get(project_id=project, scenario_id=scenario_id)
            
            scenario_name = design_scenario_data.scenario_name
            description = design_scenario_data.description
            design_results = design_scenario_data.design_result
            
            inventory_indicators = design_results["inventory_indicators"]
            performance_indicators = design_results["performance_indicators"]
            financial_indicators = design_results["financial_indicators"]
            cashflow_results = design_results["cashflow_results"]
            charging_scenario_id = design_results["charging_scenario_id"]

            scenario_data = ChargingAnalysisScenario.objects.get(project_id=project, scenario_id=charging_scenario_id)

            charging_result_data = scenario_data.result

            inputdata = {
                "IsFeasible": charging_result_data["IsFeasible"],
                "charger_system": charging_result_data["charger_system"],
                "charging_schedule_df": charging_result_data["charging_schedule_df"],
                "power_consumption_per_km": charging_result_data["power_consumption_per_km"],
                "schedule_df": charging_result_data["schedule_df"],
                "gvw": charging_result_data["gvw"],
                "np_bc": charging_result_data["np_bc"],
                "depot_df": charging_result_data["depot_df"],
                "terminal_df": charging_result_data["terminal_df"],
                "y_depot_dead_dict": charging_result_data["y_depot_dead_dict"]
            }

            analytics_response_data = data_analytics(
                inputdata["charger_system"],
                inputdata["charging_schedule_df"],
                inputdata["power_consumption_per_km"],
                inputdata["schedule_df"],
                inputdata["gvw"],
                inputdata["np_bc"],
                inputdata["depot_df"],
                inputdata["terminal_df"],
                inputdata["y_depot_dead_dict"]
            )
            response_data = {
                "scenario_name": scenario_name,
                "description": description,
                "inventory_indicators": inventory_indicators,
                "performance_indicators": performance_indicators,
                "financial_indicators": financial_indicators,
                "cashflow_results": cashflow_results,
                "charging_analysis_results": analytics_response_data
            }

            return Response(
                {
                    "status": True,
                    "message": "results fetched successfully",
                    "scenario_id": scenario_id,
                    "response_data": response_data
                },
                status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            ) 

        except DesignEbusScenario.DoesNotExist:
            return Response(
                {"error": "Scenario not found."}, status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListDesignEbusScenarios(APIView):
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
                scenarios = (
                    DesignEbusScenario.objects.filter(project_id=project_id)
                    .order_by("-scenario_id")
                    .values()
                )
                paginator = Paginator(scenarios, params["pageSize"])
                page = paginator.page(params["pageNumber"])

                return Response(
                    {
                        "status": True,
                        "total_scenarios": paginator.count,
                        "message": "Design Ebus Scenarios list",
                        "scenarios": list(page),
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                error_message = str(e)
                return Response(
                    {"message": error_message}, status=status.HTTP_404_NOT_FOUND
                )


class UpdateDesignEbusScenarioView(APIView):
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
                existing_scenario = DesignEbusScenario.objects.get(scenario_id=scenario_id)
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


class DeleteDesignEbusScenario(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = ScenarioDeleteSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": False, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            scenario_id = serializer_class.validated_data["scenario_id"]

            scenario = DesignEbusScenario.objects.get(scenario_id=scenario_id)

            scenario.delete()

            return Response(
                {"status": True, "message": "Design Ebus Scenario deleted"},
                status=status.HTTP_200_OK,
            )

        except DesignEbusScenario.DoesNotExist:
            return Response(
                {"status": False, "message": "Design Ebus Scenario not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DesignEbusScenarioCompareView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CompareScenarioSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "false", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project_id = serializer.validated_data["project_id"]
            created_by = serializer.validated_data["created_by"]
            scenario_ids = serializer.validated_data["scenario_ids"]

            if len(scenario_ids) < 2:
                return Response(
                    {"error": "At least 2 scenario IDs are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            project = Project.objects.get(project_id=project_id, created_by=created_by)

            scenario_data = []
            for scenario_id in scenario_ids:
                data = self.calculate_scenario_data(project, scenario_id)
                scenario_data.append(data)

            return Response(
                {
                    "status": True,
                    "message": "Results fetched successfully",
                    "ScenarioResults": scenario_data,
                },
                status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def calculate_scenario_data(self, project, scenario_id):
        design_scenario_data = DesignEbusScenario.objects.get(project_id=project, scenario_id=scenario_id)
            
        scenario_name = design_scenario_data.scenario_name
        description = design_scenario_data.description
        design_results = design_scenario_data.design_result
        
        inventory_indicators = design_results["inventory_indicators"]
        performance_indicators = design_results["performance_indicators"]
        financial_indicators = design_results["financial_indicators"]
        cashflow_results = design_results["cashflow_results"]
        charging_scenario_id = design_results["charging_scenario_id"]

        scenario_data = ChargingAnalysisScenario.objects.get(project_id=project, scenario_id=charging_scenario_id)

        charging_result_data = scenario_data.result

        inputdata = {
            "IsFeasible": charging_result_data["IsFeasible"],
            "charger_system": charging_result_data["charger_system"],
            "charging_schedule_df": charging_result_data["charging_schedule_df"],
            "power_consumption_per_km": charging_result_data["power_consumption_per_km"],
            "schedule_df": charging_result_data["schedule_df"],
            "gvw": charging_result_data["gvw"],
            "np_bc": charging_result_data["np_bc"],
            "depot_df": charging_result_data["depot_df"],
            "terminal_df": charging_result_data["terminal_df"],
            "y_depot_dead_dict": charging_result_data["y_depot_dead_dict"]
        }

        analytics_response_data = data_analytics(
            inputdata["charger_system"],
            inputdata["charging_schedule_df"],
            inputdata["power_consumption_per_km"],
            inputdata["schedule_df"],
            inputdata["gvw"],
            inputdata["np_bc"],
            inputdata["depot_df"],
            inputdata["terminal_df"],
            inputdata["y_depot_dead_dict"]
        )
        
        response_data = {
            "scenario_name": scenario_name,
            "description": description,
            "inventory_indicators": inventory_indicators,
            "performance_indicators": performance_indicators,
            "financial_indicators": financial_indicators,
            "cashflow_results": cashflow_results,
            "charging_analysis_results": analytics_response_data
        }


        scenario_response_data = {
            "ScenarioID": scenario_id,
            "response_data": response_data
        }

        return scenario_response_data


class ProjectNameValidationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ProjectNameValidationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            created_by = serializer.validated_data["created_by"]
            project_name = serializer.validated_data["project_name"]
            
            if Project.objects.filter(created_by=created_by,project_name=project_name).exists():
                return Response({
                    "status": False, 
                    "message": "Project name already exists"
                }, status=status.HTTP_200_OK)
            
            else:
                return Response({
                    "status": True, 
                    "message": "Project name is valid"
                }, status=status.HTTP_200_OK)
        
        except Project.DoesNotExist:
            return Response(
                {"status": False, "message": "Project not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        
class ScenarioNameValidationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ScenarioNameValidationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            project_id = serializer.validated_data["project_id"]
            created_by = serializer.validated_data["created_by"]
            workflow_type = serializer.validated_data["workflow_type"]
            scenario_name = serializer.validated_data["scenario_name"]
            
            project = Project.objects.get(
                project_id=project_id,
                created_by=created_by,
                workflow_type=workflow_type
            )
            
            scenario_exists = False

            if workflow_type == 1:
                scenario_exists = Scenario.objects.filter(
                    scenario_name=scenario_name, 
                    project_id=project
                ).exists()

            elif workflow_type == 2:
                scenario_exists = DesignEbusScenario.objects.filter(
                    scenario_name=scenario_name, 
                    project_id=project
                ).exists()
                
            elif workflow_type == 3:
                scenario_exists = ChargingAnalysisScenario.objects.filter(
                    scenario_name=scenario_name, 
                    project_id=project
                ).exists()

            if scenario_exists:
                return Response({
                    "status": False, 
                    "message": "Scenario name already exists"
                }, status=status.HTTP_200_OK)
            
            return Response({
                "status": True, 
                "message": "Scenario name is valid"
            }, status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response(
                {"status": False, "message": "Project not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

class ObjectiveFunctionView(APIView):
    def get(self, request, *args, **kwargs):
        params = {
            "project_id": request.GET.get("project_id"),
            "created_by": request.GET.get("created_by")
        }
        serializer_class = SubmitProjectSerializer(data=params)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            project_id = params["project_id"]
            created_by = params["created_by"]

            try:
                project = Project.objects.get(
                    project_id=project_id, created_by=created_by
                )

                objective_function = ObjectiveFunctions.objects.filter(project_id=project).last()

                if objective_function is None:
                    return Response(
                        {
                            "status": False, 
                            "message": "No objective function found for this project.",
                            "objective_function": None
                        },
                        status=status.HTTP_200_OK
                    )

                return Response(
                    {
                        "status": True, 
                        "message": "Found Objective Function", 
                        "objective_function": objective_function.object_value
                    },
                    status=status.HTTP_200_OK
                )

            except Project.DoesNotExist:
                return Response(
                    {"status": False, "message": "Project not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception as e:
                return Response(
                    {"status": False, "message": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
