import sys


def create_bus_system(name_plate_battery_capacity, power_consumption_per_km, usable_battery_capacity, schedule_block_df):
    deficit_data = schedule_block_df.groupby(['schedule_id']).agg({'distance': sum}).reset_index()
    deficit_data['pc'] = deficit_data['distance'] * power_consumption_per_km
    deficit_data['deficit'] = deficit_data['pc'] - usable_battery_capacity
    deficit_data.set_index('schedule_id', inplace=True, drop=True)
    #list of dictionary
    return [{'id':i, 'SoC':name_plate_battery_capacity, 'lowest_soc': name_plate_battery_capacity, 'DoD':0, 'PC_per_km':power_consumption_per_km, 'deficit':deficit_data.at[i, 'deficit'], 'queue':0, 'location':'-', 'queue_exit_time':0, 'next_trip_time':0, 'reserve_soc':round(name_plate_battery_capacity-usable_battery_capacity,1)} for i in list(schedule_block_df['schedule_id'].unique())]

def estimate_power_consumption_per_km(power_consumption_per_tonne_per_km, bus_gvw, name_plate_battery_capacity, state_of_health, minimum_soc):
    reserve_charge = name_plate_battery_capacity * minimum_soc
    usable_battery_capacity = (name_plate_battery_capacity*state_of_health) - reserve_charge
    power_consumption_per_km = power_consumption_per_tonne_per_km*bus_gvw
    return power_consumption_per_km, reserve_charge, usable_battery_capacity

#3. SET UP CHARGERS, BUS PROPERTIES
# dict containting charger_loc, charger_id, charger_capacity, charger_free_at
def create_base_charging_system(charger_data, charger_capacity, charger_type):
    charging_system = []
    id = 0
    for k,v in charger_data.items():
        for i in range(v):
            id += 1
            charging_system.append({'id':id,'location':k, 'charger_capacity': charger_capacity[k], 'charger_type': charger_type[k], 'free_at':0, 'charger_status':0})
    return charging_system
