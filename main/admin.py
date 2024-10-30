from django.contrib import admin

# Register your models here.

from .models import ( Project, Schedule, Depot, Terminal, Substation, Datatable, Scenario, Scenario_Schedule, DistanceMatrix, BusModel, ChargerModel, 
                        DepotSummary, TerminalSummary, DepotTerminalMap, PowerScenario, HistoryPowerConsumptionModel, ChargingAnalysisScenario, DepotTerminalDistanceMatrix, TerminalDepotDistanceMatrix,
                        Transformer, HTCable, RMU, MeteringPanel, LTPanel, DepotAllocationScenario, DepotAllocation_Schedule, DesignEbusScenario, ObjectiveFunctions )

admin.site.register(Project)
admin.site.register(Schedule)
admin.site.register(Depot)
admin.site.register(Terminal)
admin.site.register(Substation)
admin.site.register(Scenario)
admin.site.register(Scenario_Schedule)
# admin.site.register(DepotTerminalDistanceMatrix)
# admin.site.register(TerminalDepotDistanceMatrix)
admin.site.register(DistanceMatrix)
admin.site.register(BusModel)
admin.site.register(ChargerModel)
# admin.site.register(DepotSummary)
# admin.site.register(TerminalSummary)
# admin.site.register(DepotTerminalMap)
admin.site.register(PowerScenario)
admin.site.register(HistoryPowerConsumptionModel)
admin.site.register(ChargingAnalysisScenario)
admin.site.register(Transformer)
admin.site.register(HTCable)
admin.site.register(RMU)
admin.site.register(MeteringPanel)
admin.site.register(LTPanel)
admin.site.register(DepotAllocationScenario)
admin.site.register(DepotAllocation_Schedule)
admin.site.register(DesignEbusScenario)
admin.site.register(ObjectiveFunctions)


#admin.site.register(docType)
admin.site.register(Datatable)
