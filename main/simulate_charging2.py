import sys
import pandas as pd

def get_bus_ref_by_id(id, bus_system_dic):
    return bus_system_dic.index([i for i in bus_system_dic if i['id'] == id][0])

def get_charger_ref_by_loc_and_free_at(location, current_time, charger_system):
    free_chargers = [i for i in charger_system if (i['location'] == location) * (i['free_at'] <= current_time)]
    if len(free_chargers) > 0:
        max_charger_capacity = max([i['charger_capacity'] for i in free_chargers])
        free_chargers = [i for i in free_chargers if i['charger_capacity'] == max_charger_capacity]
        return charger_system.index(free_chargers[0])
    else:
        return False

def update_bus_soc(bus_data, pc):
    bus_data['SoC'] = bus_data['SoC'] - pc
    bus_data['DoD'] = bus_data['DoD'] + pc
    bus_data['lowest_soc'] = min(bus_data['lowest_soc'], bus_data['SoC'])
    return bus_data

def check_dod_lower_than_deficit(layover_time, dod, deficit, minimum_layover_nightcharging):
    if layover_time >= minimum_layover_nightcharging:
        top_up = dod
    else:
        top_up = deficit
    return top_up <= dod

def check_charging_duration_available_with_specific_charger(layover_time, dod, deficit, charger_capacity, minimum_layover_nightcharging, manouver_time):
    # print('layover_time_', layover_time)
    if layover_time >= minimum_layover_nightcharging:
        top_up = dod
    else:
        top_up = deficit
    charging_duration = (60 * (top_up / charger_capacity))
    gross_charging_duration = charging_duration + manouver_time
    enough_charging_duration_available = charging_duration < layover_time
    return enough_charging_duration_available, top_up, gross_charging_duration

def charge_bus(charge_start_time, charging_duration, top_up, bus_data, charger_data):
    charger_data['free_at'] = charge_start_time + charging_duration
    charger_data['charger_status'] = 1
    bus_data['SoC'] = bus_data['SoC'] + top_up
    bus_data['DoD'] = bus_data['DoD'] - top_up
    bus_data['queue'] = 0
    # print(bus_data)
    # print("--------------------------------------------------")
    return bus_data, charger_data, [bus_data['id'], charger_data['location'], charge_start_time, charger_data['free_at'], charging_duration, charger_data['id'], bus_data['SoC'] - top_up, top_up, bus_data['SoC']]

def add_bus_to_queue(bus_data, layover_time, current_time, location, charger_system, manouver_time):
    if layover_time >= 240:
        top_up = bus_data['DoD']
    else:
        top_up = bus_data['deficit']
    charger_system_in_location = [i for i in charger_system if (i['location'] == location)]
    if len(charger_system_in_location) > 0:
        charger_capacity = max([i['charger_capacity'] for i in charger_system_in_location])
        charging_duration = 60 * (top_up / charger_capacity)
        gross_charging_duration = charging_duration + manouver_time
    else:
        charger_capacity, gross_charging_duration = 0,0

    bus_data['queue'] = 1
    bus_data['location'] = location
    bus_data['queue_exit_time'] = current_time+layover_time-gross_charging_duration
    bus_data['next_trip_time'] = current_time+layover_time

    return bus_data

def clear_bus_queue_before(clear_queue_before, bus_system):
    for bus_data in bus_system:
        if (bus_data['queue_exit_time'] < clear_queue_before) * (bus_data['queue'] == 1):
            bus_data['queue'] = 0
            bus_data['location'] = '-'
    return bus_system

def generate_options_for_epoch(charger_data, epoch, step_size):
    charger_data_options = {}
    for k in charger_data:
        x = charger_data.copy()
        x[k] += step_size
        charger_data_options[k] = x
    return charger_data_options

def simulate_charging(schedule_status, bus_system, charger_system, name, minimum_layover_nightcharging, manouver_time):
    event_df = pd.DataFrame(columns=['schedule_id', 'loop', 'event_type', 'origin', 'destination', 'start_time', 'end_time', 'pc', 'soc', 'when', 'queue_exit_time'])
    # print('charger system ->>', charger_system)
    charging_schedule = pd.DataFrame(columns=['schedule_id', 'location', 'start_time', 'end_time', 'charging_duration', 'charger_id', 'start_soc', 'top_up', 'end_soc'])
    lowest_soc = 99999999  # objective_function
    schedule_status['pc'] = [dist*bus_system[get_bus_ref_by_id(i, bus_system)]['PC_per_km'] for i, dist in zip(schedule_status['schedule_id'], schedule_status['distance'])]
    schedule_status = schedule_status.sort_values(['end_time'], ascending=True)

    loop = 0

    for i,dp in schedule_status.iterrows():
        loop += 1

        #get chargers to set free
        charger_system = sorted(charger_system, key=lambda x: x['free_at'])
        free_chargers_before = dp['end_time']
        for charger_data in charger_system:
            if (charger_data['free_at'] <= free_chargers_before) * (charger_data['charger_status'] == 1):

                # clear queue
                bus_system = sorted(bus_system, key=lambda x: x['queue_exit_time'])
                bus_system = clear_bus_queue_before(clear_queue_before = charger_data['free_at'], bus_system=bus_system)

                # get bus
                charger_data['charger_status'] = 0
                if len([bus_data for bus_data in bus_system if (bus_data['location'] == charger_data['location']) * (bus_data['queue'] == 1)]) > 0:

                    # fetch the first bus that needs to exit earliest
                    bus_data = [bus_data for bus_data in bus_system if (bus_data['location'] == charger_data['location']) * (bus_data['queue'] == 1)][0]
                    enough_charging_duration_available, top_up, charging_duration = check_charging_duration_available_with_specific_charger(layover_time=bus_data['next_trip_time'] - charger_data['free_at'], dod=bus_data['DoD'], deficit=bus_data['deficit'], charger_capacity=charger_data['charger_capacity'],minimum_layover_nightcharging=minimum_layover_nightcharging, manouver_time=manouver_time)
                    if enough_charging_duration_available:
                        # print('charging bus from queue')
                        bus_data, charger_data, charging_schedule.loc[len(charging_schedule)] = charge_bus(charge_start_time= charger_data['free_at'], charging_duration=charging_duration, top_up=top_up, bus_data=bus_data, charger_data=charger_data)
                        da = charging_schedule.loc[len(charging_schedule) - 1]
                        event_df.loc[len(event_df)] = [da['schedule_id'], loop, 'charging', da['location'], da['location'], da['start_time'], da['end_time'], da['top_up'], bus_data['SoC'], 'after queue', bus_data['queue_exit_time']]

        # 1. GET BUS STATUS
        schedule_id = dp['schedule_id']
        bus_ref = get_bus_ref_by_id(schedule_id, bus_system)
        bus_data = bus_system[bus_ref]

        # 2. UPDATE BUS CHARGING
        bus_data = update_bus_soc(bus_data = bus_data, pc = dp['pc'])
        # lowest_soc = round(min(lowest_soc, bus_data['SoC']),2) # remove!!!
        event_df.loc[len(event_df)] = [schedule_id, loop, 'trip', dp['start_point'], dp['end_point'], dp['start_time'], dp['end_time'], -dp['pc'], bus_data['SoC'], 'trip', bus_data['queue_exit_time']]

        # 3 CHECK IF DOD IS LOWER THAN DEFICIT
        deficit_lower_than_DoD = check_dod_lower_than_deficit(layover_time=dp['layover'], dod= bus_data['DoD'],deficit= bus_data['deficit'],minimum_layover_nightcharging=minimum_layover_nightcharging)

        if deficit_lower_than_DoD:
            # 3. GET THE CHARGER
            charger_ref = get_charger_ref_by_loc_and_free_at(location = dp['end_point'], current_time = dp['end_time'], charger_system=charger_system)

            enough_charging_duration_available = False
            if type(charger_ref) is int: #charger_available
                charger_data = charger_system[charger_ref]
                # print(dp['end_point'], 'charger_data', charger_data)
                enough_charging_duration_available, top_up, charging_duration = check_charging_duration_available_with_specific_charger(layover_time=dp['layover'], dod= bus_data['DoD'], deficit= bus_data['deficit'], charger_capacity= charger_data['charger_capacity'],minimum_layover_nightcharging=minimum_layover_nightcharging, manouver_time=manouver_time)

            # 5. CHARGE BUS, UPDATE BUS AND CHARGER VARIABLE
            if enough_charging_duration_available:
                # print('charging_duration_available')
                bus_data, charger_data, charging_schedule.loc[len(charging_schedule)]  = charge_bus(charge_start_time=dp['end_time'],charging_duration= charging_duration, top_up = top_up, bus_data=bus_data, charger_data=charger_data)
                da = charging_schedule.loc[len(charging_schedule)-1]
                event_df.loc[len(event_df)] = [da['schedule_id'], loop, 'charging', da['location'], da['location'], da['start_time'], da['end_time'], da['top_up'], bus_data['SoC'], 'direct', bus_data['queue_exit_time']]
            else:
                bus_data = add_bus_to_queue(bus_data = bus_data, layover_time=dp['layover'], current_time=dp['end_time'], location = dp['end_point'], charger_system=charger_system, manouver_time=manouver_time)

    # print('charging schedule\n', charging_schedule)
    # print('lowest_soc', lowest_soc)
    # print('bus_system', bus_system)
    # print('charger_system', charger_system)
    # print('charging_schedule', list(charging_schedule.columns))
    lowest_soc = sum([i['lowest_soc']-i['reserve_soc'] for i in bus_system if i['lowest_soc']+1 < i['reserve_soc']]) # round off error..
    # print('bus system', len(bus_system), bus_system)
    # print('bus wise lowest soc', [i['lowest_soc'] for i in bus_system])
    # print('total deficit SoC', lowest_soc)
    x = pd.DataFrame()
    x['id'] = [i['id'] for i in bus_system]
    x['lowest_soc'] = [i['lowest_soc'] for i in bus_system]
    # x.to_csv(f'crosscheck\\{name}.csv', index=False)
    # event_df.to_csv(f'trips\\{name}.csv', index=False)
    # print('file saved as ', name)
    return charging_schedule, schedule_status, lowest_soc