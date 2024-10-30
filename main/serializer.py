from rest_framework import serializers
from .models import Project, Schedule, Depot, Terminal, Substation, BusModel, ChargerModel, HistoryPowerConsumptionModel, Transformer, HTCable, RMU, MeteringPanel, LTPanel


class FileSerializer(serializers.Serializer):
    file = serializers.CharField(max_length=None, required=False)
    projectId = serializers.IntegerField(required=False)


class CreateProjectSerializer(serializers.Serializer):
    project_name = serializers.CharField(required=True)
    description = serializers.CharField(required=False)
    created_by = serializers.CharField(required=True)
    workflow_type = serializers.IntegerField(required=True)
    schedule_data = serializers.JSONField()
    depot_data = serializers.JSONField()
    terminals_data = serializers.JSONField()
    substation_data = serializers.JSONField(required=False)

class RenameProjectSerializer(serializers.Serializer):
    project_name = serializers.CharField(required=True)
    created_by = serializers.CharField(required=True)
    project_id = serializers.CharField(required=True)
    project_new_name = serializers.CharField(required=True)


class UpdateScenarioSerializer(serializers.Serializer):
    scenario_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    description = serializers.CharField(allow_blank=True)


class SubmitProjectSerializer(serializers.Serializer):
    project_id = serializers.CharField(required=True)
    created_by = serializers.CharField(required=True)


class RenameDuplicateSerializer(serializers.Serializer):
    project_name = serializers.CharField(required=True)
    project_id = serializers.CharField(required=True)
    created_by = serializers.CharField(required=True)


class RenameDeleteSerializer(serializers.Serializer):
    project_name = serializers.CharField(required=True)
    project_id = serializers.CharField(required=True)
    created_by = serializers.CharField(required=True)


class ProjectSummarySerializer(serializers.Serializer):
    project_id = serializers.CharField(required=True)
    project_name = serializers.CharField(required=True)
    created_by = serializers.CharField(required=True)
    workflow_type = serializers.CharField(required=False)
    description = serializers.CharField(required=False)


class GetAllProjectsSerializer(serializers.Serializer):
    created_by = serializers.CharField(required=True)
    pageNumber = serializers.IntegerField(required=True)
    pageSize = serializers.IntegerField(required=True)
    searchKey = serializers.CharField(max_length=100, allow_blank=True)
    workflow_type = serializers.CharField(required=False)


class GetProjectByIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class GetDepotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depot
        fields = "__all__"


class GetScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = "__all__"


class GetTerminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = "__all__"


class GetSubstationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Substation
        fields = "__all__"


class ValidateFileSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    fileData = serializers.JSONField(required=True)


class CreateScenarioSerializer(serializers.Serializer):
    # project_id = serializers.CharField(required=True)
    # project_name = serializers.CharField(required=True)
    # created_by = serializers.CharField(required=True)
    projectDetails = serializers.DictField(required=True)


class ScenarioSerializer(serializers.Serializer):
    scenario_id = serializers.IntegerField(required=True)
    scenario_name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    result = serializers.JSONField()


class GetAllScenariosSerializer(serializers.Serializer):
    project_id = serializers.CharField(required=True)
    pageNumber = serializers.IntegerField(required=True)
    pageSize = serializers.IntegerField(required=True)


class ScheduleSerializer(serializers.Serializer):
    schedule_id = serializers.CharField(required=True)
    trip_number = serializers.CharField(required=True)
    route_number = serializers.CharField(required=True)
    direction = serializers.CharField(required=True)
    start_terminal = serializers.CharField(required=True)
    end_terminal = serializers.CharField(required=True)
    start_time = serializers.CharField(required=True)
    travel_time = serializers.CharField(required=True)
    trip_distance = serializers.FloatField(required=True)
    crew_id = serializers.CharField(required=True)
    event_type = serializers.CharField(required=True)
    operator = serializers.CharField(required=True)
    ac_non_ac = serializers.CharField(required=True)
    brt_non_brt = serializers.CharField(required=True)
    service_type = serializers.CharField(required=True)
    fuel_type = serializers.CharField(required=True)
    bus_type = serializers.CharField(required=True)
    depot_id = serializers.CharField(required=True)


class DepotSerializer(serializers.Serializer):
    depot_id = serializers.CharField(required=True)
    depot_name = serializers.CharField(required=True)
    latitude = serializers.CharField(required=True)
    longitude = serializers.CharField(required=True)
    capacity = serializers.CharField(required=True)
    operator = serializers.CharField(required=True)
    ac_non_ac = serializers.CharField(required=True)
    brt_non_brt = serializers.CharField(required=True)
    service_type = serializers.CharField(required=True)
    fuel_type = serializers.CharField(required=True)
    bus_type = serializers.CharField(required=True)


class TerminalSerializer(serializers.Serializer):
    terminal_id = serializers.CharField(required=True)
    terminal_name = serializers.CharField(required=True)
    latitude = serializers.CharField(required=True)
    longitude = serializers.CharField(required=True)
    terminal_area = serializers.CharField(required=True)


class ScenarioDeleteSerializer(serializers.Serializer):
    scenario_id = serializers.CharField(required=True)


class ScenarioSchedulesDownloadSerializer(serializers.Serializer):
    scenario_id = serializers.CharField(required=True)


class NewDepotTerminalUpdateSerializer(serializers.Serializer):
    project_id = serializers.CharField(required=True)
    created_by = serializers.CharField(required=True)


class DepotTerminalSerializer(serializers.Serializer):
    project_id = serializers.CharField(required=True)
    created_by = serializers.CharField(required=True)


class GetDepotsByIdSerializer(serializers.Serializer):
    project_id = serializers.CharField(required=True)
    created_by = serializers.CharField(required=True)


class GetTerminalsByIdSerializer(serializers.Serializer):
    project_id = serializers.CharField(required=True)
    created_by = serializers.CharField(required=True)
    depot_id = serializers.CharField(required=True)
 

class BusModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusModel
        fields = '__all__'


class ChargerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargerModel
        fields = '__all__'


class IsOutdatedSerializer(serializers.Serializer):
    project_name = serializers.CharField(required=True)
    project_id = serializers.CharField(required=True)
    created_by = serializers.CharField(required=True)


class BusDeleteSerializer(serializers.Serializer):
    short_name = serializers.CharField(required=True)
    

class ChargerDeleteSerializer(serializers.Serializer):
    short_name = serializers.CharField(required=True)
    

class DynamicFileUploadSerializer(serializers.Serializer):
    project_id = serializers.CharField(required=True)
    project_name = serializers.CharField(required=True)
    created_by = serializers.CharField(required=True)
    # scenario_name = serializers.CharField(required=True)
    # description = serializers.CharField(required=True)
    power_consp_data = serializers.JSONField()


class HistoryPowerConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryPowerConsumptionModel
        fields = '__all__'
        

class DynamicPowerConsumptionSerializer(serializers.Serializer):
    project_name = serializers.CharField(required=True)
    project_id = serializers.CharField(required=True)
    created_by = serializers.CharField(required=True)
    scenario_id = serializers.CharField(required=True)


class CreateChargingScenarioSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(required=True)
    # project_name = serializers.CharField(required=True)
    created_by = serializers.CharField(required=True)
    workflow_type = serializers.IntegerField(required=True)
    scenario_name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    depot_list = serializers.ListField(child=serializers.CharField())
    # route_numbers = serializers.ListField(required=True)
    bus_models_list = serializers.ListField(child=serializers.CharField())
    charger_model_list = serializers.ListField(child=serializers.CharField())
    opportunity_charging = serializers.IntegerField(required=True)
    static_pc_per_km = serializers.DictField(required=True)
    
    # candidate_terminal_charging_location_list = serializers.ListField(child=serializers.CharField())
    base_chargers_list = serializers.ListField(child=serializers.IntegerField())
    simulation_parameters = serializers.DictField(required=True)
    advance_settings = serializers.DictField(required=True)


class ChargingScenarioSerializer(serializers.Serializer):
    scenario_id = serializers.IntegerField(required=True)
    scenario_name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    result = serializers.JSONField()  


class ChargingAnalysisResultsSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(required=True)
    created_by = serializers.CharField(required=True)
    scenario_id = serializers.IntegerField(required=True)


class SuggestedBusModelSerializer(serializers.Serializer):
    depot_night_charging_strategy = serializers.IntegerField(required=True)
    assured_km = serializers.IntegerField(required=True)
    opportunity_charging_duration = serializers.IntegerField(required=True)
    reserve_charge = serializers.FloatField(required=True)
    bus_length = serializers.CharField(required=True)


class ExistingDepotAllocationDataSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(required=True)
    created_by = serializers.CharField(required=True)
    depot_list = serializers.ListField(child=serializers.CharField())


class DepotAllocationInputsSerializer(serializers.Serializer):
    number_of_years = serializers.IntegerField(required=True)
    electricity_tariff_per_unit = serializers.IntegerField(required=True)
    power_consumption_per_km = serializers.FloatField(required=True)
    feeder_line_cost_per_km = serializers.IntegerField(required=True)
    number_of_buses = serializers.IntegerField(required=True)


class ProposedDepotAllocationSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(required=True)
    created_by = serializers.CharField(required=True)
    scenario_name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    candidate_depots = serializers.ListField(child=serializers.CharField())
    candidate_depots_cost = serializers.ListField(child=serializers.IntegerField())
    busmodel_suggestion = SuggestedBusModelSerializer(required=True)
    depot_allocation_inputs = DepotAllocationInputsSerializer(required=True)
    suggested_busmodel = serializers.DictField(required=True)


class DepotAllocationScenarioSerializer(serializers.Serializer):
    scenario_id = serializers.IntegerField(required=True)
    scenario_name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    depot_result = serializers.JSONField()


class TransformerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transformer
        fields = '__all__'


class HTCableSerializer(serializers.ModelSerializer):
    class Meta:
        model = HTCable
        fields = '__all__'


class RMUSerializer(serializers.ModelSerializer):
    class Meta:
        model = RMU
        fields = '__all__'


class MeteringPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeteringPanel
        fields = '__all__'


class LTPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LTPanel
        fields = '__all__'


class TransformerDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    transformer = serializers.CharField(required=True)


class HtCableDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    cable_type = serializers.CharField(required=True)


class RMUDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    component_name = serializers.CharField(required=True)


class MeteringPanelDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    component_name = serializers.CharField(required=True)


class LTPanelDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    description_of_item = serializers.CharField(required=True)
    

class CompareScenarioSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(required=True)
    created_by = serializers.CharField(required=True)
    scenario_ids = serializers.ListField(child=serializers.IntegerField())


class GetComponentsByDepotSerializer(serializers.Serializer):
    apparent_power = serializers.FloatField(required=True)


class CalculateDistanceAndTransformersSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(required=True)
    created_by = serializers.CharField(required=True)
    depot_name = serializers.CharField(required=True)
    apparent_power = serializers.FloatField(required=True)
    substation_short_name = serializers.CharField(required=True)
    transformer_name = serializers.CharField(required=True)
    htcable_name = serializers.CharField(required=True)
    rmu_name = serializers.CharField(required=True)
    meteringpanel_name = serializers.CharField(required=True)
    ltpanel_name = serializers.CharField(required=True)
    busmodel_short_name = serializers.CharField(required=True)
    no_of_buses = serializers.IntegerField(required=True)
    charger_short_name = serializers.CharField(required=True)
    chargers = serializers.IntegerField(required=True)
    number_of_years = serializers.IntegerField(required=True)


class BatteryReplacementSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(required=True)
    created_by = serializers.CharField(required=True)
    depotallocation_scenario_id = serializers.IntegerField(required=True)
    battery_cycles = serializers.IntegerField(required=True)
    power_consumption_per_km = serializers.IntegerField(required=True)
    busmodel_short_name = serializers.CharField(required=True)
    number_of_years = serializers.IntegerField(required=True)


class SalvageCostEstimationSerializer(serializers.Serializer):
    components = serializers.DictField(required=True)
    deflation_rate = serializers.DictField(required=True)
    total_years = serializers.IntegerField(required=True)


class CreateDesignEbusScenarioSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(required=True)
    created_by = serializers.CharField(required=True)
    scenario_name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    inventory_indicators = serializers.DictField(required=True)
    performance_indicators = serializers.DictField(required=True)
    financial_indicators = serializers.DictField(required=True)
    charging_scenario_id = serializers.IntegerField(required=True)
    cashflow_inputs = serializers.DictField(required=True)


class DesignEbusScenarioSerializer(serializers.Serializer):
    scenario_id = serializers.IntegerField(required=True)
    scenario_name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    design_result = serializers.JSONField()


class ProjectNameValidationSerializer(serializers.Serializer):
    created_by = serializers.CharField(required=True)
    project_name = serializers.CharField(required=True)


class ScenarioNameValidationSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(required=True)
    created_by = serializers.CharField(required=True)
    workflow_type = serializers.IntegerField(required=True)
    scenario_name = serializers.CharField(required=True)
    