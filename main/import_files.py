from .models import (
    Schedule,
    Depot,
    Terminal,
    BusModel,
    ChargerModel,
    DepotAllocationScenario,
    DepotAllocation_Schedule

)
import sys

import pandas as pd
import geopy.distance

# pandas settings
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
# pd.options.display.width=None

def import_files(project, workflow_type, depot_list, depotallocation_scenario_id):

    depots = Depot.objects.filter(depot_name__in=depot_list, project_id=project).distinct()
    depot_df = pd.DataFrame(list(depots.values()))
    
    # Fetch or use the provided schedules data based on workflow_type
    if workflow_type == 3:
        schedules = Schedule.objects.filter(project_id=project, depot_id__in=depot_list)
        schedule_df = pd.DataFrame(list(schedules.values()))

    elif workflow_type == 2:
        depot_scenario_data = DepotAllocationScenario.objects.get(project_id=project, scenario_id=depotallocation_scenario_id)
        schedules = DepotAllocation_Schedule.objects.filter(scenario=depot_scenario_data)
        schedule_df = pd.DataFrame(list(schedules.values()))

    else:
        schedule_df = pd.DataFrame() 

    schedule_df['trip_number'] = schedule_df['trip_number'].astype(int)
    schedules_df_ordered  =pd.DataFrame()
    for schedule in schedule_df['schedule_id'].unique():
        schedule_id_rows = schedule_df[schedule_df['schedule_id'] == schedule]
        schedule_id_rows = schedule_id_rows.sort_values(['trip_number'], ascending=True)
        schedules_df_ordered = pd.concat([schedules_df_ordered, schedule_id_rows], ignore_index=True)

    schedule_df = schedules_df_ordered

    terminal_names = set()
    for schedule in schedules:
        if schedule.start_terminal:
            terminal_names.add(schedule.start_terminal)
        if schedule.end_terminal:
            terminal_names.add(schedule.end_terminal)

    terminals = Terminal.objects.filter(
        terminal_name__in=terminal_names, project_id=project
    ).distinct()
    terminal_df = pd.DataFrame(list(terminals.values()))

    # print(schedule_df['Route Number'].unique())
    # sys.exit()
    # schedule_df = schedule_df[schedule_df['Schedule ID'].isin(schedule_id_list)]
    # schedule_df['start_time'] = [60 * int(i.split(":")[0]) + int(i.split(":")[1]) for i in schedule_df['Start Time']]
    # schedule_df['end_time'] = [60 * int(i.split(":")[0]) + int(i.split(":")[1]) for i in schedule_df['End Time']]
    # schedule_df['travel_time'] = [60 * int(i.split(":")[0]) + int(i.split(":")[1]) for i in schedule_df['Travel Time']]
    # print('schedule_df\n', schedule_df.head(), '\n')

    schedule_df['start_time'] = schedule_df['start_time'].astype(int)
    schedule_df['travel_time'] = schedule_df['travel_time'].astype(int)

    # Calculate end_time by adding start_time and travel_time
    schedule_df['end_time'] = schedule_df['start_time'] + schedule_df['travel_time'] 

    point_data_1 = depot_df[['depot_name', 'latitude', 'longitude']].rename(columns={'depot_name': 'Name'})
    point_data_2 = terminal_df[['terminal_name', 'latitude', 'longitude']].rename(columns={'terminal_name': 'Name'})
    combined_df = pd.concat([point_data_1, point_data_2]).set_index('Name', drop=True)
    # print(combined_df)

    distance_matrix = pd.DataFrame(index=combined_df.index, columns=combined_df.index)

    for i in distance_matrix.index:
        for j in distance_matrix.columns:
            coords_1 = (combined_df.at[i, 'latitude'], combined_df.at[i, 'longitude'])
            coords_2 = (combined_df.at[j, 'latitude'], combined_df.at[j, 'longitude'])
            distance_matrix.at[i, j] = geopy.distance.geodesic(coords_1, coords_2).km

    # Fetch the specific bus models and charger models based on the input lists
    buses = BusModel.objects.all().distinct()
    bus_models = pd.DataFrame(list(buses.values()))

    chargers = ChargerModel.objects.all().distinct()
    charger_models = pd.DataFrame(list(chargers.values()))

    # bus_models = pd.read_csv("https://raw.githubusercontent.com/ArvindManickam/Files/main/bus_models.csv", index_col = 'short_name')
    # charger_models = pd.read_csv("https://raw.githubusercontent.com/ArvindManickam/Files/main/charger_models.csv", index_col='short_name')
    
    return depot_df, terminal_df, schedule_df, distance_matrix, bus_models, charger_models