import sys
import pandas as pd

def create_schedule_block_df(depot_list,candidate_terminal_charging_location_list, schedule_df, min_charging_time, distance_matrix, charging_deadkm_distance, speed = 12):
    time_required_for_charging_deadkm = (60*(charging_deadkm_distance/speed))*2.1

    #1. CREATING SCHEDULE BLOCKS
    schedule_block_df = pd.DataFrame(columns=['block', 'schedule_id', 'type' ,'route_number', 'start_point', 'end_point', 'start_time', 'end_time', 'tt', 'distance', 'layover', 'depot'])
    candidate_charging_locations = depot_list + candidate_terminal_charging_location_list
    distance_matrix = distance_matrix[candidate_charging_locations]
    candidate_charging_locations = [i for i,dp in distance_matrix.iterrows() if min(list(dp)) <= charging_deadkm_distance]
    actual_charging_location = [distance_matrix.columns[list(dp).index(min(list(dp)))] for i, dp in distance_matrix.iterrows() if min(list(dp)) <= charging_deadkm_distance]
    charging_location_reference = {loc:loc2 for loc, loc2 in zip(candidate_charging_locations,actual_charging_location)}
    print(charging_location_reference)

    for schedule in schedule_df['schedule_id'].unique():
        x = schedule_df[schedule_df['schedule_id'] == schedule]
        x['layover'] = [start_nxt-end for end, start_nxt in zip(x['end_time'], x['start_time'].shift(-1))]
        x.iloc[-1, x.columns.get_loc('layover')] = x.iloc[1, x.columns.get_loc('start_time')] + (1440 - x.iloc[-1, x.columns.get_loc('end_time')])
        x['block'] = [(end_loc in actual_charging_location)*(layover > min_charging_time) if (end_loc in actual_charging_location) else (end_loc in candidate_charging_locations)*(layover > min_charging_time+time_required_for_charging_deadkm) for end_loc, layover in zip(x['end_terminal'],x['layover'])]
        x['block'] = x['block'][::-1].cumsum()[::-1]
        depot = x.iloc[0, x.columns.get_loc('depot_id')]
        block_id = 0
        for block in list(x['block'].unique()):
            block_id += 1
            y = x[x['block'] == block]
            schedule_id = y.iloc[0, y.columns.get_loc('schedule_id')]
            route_number = y.iloc[0, y.columns.get_loc('route_number')]
            start_point = y.iloc[0, y.columns.get_loc('start_terminal')]
            end_point = y.iloc[-1, y.columns.get_loc('end_terminal')]
            start_time = y.iloc[0, y.columns.get_loc('start_time')]
            end_time = y.iloc[-1, y.columns.get_loc('end_time')]
            tt = y['travel_time'].sum()
            distance = y['trip_distance'].sum()
            layover = y.iloc[-1, y.columns.get_loc('layover')]
            if end_point not in actual_charging_location:
                # start shuttle
                schedule_block_df.loc[len(schedule_block_df)] = [block_id, schedule_id, 'normal block', route_number, start_point, end_point, start_time, end_time, tt, distance, 0, depot]
                terminal_name = end_point
                charging_point_name = charging_location_reference[end_point]
                distance = distance_matrix.at[terminal_name, charging_point_name] # ADD two -> need to have two matrix...
                tt = 60*(distance/speed)
                start_time = end_time
                end_time = start_time+tt
                charging_layover = layover - tt - tt
                block_id += 1
                schedule_block_df.loc[len(schedule_block_df)] = [block_id, schedule_id, 'to charge point trip' ,route_number, terminal_name, charging_point_name, start_time, end_time, tt, distance, charging_layover, depot]

                # end shuttle
                start_time = end_time + charging_layover
                end_time = start_time+tt
                block_id += 1
                schedule_block_df.loc[len(schedule_block_df)] = [block_id, schedule_id, 'to terminal trip' ,route_number,
                                                                 charging_point_name, terminal_name, start_time,
                                                                 end_time, tt, distance, 0, depot]

            else:
                schedule_block_df.loc[len(schedule_block_df)] = [block_id, schedule_id, 'normal block' ,route_number, start_point, end_point, start_time, end_time, tt, distance, layover, depot]
    return schedule_block_df

def set_up_blocks_for_simulation(schedule_block_df, sim_days=2):
    #2. SET UP FOR SIM DAYS
    schedule_block_sim_df = pd.DataFrame()
    for schedule in schedule_block_df['schedule_id'].unique():
        day_df = schedule_block_df[schedule_block_df['schedule_id'] == schedule]
        for i in range(sim_days):
            x = day_df.copy()
            x['start_time'] = x['start_time'] + (1440 * i)
            x['end_time'] = x['end_time'] + (1440 * i)
            x['day'] = i+1
            schedule_block_sim_df = pd.concat([schedule_block_sim_df, x], ignore_index=True)
    return (schedule_block_sim_df)