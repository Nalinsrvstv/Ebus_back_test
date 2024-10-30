from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from ..serializer import (
    CreateProjectSerializer,
    GetAllProjectsSerializer,
    RenameProjectSerializer,
    RenameDuplicateSerializer,
    RenameDeleteSerializer,
    SubmitProjectSerializer,
    ProjectSummarySerializer,
    GetProjectByIdSerializer,
    GetDepotSerializer,
    GetScheduleSerializer,
    GetTerminalSerializer,
    GetSubstationSerializer
)
from rest_framework import status
from usersmanagement.models import CustomUser
from ..models import (
    Project,
    Schedule,
    Depot,
    Terminal,
    Substation
)
from django.core.paginator import Paginator


class ListProject(APIView):
    def get(self, request, *args, **kwargs):
        params = {
            "created_by": request.GET.get("created_by"),
            "pageNumber": request.GET.get("pageNumber"),
            "pageSize": request.GET.get("pageSize"),
            "searchKey": request.GET.get("searchKey"),
            "workflow_type": request.GET.get("workflow_type"),
        }
        serializer_class = GetAllProjectsSerializer(data=params)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            created_by = params["created_by"]
            workflow_type = params["workflow_type"]
            print(workflow_type)
            try:
                projects = (
                    Project.objects.filter(
                        created_by=created_by,
                        workflow_type=workflow_type,
                        project_name__contains=params["searchKey"],
                        is_submitted=True,
                    )
                    .order_by("-project_id")
                    .values()
                )
                paginator = Paginator(projects, params["pageSize"])
                page = paginator.get_page(params["pageNumber"])
                return Response(
                    {
                        "status": True,
                        "totalprojects": len(projects),
                        "message": "project list",
                        "projects": list(page),
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response({"message": e}, status=status.HTTP_404_NOT_FOUND)


class CreateProject(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = CreateProjectSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:

            # Serializing the data from the JSON response from the front end
            username = serializer_class.validated_data["created_by"]
            schedule_data = serializer_class.validated_data["schedule_data"]
            depot_data = serializer_class.validated_data["depot_data"]
            terminals_data = serializer_class.validated_data["terminals_data"]
            workflow_type = serializer_class.validated_data.get("workflow_type")

            # If workflow_type is 2, we expect substation_data
            substation_data = []
            if workflow_type == 2:
                substation_data = serializer_class.validated_data["substation_data"]

            # check if user exists with the given username
            try:
                user = CustomUser.objects.get(username=username)
                # Create Porject Object
                project = Project(
                    created_by=serializer_class.validated_data["created_by"],
                    user_id=user,
                    project_name=serializer_class.validated_data["project_name"],
                    description=serializer_class.validated_data.get(
                        "description", "No Description"
                    ),
                    workflow_type=workflow_type,
                    is_submitted=False,
                )
                project.save()

                # Save the project to DB
                # Save the project and schedule, terminal and Depot to DB
                for schedule_object in schedule_data:
                    s_obj = Schedule.objects.create(
                        project_id=project,
                        schedule_id=schedule_object["schedule_id"],
                        trip_number=schedule_object["trip_number"],
                        route_number=schedule_object["route_number"],
                        direction=schedule_object["direction"],
                        start_terminal=schedule_object["start_terminal"],
                        end_terminal=schedule_object["end_terminal"],
                        start_time=schedule_object["start_time"],
                        travel_time=schedule_object["travel_time"],
                        trip_distance=schedule_object["trip_distance"],
                        crew_id=schedule_object["crew_id"],
                        event_type=schedule_object["event_type"],
                        operator=schedule_object["operator"],
                        ac_non_ac=schedule_object["ac_non_ac"],
                        brt_non_brt=schedule_object["brt_non_brt"],
                        service_type=schedule_object["service_type"],
                        fuel_type=schedule_object["fuel_type"],
                        bus_type=schedule_object["bus_type"],
                        depot_id=schedule_object["depot_id"],
                    )

                for depot_oject in depot_data:
                    d_obj = Depot.objects.create(
                        project_id=project,
                        depot_id=depot_oject["depot_id"],
                        depot_name=depot_oject["depot_name"],
                        latitude=depot_oject["latitude"],
                        longitude=depot_oject["longitude"],
                        capacity=depot_oject["capacity"],
                        operator=depot_oject["operator"],
                        ac_non_ac=depot_oject["ac_non_ac"],
                        brt_non_brt=depot_oject["brt_non_brt"],
                        service_type=depot_oject["service_type"],
                        fuel_type=depot_oject["fuel_type"],
                        bus_type=depot_oject["bus_type"],
                    )

                for terminals_object in terminals_data:
                    t_obj = Terminal.objects.create(
                        project_id=project,
                        terminal_id=terminals_object["terminal_id"],
                        terminal_name=terminals_object["terminal_name"],
                        latitude=terminals_object["latitude"],
                        longitude=terminals_object["longitude"],
                        terminal_area=terminals_object["terminal_area"],
                    )

                # Save terminal file content to DB
                # project.save()
                if workflow_type == 2:
                    for substation_object in substation_data:
                        Substation.objects.create(
                            project_id=project,
                            short_name=substation_object["short_name"],
                            long_name=substation_object["long_name"],
                            latitude=substation_object["latitude"],
                            longitude=substation_object["longitude"],
                        )

                response_data = (ProjectSummarySerializer(project).data,)

                return Response(
                    {
                        "status": True,
                        "message": "project created",
                        "details": response_data,
                    },
                    status=status.HTTP_200_OK,
                )

            except Exception as e:

                return Response(
                    {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            except CustomUser.DoesNotExist:
                return Response(
                    {"message": "Username not found."}, status=status.HTTP_404_NOT_FOUND
                )


class ProjecRename(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = RenameProjectSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:

            # Serializing the data from the JSON response from the front end
            username = serializer_class.validated_data["created_by"]
            project_name = serializer_class.validated_data["project_name"]
            project_new_name = serializer_class.validated_data["project_new_name"]
            project_id = serializer_class.validated_data["project_id"]

            # check if user and project exists with the given username and project_name
            try:
                existing_user = CustomUser.objects.get(username=username)

                existing_project = Project.objects.get(project_id=project_id)
                existing_project.project_name = project_new_name
                existing_project.save()
                return Response(
                    {"status": True, "message": "project renamed"},
                    status=status.HTTP_200_OK,
                )

            except Exception as e:

                return Response(
                    {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            except CustomUser.DoesNotExist:
                return Response(
                    {"message": "Username not found."}, status=status.HTTP_404_NOT_FOUND
                )


class projectDuplicate(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = RenameDuplicateSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:

            # Serializing the data from the JSON response from the front end
            username = serializer_class.validated_data["created_by"]
            project_id = serializer_class.validated_data["project_id"]

            # check if user and project exists with the given username and project_name
            try:
                existing_user = CustomUser.objects.get(username=username)
                existing_project = Project.objects.get(project_id=project_id)

                def clone(instance):
                    instance.pk = None
                    instance.save()
                    return instance

                depot_instance = Depot.objects.filter(
                    project_id=existing_project.project_id
                )
                terminal_instance = Terminal.objects.filter(
                    project_id=existing_project.project_id
                )
                schedule_instance = Schedule.objects.filter(
                    project_id=existing_project.project_id
                )

                clone_project_instance = clone(existing_project)

                # From the existing project get all the instance of the depot
                for depot_obj in depot_instance:
                    depot_obj.project_id = clone_project_instance
                    clone(depot_obj)

                # From the existing project get all the instance of the terminal
                for terminal_obj in terminal_instance:
                    terminal_obj.project_id = clone_project_instance
                    clone(terminal_obj)

                # From the existing project get all the instance of the terminal
                for schedule_obj in schedule_instance:
                    schedule_obj.project_id = clone_project_instance
                    clone(schedule_obj)

                return Response(
                    {"status": True, "message": "project duplicated"},
                    status=status.HTTP_200_OK,
                )

            except Exception as e:

                return Response(
                    {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            except CustomUser.DoesNotExist:
                return Response(
                    {"message": "Username not found."}, status=status.HTTP_404_NOT_FOUND
                )


class projectDelete(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = RenameDeleteSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:

            # Serializing the data from the JSON response from the front end
            username = serializer_class.validated_data["created_by"]
            project_name = serializer_class.validated_data["project_name"]
            project_id = serializer_class.validated_data["project_id"]

            # check if user and project exists with the given username and project_name
            try:
                existing_user = CustomUser.objects.get(username=username)
                existing_project = Project.objects.get(project_id=project_id)
                id_existing_depot = Depot.objects.filter(
                    project_id=existing_project.project_id
                )
                id_existing_schedule = Schedule.objects.filter(
                    project_id=existing_project.project_id
                )
                id_existing_terminal = Terminal.objects.filter(
                    project_id=existing_project.project_id
                )
                id_existing_schedule.delete()
                id_existing_terminal.delete()
                id_existing_depot.delete()
                existing_project.delete()
                return Response(
                    {"status": True, "message": "project deleted"},
                    status=status.HTTP_200_OK,
                )

            except Exception as e:

                return Response(
                    {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            except CustomUser.DoesNotExist:
                return Response(
                    {"message": "Username not found."}, status=status.HTTP_404_NOT_FOUND
                )


class ProjectSummaryView(APIView):
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

            # Retrieving the project details
            project = Project.objects.get(
                project_id=project_id, created_by=created_by, project_name=project_name
            )

            # Fetch data from the database based on the project information
            schedules = Schedule.objects.filter(project_id=project)

            # System Summary
            system_sum = schedules.aggregate(
                routes_count=Count("route_number", distinct=True),
                schedules_count=Count("schedule_id", distinct=True),
                system_distance=Sum("trip_distance"),
                dead_km=Sum("trip_distance", filter=Q(event_type="Non-revenue trip")),
            )

            # Depot Summary
            depot_sum = schedules.values("depot_id").annotate(
                routes_by_depot=Count("route_number", distinct=True),
                schedules_by_depot=Count("schedule_id", distinct=True),
                distance_by_depot=Sum("trip_distance"),
                dead_km_by_depot=Sum(
                    "trip_distance", filter=Q(event_type="Non-revenue trip")
                ),
            )

            # Calculate total system scheduled distance
            total_system_distance = schedules.aggregate(
                total_distance=Sum("trip_distance")
            )["total_distance"]

            # Additional logic for total system scheduled distance percentage
            total_system_distance_percentage = (
                system_sum["system_distance"] / total_system_distance
            ) * 100

            # Visualization Data
            visualization_data = {
                "dead_km_percentage": (
                    system_sum["dead_km"] / system_sum["system_distance"]
                )
                * 100,
                "total_system_distance_percentage": total_system_distance_percentage,
                "schedules_by_route": list(
                    schedules.values("route_number")
                    .annotate(route_count=Count("schedule_id", distinct=True))
                    .order_by("-route_count")
                ),
                "stacked_bars": {
                    "operator": list(
                        schedules.values("operator").annotate(
                            category_count=Count("schedule_id", distinct=True)
                        )
                    ),
                    "ac_non_ac": list(
                        schedules.values("ac_non_ac").annotate(
                            category_count=Count("schedule_id", distinct=True)
                        )
                    ),
                    "brt_non_brt": list(
                        schedules.values("brt_non_brt").annotate(
                            category_count=Count("schedule_id", distinct=True)
                        )
                    ),
                    "service_type": list(
                        schedules.values("service_type").annotate(
                            category_count=Count("schedule_id", distinct=True)
                        )
                    ),
                    "fuel_type": list(
                        schedules.values("fuel_type").annotate(
                            category_count=Count("schedule_id", distinct=True)
                        )
                    ),
                    "bus_type": list(
                        schedules.values("bus_type").annotate(
                            category_count=Count("schedule_id", distinct=True)
                        )
                    ),
                },
            }

            # Creating a new dictionary to hold the response data
            response_data = {
                "status": "success",
                "projectDetails": {
                    "project": ProjectSummarySerializer(project).data,
                    "systemSummary": system_sum,
                    "depotSummary": depot_sum,
                },
                "visualization": visualization_data,
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


class SubmitProject(APIView):
    def post(self, request, *args, **kwargs):
        serializer_class = SubmitProjectSerializer(data=request.data)
        if not serializer_class.is_valid():
            return Response(
                {"status": True, "message": serializer_class.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            # Serializing the data from the JSON response from the front end
            _project_id = serializer_class.validated_data["project_id"]
            _created_by = serializer_class.validated_data["created_by"]

            # check if the project is created by the same user who is submitting it
            try:
                existing_project = Project.objects.get(
                    Q(created_by=_created_by) & Q(project_id=_project_id)
                )
                existing_project.is_submitted = True
                existing_project.save()
                return Response(
                    {"status": True, "message": "Project submitted successfully"},
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except CustomUser.DoesNotExist:
                return Response(
                    {"message": "Username not found."}, status=status.HTTP_404_NOT_FOUND
                )


class GetProjectById(APIView):
    def get(self, request, *args, **kwargs):
        project_id = request.GET.get("project_id")
        workflow_type = request.GET.get("workflow_type")

        try:
            if not project_id:
                return Response(
                    {"status": False, "message": "Project ID is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not workflow_type:
                return Response(
                    {"status": False, "message": "Workflow type is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            workflow_type = int(workflow_type)
            project = Project.objects.get(project_id=project_id, workflow_type=workflow_type)

            # Retrieve depot data
            depots = Depot.objects.filter(project_id=project)
            depot_serializer_data = GetDepotSerializer(depots, many=True).data

            # Retrieve schedule data
            schedules = Schedule.objects.filter(project_id=project)
            schedule_serializer_data = GetScheduleSerializer(schedules, many=True).data

            # Retrieve terminal data
            terminals = Terminal.objects.filter(project_id=project)
            terminal_serializer_data = GetTerminalSerializer(terminals, many=True).data

            # Prepare the project response
            project_serializer = GetProjectByIdSerializer(project)
            response_data = {
                "project": project_serializer.data,
                "depot": {
                    "json": depot_serializer_data,
                    "fileHeader": [],
                    "filename": "",
                    "validated": False,
                    "selectedColumns": {},
                },
                "schedule": {
                    "json": schedule_serializer_data,
                    "fileHeader": [],
                    "filename": "",
                    "validated": False,
                    "selectedColumns": {},
                },
                "terminal": {
                    "json": terminal_serializer_data,
                    "fileHeader": [],
                    "filename": "",
                    "validated": False,
                    "selectedColumns": {},
                },
            }

            # Include substation data only if workflow_type is 2
            if workflow_type == 2:
                substations = Substation.objects.filter(project_id=project)
                substation_serializer_data = GetSubstationSerializer(substations, many=True).data
                response_data["substation"] = {
                    "json": substation_serializer_data,
                    "fileHeader": [],
                    "filename": "",
                    "validated": False,
                    "selectedColumns": {},
                }

            return Response(
                {
                    "status": True,
                    "message": "Project retrieved successfully",
                    **response_data,
                },
                status=status.HTTP_200_OK,
            )
        except Project.DoesNotExist:
            return Response(
                {"status": False, "message": "Project does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

