from .models import (
    Schedule,
    Depot,
    Terminal,
    Substation,
    BusModel,
    ChargerModel,
    DistanceMatrix

)
# import libraries
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import ipywidgets as widgets
from geopy.distance import geodesic
import warnings
warnings.filterwarnings("ignore") # Ignore all warnings
from math import factorial
from decimal import Decimal
from pulp import LpMaximize, LpMinimize, LpProblem, LpStatus, lpSum, LpVariable

# pandas settings
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.options.display.width=None

def ebus_depot_allocation(project, candidate_depots, candidate_depots_cost, busmodel_suggestion, depot_allocation_inputs, suggested_busmodel):
    # imports
    depot_list = candidate_depots
    depots = Depot.objects.filter(depot_name__in=depot_list, project_id=project).distinct()
    depot_df = pd.DataFrame(list(depots.values()))
    # depot_df = gpd.GeoDataFrame(depot_df, crs=4326, geometry=[Point(xy) for xy in zip(depot_df.longitude, depot_df.latitude)])

    schedules = Schedule.objects.filter(project_id=project)
    schedule_df = pd.DataFrame(list(schedules.values()))

    terminals = Terminal.objects.filter(project_id=project).distinct()
    terminal_df = pd.DataFrame(list(terminals.values()))
    # terminal_df = gpd.GeoDataFrame(terminal_df, crs = 4326, geometry=[Point(xy) for xy in zip(terminal_df.longitude, terminal_df.latitude)])

    substations=Substation.objects.filter(project_id=project)
    substation_df = pd.DataFrame(list(substations.values()))
    substation_df = gpd.GeoDataFrame(substation_df, crs = 4326, geometry=[Point(xy) for xy in zip(substation_df.longitude, substation_df.latitude)])

    buses=BusModel.objects.all()
    bus_models = pd.DataFrame(list(buses.values()))

    chargers = ChargerModel.objects.all().distinct()
    charger_models = pd.DataFrame(list(chargers.values()))

    depot_night_charging_strategy = busmodel_suggestion["depot_night_charging_strategy"]
    assured_km = busmodel_suggestion["assured_km"]
    opportunity_charging_duration = busmodel_suggestion["opportunity_charging_duration"]
    reserve_charge = busmodel_suggestion["reserve_charge"] / 100
    bus_length = busmodel_suggestion["bus_length"]
    # seating_capacity = busmodel_suggestion["seating_capacity"]
    
    #estimates
    # if depot_night_charging_strategy:
    #     filtered_bus_modelsdf = bus_models[bus_models['charger_type'].str.contains('GB/', na=False)]
    #     filtered_bus_modelsdf = filtered_bus_modelsdf[filtered_bus_modelsdf['seating_capacity'] >= seating_capacity]
    #     filtered_bus_modelsdf['total_range'] = (filtered_bus_modelsdf['battery_capacity']/filtered_bus_modelsdf['power_consumption'])*(1-reserve_charge)

    #     filtered_bus_modelsdf = filtered_bus_modelsdf.sort_values(by=['total_range'], ascending=False).reset_index(drop=True)

    # else:
    #     filtered_bus_modelsdf = bus_models[bus_models['charger_type'].str.contains('CCS2', na=False)] #filter CCS2
    #     filtered_bus_modelsdf = filtered_bus_modelsdf[filtered_bus_modelsdf['seating_capacity'] >= seating_capacity] # Seat Capacity
    #     filtered_charger_models = charger_models[charger_models['charger_type'].str.contains('CCS2', na=False)] # Charger CCS2
    #     filtered_charger_models = filtered_charger_models.sort_values(by=['charger_capacity'], ascending=False).reset_index(drop=True) # sort highest charger_capacity
    #     charger_capacity = filtered_charger_models['charger_capacity'].tolist()[0] #select highest charger_capacity
    #     filtered_bus_modelsdf['top_up'] = [min(charger_capacity*(opportunity_charging_duration/60), 0.85*(1-reserve_charge)*i) for i in filtered_bus_modelsdf['battery_capacity']] #top up for opportunity charging
    #     filtered_bus_modelsdf['range'] = (filtered_bus_modelsdf['battery_capacity']*(1-reserve_charge))/filtered_bus_modelsdf['power_consumption']
    #     filtered_bus_modelsdf['topup_range'] = filtered_bus_modelsdf['top_up']/filtered_bus_modelsdf['power_consumption']
    #     filtered_bus_modelsdf['total_range'] = filtered_bus_modelsdf['range'] + filtered_bus_modelsdf['topup_range']

    #     filtered_bus_modelsdf = filtered_bus_modelsdf.sort_values(by=['total_range'], ascending=False).reset_index(drop=True)
    #     filtered_bus_modelsdf

    # suggested_bus_model = filtered_bus_modelsdf.iloc[0]

    number_of_years = depot_allocation_inputs["number_of_years"]
    electricity_tariff_per_unit = depot_allocation_inputs["electricity_tariff_per_unit"]
    power_consumption_per_km = depot_allocation_inputs["power_consumption_per_km"]
    feeder_line_cost_per_km = depot_allocation_inputs["feeder_line_cost_per_km"]
    number_of_buses = depot_allocation_inputs["number_of_buses"]

    # ESTIMATED FROM BUS SELECTION
    # selected_bus_model = suggested_bus_model.short_name # not an ui input
    # total_range = suggested_bus_model.total_range #estimated from bus selection

    selected_bus_model = suggested_busmodel["short_name"] # from ui
    total_range = suggested_busmodel["total_range"]
    depot_df['depot_id'] = depot_df['depot_id'].astype(int)
    terminal_df['terminal_id'] = terminal_df['terminal_id'].astype(int)

    # create distance matrix - for every project
    # DT_distance_matrix = pd.DataFrame(index=depot_df['depot_id'] ,columns=terminal_df['terminal_id'])
    # for i,dp in depot_df.to_crs(32643).iterrows():
    #     DT_distance_matrix.loc[dp['depot_id']] = list((terminal_df.to_crs(32643).distance(dp['geometry'])*1.2).round())

    # # create distance matrix - for every project
    # TD_distance_matrix = pd.DataFrame(index = terminal_df['terminal_id'], columns = depot_df['depot_id'])
    # for i,dp in terminal_df.to_crs(32643).iterrows():
    #     TD_distance_matrix.loc[dp['terminal_id']] = list((depot_df.to_crs(32643).distance(dp['geometry'])*1.2).round())


# Fetch the distance matrix from the database
    distance_records = DistanceMatrix.objects.all().values('start_latitude', 'start_longitude', 'end_latitude', 'end_longitude', 'distance')
    distance_df = pd.DataFrame(list(distance_records))

    depot_df['latitude'] = depot_df['latitude'].round(6)
    depot_df['longitude'] = depot_df['longitude'].round(6)
    terminal_df['latitude'] = terminal_df['latitude'].round(6)
    terminal_df['longitude'] = terminal_df['longitude'].round(6)
    distance_df['start_latitude'] = distance_df['start_latitude'].round(6)
    distance_df['start_longitude'] = distance_df['start_longitude'].round(6)
    distance_df['end_latitude'] = distance_df['end_latitude'].round(6)
    distance_df['end_longitude'] = distance_df['end_longitude'].round(6)

    depot_df[['latitude', 'longitude']] = depot_df[['latitude', 'longitude']].astype(float)
    terminal_df[['latitude', 'longitude']] = terminal_df[['latitude', 'longitude']].astype(float)
    distance_df[['start_latitude', 'start_longitude', 'end_latitude', 'end_longitude']] = distance_df[['start_latitude', 'start_longitude', 'end_latitude', 'end_longitude']].astype(float)
   
    epsilon = 0.0001

    DT_distance_matrix = pd.DataFrame(index=depot_df['depot_id'], columns=terminal_df['terminal_id'])
    for i, depot in depot_df.iterrows():
        for j, terminal in terminal_df.iterrows():
            distance = distance_df[
                (abs(distance_df['start_latitude'] - depot['latitude']) < epsilon) &
                (abs(distance_df['start_longitude'] - depot['longitude']) < epsilon) &
                (abs(distance_df['end_latitude'] - terminal['latitude']) < epsilon) &
                (abs(distance_df['end_longitude'] - terminal['longitude']) < epsilon)
            ]['distance'].values

            DT_distance_matrix.at[depot['depot_id'], terminal['terminal_id']] = distance[0]
        
    TD_distance_matrix = pd.DataFrame(index=terminal_df['terminal_id'], columns=depot_df['depot_id'])
    for i, terminal in terminal_df.iterrows():
        for j, depot in depot_df.iterrows():
            distance = distance_df[
                (abs(distance_df['start_latitude'] - terminal['latitude']) < epsilon) &
                (abs(distance_df['start_longitude'] - terminal['longitude']) < epsilon) &
                (abs(distance_df['end_latitude'] - depot['latitude']) < epsilon) &
                (abs(distance_df['end_longitude'] - depot['longitude']) < epsilon)
            ]['distance'].values

            TD_distance_matrix.at[terminal['terminal_id'], depot['depot_id']] = distance[0]
        
    speed = 20
    # DT_tt_matrix = 60*(DT_distance_matrix/1000)/speed
    # TD_tt_matrix = 60*(TD_distance_matrix/1000)/speed

    DT_tt_matrix = 60*(DT_distance_matrix)/speed
    TD_tt_matrix = 60*(TD_distance_matrix)/speed

    depot_df = gpd.GeoDataFrame(depot_df, crs=4326, geometry=[Point(xy) for xy in zip(depot_df.longitude, depot_df.latitude)])

    ss_depot_distance_matrix = pd.DataFrame(columns = depot_df['depot_id'], index = substation_df['short_name'])
    for i,dp in depot_df.to_crs(32643).iterrows():
        ss_depot_distance_matrix[dp['depot_id']] = list((substation_df.to_crs(32643).distance(dp['geometry'])*1.2).round())

    # DT_cost_matrix = (DT_distance_matrix/1000)*power_consumption_per_km*electricity_tariff_per_unit
    # TD_cost_matrix = (TD_distance_matrix/1000)*power_consumption_per_km*electricity_tariff_per_unit
    
    power_consumption_per_km = Decimal(power_consumption_per_km)
    DT_cost_matrix = (DT_distance_matrix)*power_consumption_per_km*electricity_tariff_per_unit
    TD_cost_matrix = (TD_distance_matrix)*power_consumption_per_km*electricity_tariff_per_unit
    
    ss_depot_cost_matrix = (ss_depot_distance_matrix/1000)*feeder_line_cost_per_km

    # 2. Variables and variable costs
    allocation_df = schedule_df[(schedule_df['direction'] == 'Start Shuttle') | (schedule_df['direction'] == 'End Shuttle')]

    bus_distance_cost_variables = [] #cost
    bus_distance_decision_variables = [] #1 or 0
    bus_dead_km_distance_variables = []
    for schedule_id in allocation_df['schedule_id'].unique():
        temp_df = allocation_df[allocation_df['schedule_id'] == schedule_id]
        for i, dp in depot_df.iterrows():
            depot_id = dp['depot_id']
            bus_distance_decision_variables.append(f"{schedule_id}|{depot_id}")
            cost = 0
            distance = 0
            for j, dp2 in temp_df.iterrows():
                if dp2['direction'] == 'Start Shuttle':
                    end_terminal = dp2['end_terminal']
                    end_terminal_id = terminal_df[terminal_df['terminal_name'] == end_terminal]['terminal_id'].iloc[0]
                    cost += DT_cost_matrix.at[depot_id, end_terminal_id]
                    distance += DT_distance_matrix.at[depot_id, end_terminal_id]
                elif dp2['direction'] == 'End Shuttle':
                    start_terminal = dp2['start_terminal']
                    start_terminal_id = terminal_df[terminal_df['terminal_name'] == start_terminal]['terminal_id'].iloc[0]
                    cost += TD_cost_matrix.at[start_terminal_id, depot_id]
                    distance += TD_distance_matrix.at[start_terminal_id, depot_id]
            bus_distance_cost_variables.append(cost)
            bus_dead_km_distance_variables.append(distance)

    # candidate_depots_development_cost_variables = [i*1000000 for i in range(len(candidate_depots))]
    candidate_depots_development_cost_variables = candidate_depots_cost

    ss_depot_decision_variabes = []
    ss_depot_cost_variables = []
    for ss in ss_depot_cost_matrix.index:
        for depot in ss_depot_cost_matrix.columns:
            ss_depot_decision_variabes.append(f"{ss}|{depot}")
            ss_depot_cost_variables.append(ss_depot_cost_matrix.at[ss, depot])

    ss_depot_cost_variables = [float(value) for value in ss_depot_cost_variables]

    revenue_schedule_df = schedule_df[~schedule_df['direction'].str.contains('Shuttle', case=False, na=False)]
    scheduled_revenue_distances = revenue_schedule_df.groupby(['schedule_id']).agg({'trip_distance':sum}).reset_index().set_index('schedule_id', drop=True)

    final_dictionary = dict()
    for variable_name, dead_km_distance, cost in zip(bus_distance_decision_variables, bus_dead_km_distance_variables, bus_distance_cost_variables):
        schedule_id = variable_name.split("|")[0]
        # total_distance = scheduled_revenue_distances.at[schedule_id, 'trip_distance'] + float(dead_km_distance/1000)
        total_distance = scheduled_revenue_distances.at[schedule_id, 'trip_distance'] + float(dead_km_distance)
        if (total_distance >= assured_km) * (total_distance <= total_range):
            final_dictionary[variable_name] = cost
    final_dictionary

    bus_distance_cost_variables = list(final_dictionary.values())
    bus_distance_decision_variables = list(final_dictionary.keys())
    len(bus_distance_decision_variables)

    bus_distance_cost_variables = [float(value) for value in bus_distance_cost_variables]
    candidate_depots_development_cost_variables = [float(value) for value in candidate_depots_development_cost_variables]
    ss_depot_cost_variables = [float(value) for value in ss_depot_cost_variables]

    decision_var_bus = [LpVariable(i, lowBound=0, upBound=1, cat='Integer') for i in bus_distance_decision_variables]
    decision_var_depot = [LpVariable(i, lowBound=0, upBound=1, cat='Integer') for i in candidate_depots]
    decision_var_ss_depot = [LpVariable(i, lowBound=0, upBound=1, cat='Integer') for i in ss_depot_decision_variabes]

    ## MODEL
    model = LpProblem(name="Depot Allocation", sense=LpMinimize)

    # Objective Function Equation
    objective = lpSum([decision_var_bus[i]*bus_distance_cost_variables[i]*365*number_of_years for i in range(len(bus_distance_decision_variables))]) + lpSum([i*j for i,j in zip(decision_var_depot, candidate_depots_development_cost_variables)]) +lpSum([i*j for i,j in zip(decision_var_ss_depot, ss_depot_cost_variables)])

    # print(objective
    model.setObjective(objective)

    # every schedule must be allocated
    for schedule in allocation_df['schedule_id'].unique():
        model += lpSum([i for i in decision_var_bus if schedule == str(i).split("|")[0]]) <= 1, "schedule_constraint-"+str(schedule)
    # total schedules must be equal to number of buses
    model += lpSum([i for i in decision_var_bus]) == number_of_buses, "bus_constraint"

    # depot constraint
    for i, dp in  depot_df.iterrows():
        depot_name = dp['depot_name'].replace(" ","_")
        depot_name_index = [i.name for i in decision_var_depot].index(depot_name)
        model += lpSum([j for j in decision_var_bus if str(dp['depot_id']) == str(j).split("|")[1]]) <= int(dp['capacity'])*decision_var_depot[depot_name_index], "depot_constraint-"+str(dp['depot_id'])

    # ss depot constraint
    for i, dp in  depot_df.iterrows():
        depot_name = dp['depot_name'].replace(" ","_")
        depot_name_index = [i.name for i in decision_var_depot].index(depot_name)
        model += lpSum([j for j in decision_var_ss_depot if str(dp['depot_id']) == str(j).split("|")[1]]) == decision_var_depot[depot_name_index], "depot_ss_constraint-"+str(dp['depot_id'])

    # # other user specific contraints
    # for column in constraints:
    #   for col_val in constraints[column]:
    #     if constraints[column][col_val] == True:
    #       depots_in_constraint = list(depot_df[depot_df[column] == col_val]['depot_id'].unique())
    #       print(column, col_val)
    #       number_of_schedules = len(allocation_df[allocation_df[column] == col_val])

    #       model += lpSum([j for j in act_var if str(j).split("|")[1] in depots_in_constraint]) == number_of_schedules, "user_defined_constraint-"+col_val


    model.solve()
    print(" model.solve()", model.solve())
    model.objective.value()
    print("model.objective.value()", model.objective.value())

    IsFeasible=""
    if model.solve() == 1:
        IsFeasible="YES"
        new_allocation_results = [i.name for i in decision_var_bus if i.varValue == 1]
        new_allocation_depots = [i.name.replace("_"," ") for i in decision_var_depot if i.varValue == 1]
        new_allocation_ss_depots = [i.name for i in decision_var_ss_depot if i.varValue == 1]
        
        new_schedule_df = pd.DataFrame()
        for allocation in new_allocation_results:
            schedule_id = allocation.split("|")[0]
            depot_id = int(allocation.split("|")[1])
            temp_schedules = schedule_df[schedule_df['schedule_id'] == schedule_id]
            start_shuttle_index = temp_schedules[temp_schedules['direction'] == 'Start Shuttle'].index[0]
            end_shuttle_index = temp_schedules[temp_schedules['direction'] == 'End Shuttle'].index[0]

            # replace depot_name, start and end
            # depot_name = depot_df[depot_df['depot_id'] == int(depot_id)]['depot_name'].tolist()[0]
            depot_names = depot_df[depot_df['depot_id'] == int(depot_id)]['depot_name'].tolist()
            depot_name = depot_names[0]
            
            # map time and distance
            #start terminal_ids
            start_terminal_name = temp_schedules.at[start_shuttle_index, 'end_terminal']
            end_terminal_name = temp_schedules.at[end_shuttle_index, 'start_terminal']
            start_terminal_id = terminal_df[terminal_df['terminal_name'] == start_terminal_name]['terminal_id'].tolist()[0]
            end_terminal_id = terminal_df[terminal_df['terminal_name'] == end_terminal_name]['terminal_id'].tolist()[0]

            # travel distances and travel_times
            # start_shuttle_td = DT_distance_matrix.at[depot_id, start_terminal_id]/1000
            # end_shuttle_td = TD_distance_matrix.at[end_terminal_id, depot_id]/1000
            start_shuttle_td = DT_distance_matrix.at[depot_id, start_terminal_id]
            end_shuttle_td = TD_distance_matrix.at[end_terminal_id, depot_id]
            start_shuttle_tt = DT_tt_matrix.at[depot_id, start_terminal_id]
            end_shuttle_tt = TD_tt_matrix.at[end_terminal_id, depot_id]

            # estimated start and end times
            start_shuttle_start_time = start_shuttle_tt
            end_shuttle_start_time = end_shuttle_tt
            estimated_start_shuttle_trip_end_time = temp_schedules.at[start_shuttle_index, 'start_time'] + temp_schedules.at[start_shuttle_index, 'travel_time']
            new_start_shuttle_start_time = estimated_start_shuttle_trip_end_time - start_shuttle_tt

            # #assign new values - start shuttle
            temp_schedules['depot_id'] = depot_name
            temp_schedules.at[start_shuttle_index, 'start_terminal'] = depot_name
            temp_schedules.at[start_shuttle_index, 'start_time'] = new_start_shuttle_start_time
            temp_schedules.at[start_shuttle_index, 'travel_time'] = start_shuttle_tt
            temp_schedules.at[start_shuttle_index, 'trip_distance'] = start_shuttle_td

            # end shuttle assign new values
            temp_schedules.at[end_shuttle_index, 'end_terminal'] = depot_name
            temp_schedules.at[end_shuttle_index, 'travel_time'] = end_shuttle_tt
            temp_schedules.at[end_shuttle_index, 'trip_distance'] = end_shuttle_td

            new_schedule_df = pd.concat([new_schedule_df, temp_schedules], ignore_index=True)

        temp_schedules
        new_schedule_df
        # new_schedule_df.to_csv('new_schedule_df.csv', index=False)
        # Drop the 'geometry' column from depot_df, terminal_df, and substation_df
        depot_df = depot_df.drop(columns=['geometry'])
        # terminal_df = terminal_df.drop(columns=['geometry'])
        substation_df = substation_df.drop(columns=['geometry'])

        depot_result = {
                "new_schedule_df": new_schedule_df,
                "depot_df": depot_df,
                "terminal_df": terminal_df,
                "substation_df": substation_df
            }

        return IsFeasible, depot_result
    
    else:
        IsFeasible="NO"
        depot_result = {}

        return IsFeasible, depot_result