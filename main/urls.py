from django.urls import path
from .views.views import (
    FileUploadView,
    ValidateFile,
    UniqueValuesView,
    CheckNewDepotsAndTerminalsView,
    ScenarioSchedulesDownload,
    DepotTerminalDistanceUpdateView,
    DistanceMatrixUpdateView,
    ScenarioSchedulesDownload,
    GetAllDepotsView,
    GetAllTerminalsView,
    GetDepotsByProjectIdView,
    GetTerminalsByProjectIdView,
    BusModelCreateView,
    BusModelListView,
    ChargerModelListView,
    ChargerModelCreateView,
    DeleteBusModelView,
    DeleteChargerModelView,
    UpdateBusModelView,
    UpdateChargerModelView,
    BusModelPowerConsumptionView,
    DynamicFileUploadView,
    DynamicPowerConsumptionView,
    CreateChargingScenarioView,
    ChargingAnalysisResultsView,
    ListChargingScenarios,
    UpdateChargingScenarioView,
    DeleteChargingScenario,
    FilteredCCSBusModelListView,
    FilteredGBTBusModelListView,
    SuggestedBusModelView,
    ExistingDepotAllocationDataView,
    ProposedDepotAllocationView,
    DepotAllocationScenarioResultsView,
    TransformerListView, HTCableListView, RMUListView, MeteringPanelListView, LTPanelListView,
    TransformerCreateView, HTCableCreateView, RMUCreateView, MeteringPanelCreateView, LTPanelCreateView,
    DeleteTransformerView, DeleteHTCableView, DeleteRMUView, DeleteMeteringPanelView, DeleteLTPanelView,
    UpdateTransformerView, UpdateHTCableView, UpdateRMUView, UpdateMeteringPanelView, UpdateLTPanelView,
    ChargingScenarioCompareView,
    GetComponentsByDepotView,
    CalculateDistanceAndTransformersView,
    BatteryReplacementView,
    OperationalCostCalculationView,
    SalvageCostEstimationView,
    CreateDesignEbusScenarioView,
    DesignEbusScenarioResultsView,
    ListDesignEbusScenarios, UpdateDesignEbusScenarioView, DeleteDesignEbusScenario,
    DesignEbusScenarioCompareView,
    ProjectNameValidationView, ScenarioNameValidationView,
    ObjectiveFunctionView

)

from .views.scenario_views import (
    CreateScenarioView,
    ListScenario,
    DeadKmVisualOptimizeView,
    DeadKmScenarioCompareView,
    UpdateScenarioView,
    DeleteScenarioView,
    CheckIsOutdatedView
)

from .views.project_views import (
    ProjectSummaryView,
    SubmitProject,
    CreateProject,
    ListProject,
    GetProjectById,
    ProjecRename,
    projectDelete,
    projectDuplicate,
)

urlpatterns = [
    path("fileUpload/", FileUploadView.as_view(), name="fileUpload"),
    path("createProject/", CreateProject.as_view(), name="createProject"),
    path("getAllProjects/", ListProject.as_view(), name="getAllProjects"),
    path("getProjectById/", GetProjectById.as_view(), name="getProjectById"),
    path("validatefile/", ValidateFile.as_view(), name="validateFile"),
    path("projectRename/", ProjecRename.as_view(), name="projectRename"),
    path("projectDelete/", projectDelete.as_view(), name="projectDelete"),
    path("projectDuplicate/", projectDuplicate.as_view(), name="projectDuplicate"),
    path("projectSummary/", ProjectSummaryView.as_view(), name="projectDetails"),
    path("submitProject/", SubmitProject.as_view(), name="submitProject"),
    path("unique-values/", UniqueValuesView.as_view(), name="unique-values"),
    path("checkNewDepotTerminal/",CheckNewDepotsAndTerminalsView.as_view(), name="checkNewDepotTerminal"),
    path("createScenario/", CreateScenarioView.as_view(), name="createScenario"),
    path("getAllScenarios/", ListScenario.as_view(), name="getAllScenarios"),
    path(
        "deadKmVisualOptimize/",
        DeadKmVisualOptimizeView.as_view(),
        name="deadKmVisualOptimize",
    ),
    path(
        "deadKmScenarioCompare/",
        DeadKmScenarioCompareView.as_view(),
        name="deadKmScenarioCompare",
    ),
    path(
        "updateScenario/",
        UpdateScenarioView.as_view(),
        name="updateScenario",
    ),
    path(
        "delete-scenario/",
        DeleteScenarioView.as_view(),
        name="deleteScenario",
    ),
    path(
        "download-modified-schedule-file/",
        ScenarioSchedulesDownload.as_view(),
        name="downloadScenarioSchedules",
    ),
    path(
        "update-distance-matrix/",
        DistanceMatrixUpdateView.as_view(),
        name="depotTerminalDisatnceUpdate",
    ),
    path(
        "get-all-depots/",
        GetAllDepotsView.as_view(),
        name="getAllDepots",
    ),
    path(
        "get-all-terminals/",
        GetAllTerminalsView.as_view(),
        name="getAllTerminals",
    ),
    path(
        "get-depots-by-project-id/",
        GetDepotsByProjectIdView.as_view(),
        name="getDepotsByProjectId",
    ),
    path(
        "get-terminals-by-project-id/",
        GetTerminalsByProjectIdView.as_view(),
        name="getTerminalsByProjectId",
    ),
    path(
        "bus-model-create/",
        BusModelCreateView.as_view(),
        name="busModelCreate",
    ),
    path(
        "bus-model-list/",
        BusModelListView.as_view(),
        name="busModelList",
    ),
    path(
        "charger-model-list/",
        ChargerModelListView.as_view(),
        name="chargerModelList",
    ),
    path(
        "charger-model-create/",
        ChargerModelCreateView.as_view(),
        name="chargerModelCreate",
    ),    
    path(
        "check-is-outdated/",
        CheckIsOutdatedView.as_view(),
        name="checkIsOutdated",
    ), 
    path(
        "delete-bus-model/",
        DeleteBusModelView.as_view(),
        name="deleteBusModel",
    ),
    path(
        "delete-charger-model/",
        DeleteChargerModelView.as_view(),
        name="deleteChargerModel",
    ),
    path(
        'update-bus-model/',
        UpdateBusModelView.as_view(),
        name='updateBusModel'
    ),
    path(
        'update-charger-model/',
        UpdateChargerModelView.as_view(),
        name='updateChargerModel'
    ),
    path(
        "bus-model-power-consumption/",
        BusModelPowerConsumptionView.as_view(),
        name="busModelPowerConsumption",
    ), 
    path(
        "dynamic-file-upload/",
        DynamicFileUploadView.as_view(),
        name="dynamicFileUpload",
    ), 
    path(
        "dynamic-power-consumption/",
        DynamicPowerConsumptionView.as_view(),
        name="dynamicPowerConsumption",
    ),
    path(
        "create-charging-scenario/",
        CreateChargingScenarioView.as_view(),
        name="createChargingScenario", 
    ),
    path(
        "charging-analysis-results/",
        ChargingAnalysisResultsView.as_view(),
        name="chargingAnalysisResults", 
    ), 
    path("get-charging-scenarios/", 
        ListChargingScenarios.as_view(),
        name="listChargingScenarios"
    ),
    path(
        "update-charging-scenario/",
        UpdateChargingScenarioView.as_view(),
        name="updateChargingScenario"
    ),
    path(
        "delete-charging-scenario/",
        DeleteChargingScenario.as_view(),
        name="deleteChargingScenario",
    ),
    path(
        "ccs-bus-model-list/",
        FilteredCCSBusModelListView.as_view(),
        name="ccsbusModelList",
    ),
    path(
        "gbt-bus-model-list/",
        FilteredGBTBusModelListView.as_view(),
        name="gbtbusModelList",
    ),
    path(
        "suggested-bus-model/",
        SuggestedBusModelView.as_view(),
        name="suggestedBusModel",
    ),
    path(
        "existing-depot-allocation-data/",
        ExistingDepotAllocationDataView.as_view(),
        name="existingDepotAllocationData",
    ),
    path(
        "proposed-depot-allocation/",
        ProposedDepotAllocationView.as_view(),
        name="proposedDepotAllocation",
    ),
    path(
        "depot-allocation-scenario-results/",
        DepotAllocationScenarioResultsView.as_view(),
        name="depotAllocationScenarioResults",
    ),
    path(
        "transformer-create/",
        TransformerCreateView.as_view(),
        name="transformerCreate",
    ),
    path(
        "transformer-list/",
        TransformerListView.as_view(),
        name="transformerlList",
    ),
    path(
        "delete-transformer/",
        DeleteTransformerView.as_view(),
        name="deleteTransformer",
    ),
    path(
        "update-transformer/",
        UpdateTransformerView.as_view(),
        name="updateTransformer",
    ),
    path(
        "htcable-create/",
        HTCableCreateView.as_view(),
        name="htcableCreate",
    ),
    path(
        "htcable-list/",
        HTCableListView.as_view(),
        name="htcableList",
    ),
    path(
        "delete-htcable/",
        DeleteHTCableView.as_view(),
        name="deleteHTCable",
    ),
    path(
        "update-htcable/",
        UpdateHTCableView.as_view(),
        name="updateHTCable",
    ),
    path(
        "rmu-create/",
        RMUCreateView.as_view(),
        name="rmuCreate",
    ),
    path(
        "rmu-list/",
        RMUListView.as_view(),
        name="rmuList",
    ),
    path(
        "delete-rmu/",
        DeleteRMUView.as_view(),
        name="deleteRMU",
    ),
    path(
        "update-rmu/",
        UpdateRMUView.as_view(),
        name="updateRMU",
    ),
    path(
        "meteringpanel-create/",
        MeteringPanelCreateView.as_view(),
        name="meteringPanelCreate",
    ),
    path(
        "meteringpanel-list/",
        MeteringPanelListView.as_view(),
        name="meteringPanelList",
    ),
    path(
        "delete-meteringpanel/",
        DeleteMeteringPanelView.as_view(),
        name="deleteMeteringPanel",
    ),
    path(
        "update-meteringpanel/",
        UpdateMeteringPanelView.as_view(),
        name="updateMeteringPanel",
    ),
    path(
        "ltpanel-create/",
        LTPanelCreateView.as_view(),
        name="ltPanelCreate",
    ),
    path(
        "ltpanel-list/",
        LTPanelListView.as_view(),
        name="ltPanelList",
    ),
    path(
        "delete-ltpanel/",
        DeleteLTPanelView.as_view(),
        name="deleteLTPanel",
    ),
    path(
        "update-ltpanel/",
        UpdateLTPanelView.as_view(),
        name="updateLTPanel",
    ),
    path(
        "charging-scenario-compare/",
        ChargingScenarioCompareView.as_view(),
        name="chargingScenarioCompare",
    ),
    path(
        "get-components-by-depot/",
        GetComponentsByDepotView.as_view(),
        name="getComponentsByDepot",
    ),
    path(
        "calculate-distance-transformers/",
        CalculateDistanceAndTransformersView.as_view(),
        name="calculateDistanceTransformers",
    ),
    path(
        "battery-replacement/",
        BatteryReplacementView.as_view(),
        name="batteryReplacement"
    ),
    path(
        "operational-cost-calculation/",
        OperationalCostCalculationView.as_view(),
        name="operationalCostCalculation"
    ),
    path(
        "salvage-cost-estimation/",
        SalvageCostEstimationView.as_view(),
        name="salvageCostEstimation"
    ),
    path(
        "create-designebus-scenario/",
        CreateDesignEbusScenarioView.as_view(),
        name="createDesignEbusScenario"
    ),
    path(
        "designebus-scenario-results/",
        DesignEbusScenarioResultsView.as_view(),
        name="designEbusScenarioResults"
    ),
    path("get-designebus-scenarios/", 
        ListDesignEbusScenarios.as_view(),
        name="listDesignEbusScenarios"
    ),
    path(
        "update-designebus-scenario/",
        UpdateDesignEbusScenarioView.as_view(),
        name="updateDesignEbusScenario",
    ),
    path(
        "delete-designebus-scenario/",
        DeleteDesignEbusScenario.as_view(),
        name="deleteDesignEbusScenario",
    ),
    path(
        "designebus-scenario-compare/",
        DesignEbusScenarioCompareView.as_view(),
        name="designEbusScenarioCompare"
    ),
    path(
        "project-name-validation/",
        ProjectNameValidationView.as_view(),
        name="projectNameValidation"
    ),
    path(
        "scenario-name-validation/",
        ScenarioNameValidationView.as_view(),
        name="scenarioNameValidation"
    ),
    path(
        "objective-function/", 
        ObjectiveFunctionView.as_view(), 
        name='objectiveFunction'
    ),

]
