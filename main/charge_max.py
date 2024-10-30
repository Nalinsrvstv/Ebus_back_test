# 1. IMPORT LIBRARIES AND SCRIPS
import sys
import time
import pandas as pd
from . import viz
from . import import_files
from . import schedule_block
from . import bus_and_charging_system
from . import simulate_charging2
# from . import data_analytics
import warnings
from .models import (ObjectiveFunctions)

warnings.filterwarnings("ignore")

def run_algorithm(project, workflow_type, depot_list, bus_models_list, charger_model_list, opportunity_charging, static_pc_per_km, candidate_terminal_charging_location_list, base_chargers_list, simulation_parameters, advanace_settings, depotallocation_scenario_id):
    start_time = time.time()
    current_objective_function = None
    ObjectiveFunctions.objects.create(object_value=current_objective_function, project_id=project)
    #depot - GREENCELL MAGOB DEPOT # routes - '13','16','19'
    #depot - OLECTRA ALTHAN DEPOT #routes  '21', '15AA', '15CC'
    # 2. IMPORT FILES
    # depot_list = ['OLECTRA ALTHAN DEPOT', 'GREENCELL MAGOB DEPOT'] #user input
    # route_no_list = ['21', '15AA', '15CC', '13','16','19']
    # depot_df,terminal_df,schedule_df, distance_matrix, bus_models, charger_models = import_files.import_files(depot_list, route_no_list)
    depot_df,terminal_df,schedule_df, distance_matrix, bus_models, charger_models = import_files.import_files(project, workflow_type, depot_list, depotallocation_scenario_id)

    print('depot_df\n', depot_df.head(), '\n')
    print('terminal_df\n', terminal_df.head(), '\n')
    print('schedule_df\n', schedule_df.head(11), '\n')
    print('bus_models\n', bus_models, '\n')
    print('charger_models\n', charger_models, '\n')
    print('distance_matrix\n', distance_matrix.head(5), '\n')
    print('number of schedules is ', len(list(schedule_df['schedule_id'].unique())),'\n')

    # viz.vizualize_depot_terminal_in_map(depot_df, terminal_df)
    # viz.vizualize_schedule_in_bar(schedule_df, unique_x = 'schedule_id', start_time='start_time', event_duration='travel_time', event_type='depot_id', day_to_show=1, yaxis_title = 'Schedule')

    reserving_charge = simulation_parameters["reserve_charge"] / 100
    state_of_health = simulation_parameters["state_of_health"] / 100
    maximum_deadkm = simulation_parameters["maximum_deadkm"]
    minimum_charging_time = simulation_parameters["minimum_charging_time"]

    manouver_time = advanace_settings["manoeuvre_duration"]
    minimum_layover_nightcharging = advanace_settings["minimum_layover_nightcharging"]
    simulation_days = advanace_settings["simulation_days"]

    # 3. CREATE SCHEDULE BLOCKS
    # opportunity_charging = 1 #user input

    if opportunity_charging:
        candidate_terminal_charging_location_list = candidate_terminal_charging_location_list
        # candidate_terminal_charging_location_list = []
        # min_charging_time = 30 #user input
        min_charging_time = minimum_charging_time
    else:
        min_charging_time = 180
        # candidate_terminal_charging_location_list = []
        candidate_terminal_charging_location_list = candidate_terminal_charging_location_list

    charging_deadkm_distance = maximum_deadkm
    schedule_block_df = schedule_block.create_schedule_block_df(depot_list, candidate_terminal_charging_location_list, schedule_df, min_charging_time, distance_matrix, charging_deadkm_distance)
    print('schedule_block_df\n', schedule_block_df.head(12), '\n')

    # 4. SET UP FOR SIMULATION
    schedule_block_sim_df = schedule_block.set_up_blocks_for_simulation(schedule_block_df, sim_days=simulation_days)
    print('schedule_block_sim_df\n', schedule_block_sim_df.head(12), '\n')
    # schedule_block_sim_df.to_csv('schedule_block_sim_df.csv', index=False)

    # 5. CREATE BUS SYSTEM
    # bus_models_list = ['Urban 9/12m', 'Urban 9/12m'] #user input
    bus_models_for_depot = {i:j for i,j in zip(depot_list, bus_models_list)}
    bus_system = []
    for depot in depot_list:
        # np_bc = bus_models.at[bus_models_for_depot[depot], 'battery_capacity'] #kwh
        # pc_per_km = bus_models.at[bus_models_for_depot[depot], 'power_consumption']
        # gvw = bus_models.at[bus_models_for_depot[depot], 'GVW']
        np_bc = bus_models.loc[bus_models['short_name'] == bus_models_for_depot[depot], 'battery_capacity'].values[0]
        # pc_per_km = bus_models.loc[bus_models['short_name'] == bus_models_for_depot[depot], 'power_consumption'].values[0]
        pc_per_km = static_pc_per_km.get(bus_models_for_depot[depot])
        gvw = bus_models.loc[bus_models['short_name'] == bus_models_for_depot[depot], 'gross_vehicle_weight'].values[0]
        # minimum_soc = 0.2 # in percentage 
        minimum_soc = reserving_charge 
        state_of_health = state_of_health 
        power_consumption_per_km, reserve_charge, usable_battery_capacity = bus_and_charging_system.estimate_power_consumption_per_km(power_consumption_per_tonne_per_km = pc_per_km/gvw, bus_gvw= gvw, name_plate_battery_capacity=np_bc,state_of_health=state_of_health, minimum_soc = minimum_soc)
        schedule_block_df_fr_depot = schedule_block_df[schedule_block_df['depot'] == depot]
        bus_system = bus_system+bus_and_charging_system.create_bus_system(name_plate_battery_capacity=np_bc, power_consumption_per_km=power_consumption_per_km, usable_battery_capacity=usable_battery_capacity, schedule_block_df=schedule_block_df_fr_depot)
    print('bus_system', bus_system) #list of dictionaries

    # 6. CREATE CHARGER SYSTEM
    # charger_model_list = ['Model 3','Model 3']  #user input
    candidate_charging_locations = depot_list + candidate_terminal_charging_location_list
    # charger_capacity = [charger_models.at[i,'Charger Capacity'] for i in charger_model_list]
    charger_capacity = [charger_models.loc[charger_models['short_name'] == i, 'charger_capacity'].values[0] for i in charger_model_list]
    charger_type = [charger_models.loc[charger_models['short_name'] == j, 'charger_type'].values[0] for j in charger_model_list]
    # charger_data = {loc: 5 for loc in candidate_charging_locations}
    charger_data = {loc:val for loc, val in zip(candidate_charging_locations, base_chargers_list)}
    charger_capacity_dict = {loc:cap for loc, cap in zip(candidate_charging_locations,charger_capacity)}
    charger_type_dict = {loc:typ for loc, typ in zip(candidate_charging_locations,charger_type)}
    charger_system = bus_and_charging_system.create_base_charging_system(charger_data=charger_data, charger_capacity=charger_capacity_dict,charger_type=charger_type_dict)
    print('charger_system', charger_system)#list of dictionaries

    #7. SIMULATE ### - ALGORITHM STARTS HERE...
    print("---------------------<<BASE SIMULATION START>>----------------------")
    print('charger_data', charger_data)

    charging_schedule_df, y, obj_func = simulate_charging2.simulate_charging(schedule_block_sim_df, bus_system, charger_system, 'base_sim', minimum_layover_nightcharging, manouver_time)
    current_objective_function = obj_func
    ObjectiveFunctions.objects.create(object_value=current_objective_function, project_id=project)
    selected_option = {'option':charger_data, 'obj_func':obj_func, 'charging_schedule_df':charging_schedule_df}
    feasibility = obj_func >= 0
    IsFeasible=""

    
    if feasibility:
        IsFeasible="YES"
        print('The no. of base chargers meets the power demand')
        y_dead = y[((y['type'] == 'to charge point trip')|(y['type'] == 'to terminal trip'))*(y['day'] == 2)]
        y_depot_dead = y_dead.groupby('depot').agg({'distance':sum})
        y_depot_dead_dict = {i:j for i,j in zip(y_depot_dead.index, y_depot_dead['distance'])}

    print("---------------------<<EPOCH START>>----------------------")
    step_size = 1
    epoch = 0
    
    while feasibility == 0:
        epoch += 1
        print(f"EPOCH START----------------->>> {epoch} with step size {step_size}")
        options = simulate_charging2.generate_options_for_epoch(charger_data, epoch, step_size)
        iteration = 0
        previous_solution = selected_option
        for charger_data_key in options:
            iteration += 1
            charger_data = options[charger_data_key]
            print('iteration ----->>>', iteration)
            print('charger data is ', charger_data)
            charger_system = bus_and_charging_system.create_base_charging_system(charger_data=charger_data,
                                                                                charger_capacity=charger_capacity_dict, charger_type=charger_type_dict)
            # print('charger_data', charger_data)
            bus_system = bus_and_charging_system.create_bus_system(name_plate_battery_capacity=np_bc,
                                                                power_consumption_per_km=power_consumption_per_km,
                                                                usable_battery_capacity=usable_battery_capacity,
                                                                schedule_block_df=schedule_block_df)

            charging_schedule_df, y, obj_func = simulate_charging2.simulate_charging(schedule_block_sim_df, bus_system,
                                                                                    charger_system, f'{epoch}_{iteration}', minimum_layover_nightcharging, manouver_time)

            if obj_func > selected_option['obj_func']:
                selected_option = {'option':charger_data, 'obj_func':obj_func, 'charging_schedule_df':charging_schedule_df}
                selected_key = charger_data_key
                step_size = 1
            if obj_func >= 0:
                feasibility = 1
                IsFeasible="YES"
                print('Feasible solution')
                
                
                
                break
            print('objective function is', obj_func)
            print('______________________________________')

        charger_data = selected_option['option']
        current_objective_function = selected_option['obj_func']
        ObjectiveFunctions.objects.create(object_value=current_objective_function, project_id=project)

        print('selected in epoch', epoch, iteration, selected_option['obj_func'], charger_data)
        print('================EPOCH END==================')

        if (selected_option == previous_solution) * (feasibility == 0):
            step_size += 1
            if step_size == 10:
                end_time = time.time()
                elapsed_time = end_time - start_time
                IsFeasible="NO"
                result = {
                    "error": "Infeasible Solution",
                    "elapsed_time": elapsed_time
                    }
                print('Infeasible Solution')
                current_objective_function = None
                ObjectiveFunctions.objects.create(object_value=current_objective_function, project_id=project)

                return IsFeasible, result
                sys.exit()
        elif feasibility == 1:
            IsFeasible="YES"
            print('Feasible Solution')
            y_dead = y[((y['type'] == 'to charge point trip')|(y['type'] == 'to terminal trip'))*(y['day'] == 2)]
            y_depot_dead = y_dead.groupby('depot').agg({'distance':sum})
            y_depot_dead_dict = {i:j for i,j in zip(y_depot_dead.index, y_depot_dead['distance'])}
            break


    charging_schedule_df['charger_id_'] = [f'{i}-{j}|{charger_capacity_dict[i]} kw' for i,j in zip(charging_schedule_df['location'], charging_schedule_df['charger_id'])]
    schedule_routeno_link = schedule_df.drop_duplicates(subset = 'schedule_id', keep = 'first')[['schedule_id','route_number']]
    # charging_schedule_df = charging_schedule_df.merge(schedule_routeno_link, left_on='schedule_id', right_on='schedule_id', how='left').drop(columns=['schedule_id'])
    charging_schedule_df = charging_schedule_df.merge(schedule_routeno_link, left_on='schedule_id', right_on='schedule_id', how='left')

    # viz.vizualize_schedule_in_bar(charging_schedule_df, unique_x ='charger_id_', start_time='start_time', event_duration='charging_duration', event_type='route_number', day_to_show = 2, yaxis_title='Charger ID (Location - ID - Capacity)')

    # Record the end time
    end_time = time.time()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time
    print('schedule', schedule_block_df.columns.tolist())
    print("Elapsed time:", elapsed_time, "seconds")

    current_objective_function = None
    ObjectiveFunctions.objects.create(object_value=current_objective_function, project_id=project)


    result = {
        "IsFeasible": IsFeasible,
        "elapsed_time": elapsed_time,
        "charger_system": charger_system,
        "charging_schedule_df": charging_schedule_df,
        "power_consumption_per_km": power_consumption_per_km,
        "schedule_df": schedule_df,
        "gvw": gvw, 
        "np_bc": np_bc,
        "depot_df": depot_df,
        "terminal_df": terminal_df,
        "y_depot_dead_dict": y_depot_dead_dict,
    }

    # analytics_data = data_analytics.data_analytics(charger_system, charging_schedule_df, power_consumption_per_km, schedule_df, gvw, np_bc, depot_df, terminal_df)

    return IsFeasible, result
