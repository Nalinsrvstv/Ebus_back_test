from datetime import datetime
from django.db import models
from usersmanagement.models import CustomUser
from enum import Enum
from picklefield.fields import PickledObjectField


class Project(models.Model):
    # Fields for the Project model
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    workflow_type = models.IntegerField(blank=True)
    created_by = models.CharField(default=None)
    created_date = models.DateTimeField(default=datetime.now, blank=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field="id")
    is_submitted = models.BooleanField(default=False, blank=True)
    # The 'user_id' field establishes the foreign key relationship with User's 'id' field

    def __str__(self):
        return str(self.project_id) + "_" + str(self.project_name)


class Schedule(models.Model):
    # Fields for the Project model
    project_id = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, related_name="schedule"
    )  # Foreign key for connect to the Project for which the schedule file is uploaded.
    id = models.AutoField(
        primary_key=True
    )  # ID provided by Django as default for every table
    schedule_id = models.CharField(blank=True, null=True)
    trip_number = models.IntegerField(blank=True, null=True)
    route_number = models.CharField(blank=True, null=True)
    direction = models.CharField(blank=True, null=True)
    start_terminal = models.CharField(blank=True, null=True)
    end_terminal = models.CharField(blank=True, null=True)
    start_time = models.IntegerField(blank=True, null=True)
    travel_time = models.IntegerField(blank=True, null=True)
    trip_distance = models.FloatField(blank=True, null=True)
    crew_id = models.CharField(blank=True, null=True)
    event_type = models.CharField(blank=True, null=True)
    operator = models.CharField(blank=True, null=True)
    ac_non_ac = models.CharField(blank=True, null=True)
    brt_non_brt = models.CharField(blank=True, null=True)
    service_type = models.CharField(blank=True, null=True)
    fuel_type = models.CharField(blank=True, null=True)
    bus_type = models.CharField(blank=True, null=True)
    depot_id = models.CharField(blank=True, null=True)

    def __str__(self):
        return str(self.project_id) + "_" + str(self.id) + "_Schedule"


class Depot(models.Model):
    # Fields for the Project model
    project_id = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, related_name="depot"
    )  # Foreign key for connect to the Project for which the depot file is uploaded.
    id = models.AutoField(
        primary_key=True
    )  # ID provided by Django as default for every table
    depot_id = models.CharField(null=True)  # field in the Depot CSV file
    depot_name = models.CharField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)
    operator = models.CharField(blank=True, null=True)
    ac_non_ac = models.CharField(blank=True, null=True)
    brt_non_brt = models.CharField(blank=True, null=True)
    service_type = models.CharField(blank=True, null=True)
    fuel_type = models.CharField(blank=True, null=True)
    bus_type = models.CharField(blank=True, null=True)

    def __str__(self):
        return str(self.project_id) + "_" + str(self.id) + "_Depot"


class Terminal(models.Model):
    # Fields for the Project model
    project_id = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, related_name="terminal"
    )  # Foreign key for connect to the Project for which the depot file is uploaded.
    id = models.AutoField(
        primary_key=True
    )  # ID provided by Django as default for every table
    terminal_id = models.CharField(null=True)  # ID field in the Terminal CSV file
    terminal_name = models.CharField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    terminal_area = models.CharField(blank=True, null=True)

    def __str__(self):
        return str(self.project_id) + "_" + str(self.id) + "_Terminal"


class Substation(models.Model):
    project_id = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, related_name="substation") 
    id = models.AutoField(primary_key=True)  
    short_name = models.CharField(blank=True,null=True) 
    long_name = models.CharField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return str(self.project_id) + "_" + str(self.id) + "_Substation"


class Scenario(models.Model):
    scenario_id = models.AutoField(primary_key=True)
    scenario_name = models.CharField(blank=True, null=True)
    description = models.CharField(blank=True, null=True)
    result = models.JSONField(blank=True, null=True)
    exclusions = models.JSONField(blank=True, null=True)
    assignment_preferences = models.JSONField(blank=True, null=True)
    project_id = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, related_name="scenario"
    )

    def __str__(self):
        return str(self.project_id) + "_" + str(self.scenario_id) + "_Scenario"


class Scenario_Schedule(models.Model):
    id = models.AutoField(primary_key=True)
    scenario = models.ForeignKey(
        Scenario, on_delete=models.CASCADE, related_name="scenario_schedule"
    )
    # Copy all fields from the Schedule model
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    schedule_id = models.CharField(blank=True, null=True)
    trip_number = models.IntegerField(blank=True, null=True)
    route_number = models.CharField(blank=True, null=True)
    direction = models.CharField(blank=True, null=True)
    start_terminal = models.CharField(blank=True, null=True)
    end_terminal = models.CharField(blank=True, null=True)
    start_time = models.IntegerField(blank=True, null=True)
    travel_time = models.IntegerField(blank=True, null=True)
    trip_distance = models.FloatField(blank=True, null=True)
    crew_id = models.CharField(blank=True, null=True)
    event_type = models.CharField(blank=True, null=True)
    operator = models.CharField(blank=True, null=True)
    ac_non_ac = models.CharField(blank=True, null=True)
    brt_non_brt = models.CharField(blank=True, null=True)
    service_type = models.CharField(blank=True, null=True)
    fuel_type = models.CharField(blank=True, null=True)
    bus_type = models.CharField(blank=True, null=True)
    depot_id = models.CharField(blank=True, null=True)

    def __str__(self):
        return (
            str(self.scenario)
            + "_"
            + str(self.schedule_id)
            + "_"
            + str(self.id)
            + "_Scenario_Schedule"
        )


class DistanceMatrix(models.Model):
    id = models.AutoField(primary_key=True)
    start_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    start_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    end_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    end_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return f"Distance from ({self.start_latitude}, {self.start_longitude}) to ({self.end_latitude}, {self.end_longitude}) is {self.distance} units"


class DepotTerminalDistanceMatrix(models.Model):
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE)
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    distance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return (
            self.depot.depot_id
            + " to "
            + self.terminal.terminal_id
            + ": "
            + str(self.distance)
            + " km"
        )


class TerminalDepotDistanceMatrix(models.Model):
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE)
    distance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return (
            self.terminal.terminal_id
            + " to "
            + self.depot.depot_id
            + ": "
            + str(self.distance)
            + " km"
        )


class BusModel(models.Model):
    id = models.AutoField(primary_key=True)
    short_name = models.CharField(max_length=50, unique=True)
    long_name = models.CharField(max_length=200, null=True)
    oem = models.CharField(max_length=100, null=True)
    bus_dimension = models.CharField(max_length=100, null=True)
    curb_weight = models.FloatField(null=True)
    gross_vehicle_weight = models.FloatField(null=True)
    air_conditioning = models.CharField(null=True)
    seating_capacity = models.IntegerField(null=True)
    bus_cost = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    charger_type = models.CharField(max_length=50, null=True)
    power_consumption = models.FloatField(null=True)
    battery_capacity = models.IntegerField(null=True)
    battery_cost = models.DecimalField(max_digits=20, decimal_places=4, null=True)

    def __str__(self):
        return (str(self.id) + "_" + str(self.short_name))
    

class ChargerModel(models.Model):
    id = models.AutoField(primary_key=True)
    short_name = models.CharField(max_length=50, unique=True, null=True)
    long_name = models.CharField(max_length=100, unique=True, null=True)
    oem = models.CharField(max_length=100, null=True)
    charger_type = models.CharField(max_length=50, null=True)
    charger_capacity = models.IntegerField(null=True)
    charger_cost = models.DecimalField(max_digits=20, decimal_places=4, null=True)

    def __str__(self):
        return (str(self.id) + "_" + str(self.short_name))


class DepotSummary(models.Model):
    id = models.AutoField(primary_key=True)
    depot_id = models.ForeignKey(
        Depot, on_delete=models.CASCADE, null=True, related_name="depot_summaries"
    )
    bus_model_id = models.ForeignKey(
        BusModel, on_delete=models.CASCADE, null=True, related_name="depot_summaries"
    )
    charger_model_id = models.ForeignKey(
        ChargerModel, on_delete=models.CASCADE, null=True, related_name="depot_summaries"
    )
    base_no_of_chargers = models.IntegerField(null=True)


class TerminalSummary(models.Model):
    id = models.AutoField(primary_key=True)
    terminal_id = models.ForeignKey(
        Terminal, on_delete=models.CASCADE, null=True, related_name="terminal_summaries"
    )
    charger_model_id = models.ForeignKey(
        ChargerModel, on_delete=models.CASCADE, null=True, related_name="terminal_summaries"
    )
    base_no_of_chargers = models.IntegerField(null=True)


class DepotTerminalMap(models.Model):
    depot_summary_id = models.ForeignKey(
        DepotSummary, on_delete=models.CASCADE, null=True, related_name="depot_terminal_sum"
    )
    terminal_id = models.ForeignKey(
        Terminal, on_delete=models.CASCADE, null=True, related_name="depot_terminal_sum"
    )


class PowerScenario(models.Model):
    scenario_id = models.AutoField(primary_key=True)
    scenario_name = models.CharField(blank=True, null=True)
    description = models.CharField(blank=True, null=True)
    project_id = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, related_name="p_scenario"
    )

    def __str__(self):
        return str(self.project_id) + "_" + str(self.scenario_id) + "_Scenario"


class HistoryPowerConsumptionModel(models.Model):
    id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="power_consumption")
    scenario = models.ForeignKey(
        PowerScenario, on_delete=models.CASCADE, related_name="power_schedule"
    )
    route_no = models.CharField(null=True)
    start_min = models.IntegerField(null=True)
    end_min = models.IntegerField(null=True)
    start_odo = models.IntegerField(null=True)
    end_odo = models.IntegerField(null=True)
    start_soc = models.IntegerField(null=True)
    end_soc = models.IntegerField(null=True)
    passenger_load = models.FloatField(null=True)
    short_name = models.ForeignKey(
        BusModel, on_delete=models.CASCADE, related_name="power_consupt"
    )

    def __str__(self):
        return (str(self.id) + "_" + str(self.route_no))


class ChargingAnalysisScenario(models.Model):
    scenario_id = models.AutoField(primary_key=True)
    scenario_name = models.CharField(blank=True, null=True)
    description = models.CharField(blank=True, null=True)
    requestdata = PickledObjectField(blank=True, null=True)
    result = PickledObjectField(blank=True, null=True)
    project_id = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, related_name="charging_scenario"
    )

    def __str__(self):
        return str(self.project_id) + "_" + str(self.scenario_id) + "_Scenario"


class Transformer(models.Model):
    id = models.AutoField(primary_key=True)
    transformer = models.CharField(null=True)
    voltage = models.IntegerField(null=True)
    capacity_kva = models.IntegerField(null=True)
    total_cost = models.IntegerField(null=True)

    def __str__(self):
        return (str(self.id) + "_" + str(self.transformer))
    

class HTCable(models.Model):
    id = models.AutoField(primary_key=True)
    cable_type = models.CharField(null=True)
    voltage = models.IntegerField(null=True)
    max_current_carrying_capacity = models.IntegerField(null=True)
    total_cost = models.IntegerField(null=True)

    def __str__(self):
        return (str(self.id) + "_" + str(self.cable_type))


class RMU(models.Model):
    id = models.AutoField(primary_key=True)
    component_name = models.CharField(null=True)
    specification = models.CharField(null=True)
    voltage = models.IntegerField(null=True)
    capacity_kva = models.IntegerField(null=True)
    cost = models.IntegerField(null=True)

    def __str__(self):
        return (str(self.id) + "_" + str(self.component_name))
    

class MeteringPanel(models.Model):
    id = models.AutoField(primary_key=True)
    component_name = models.CharField(null=True)
    voltage = models.IntegerField(null=True)
    amount = models.IntegerField(null=True)

    def __str__(self):
        return (str(self.id) + "_" + str(self.component_name))
    

class LTPanel(models.Model):
    id = models.AutoField(primary_key=True)
    description_of_item = models.CharField(null=True)
    unit = models.CharField(null=True)
    voltage = models.IntegerField(null=True)
    current = models.IntegerField(null=True)
    total = models.IntegerField(null=True)

    def __str__(self):
        return (str(self.id) + "_" + str(self.description_of_item))


class DepotAllocationScenario(models.Model):
    scenario_id = models.AutoField(primary_key=True)
    scenario_name = models.CharField(blank=True, null=True)
    description = models.CharField(blank=True, null=True)
    depot_requestdata = PickledObjectField(blank=True, null=True)
    depot_result = PickledObjectField(blank=True, null=True)
    project_id = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, related_name="depot_allocation_scenario"
    )

    def __str__(self):
        return str(self.project_id) + "_" + str(self.scenario_id) + "_Scenario"
    

class DepotAllocation_Schedule(models.Model):
    id = models.AutoField(primary_key=True)
    scenario = models.ForeignKey(
        DepotAllocationScenario, on_delete=models.CASCADE, related_name="depotallocation_schedule"
    )
    # Copy all fields from the Schedule model
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    schedule_id = models.CharField(blank=True, null=True)
    trip_number = models.IntegerField(blank=True, null=True)
    route_number = models.CharField(blank=True, null=True)
    direction = models.CharField(blank=True, null=True)
    start_terminal = models.CharField(blank=True, null=True)
    end_terminal = models.CharField(blank=True, null=True)
    start_time = models.IntegerField(blank=True, null=True)
    travel_time = models.IntegerField(blank=True, null=True)
    trip_distance = models.FloatField(blank=True, null=True)
    crew_id = models.CharField(blank=True, null=True)
    event_type = models.CharField(blank=True, null=True)
    operator = models.CharField(blank=True, null=True)
    ac_non_ac = models.CharField(blank=True, null=True)
    brt_non_brt = models.CharField(blank=True, null=True)
    service_type = models.CharField(blank=True, null=True)
    fuel_type = models.CharField(blank=True, null=True)
    bus_type = models.CharField(blank=True, null=True)
    depot_id = models.CharField(blank=True, null=True)

    def __str__(self):
        return (
            str(self.scenario)
            + "_"
            + str(self.schedule_id)
            + "_"
            + str(self.id)
            + "_Depot_Schedule"
        )


class DesignEbusScenario(models.Model):
    scenario_id = models.AutoField(primary_key=True)
    scenario_name = models.CharField(blank=True, null=True)
    description = models.CharField(blank=True, null=True)
    design_requestdata = PickledObjectField(blank=True, null=True)
    design_result = PickledObjectField(blank=True, null=True)
    project_id = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, related_name="design_ebus_scenario"
    )

    def __str__(self):
        return str(self.project_id) + "_" + str(self.scenario_id) + "_Scenario"
 

class ObjectiveFunctions(models.Model):
    id = models.AutoField(primary_key=True)
    object_value = models.FloatField(blank=True, null=True)
    project_id = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, related_name="_objectfunction"
    )

    def __str__(self):
        return str(self.project_id) + "_" + str(self.object_value)
 

class docType(Enum):
    Schedule = "Schedule"
    Depot = "Depot"
    Terminal = "Terminal"
    Scenario = "Scenario"
    Scenario_Schedule = "Scenario_Schedule"
    DepotTerminalDistanceMatrix = " DepotTerminalDistanceMatrix"
    TerminalDepotDistanceMatrix = "TerminalDepotDistanceMatrix"
    Discom_station = "Dscmstn"
    Ebus_schedule = "Ebsscdl"



class Datatable(models.Model):
    # Fields for the Project model
    doc_id = models.ForeignKey(Project, on_delete=models.CASCADE, to_field="project_id")
    doc_name = models.TextField(max_length=100, default=None)
    # doc_data = models.JSONField(default=None)
    created_date = models.DateTimeField(default=datetime.now, blank=True)
    docType = models.TextField(
        max_length=100,
        default=None,
        choices=[(docType.name, docType.value) for docType in docType],
    )

    def __str__(self):
        return self.doc_name

