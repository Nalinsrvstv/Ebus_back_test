import pandas as pd
import json

def data_analytics(charger_system, charging_schedule_df, power_consumption_per_km, schedule_df, gvw, np_bc, depot_df, terminal_df, y_depot_dead_dict):

    bus_schedules = []
    for depot in schedule_df['depot_id'].unique():
        depot_schedule = schedule_df[schedule_df['depot_id'] == depot]
        for schedule_id in depot_schedule['schedule_id'].unique():
            schedule = depot_schedule[depot_schedule['schedule_id'] == schedule_id]

            shuttle_trips = schedule[schedule['event_type'] == 'Non-revenue trip']
            total_shuttle_distance = sum(shuttle_trips['trip_distance'])

            revenue_trips = schedule[schedule['event_type'] != 'Non-revenue trip']
            total_revenue_distance = sum(revenue_trips['trip_distance'])

            total_distance = total_shuttle_distance + total_revenue_distance
            power_consumed = total_distance * power_consumption_per_km

            charging_schedule = charging_schedule_df[charging_schedule_df["schedule_id"] == schedule_id]
            bus_charging = []
            for i, row in charging_schedule.iterrows():
                bus_charging.append({"start_time": round(row["start_time"], 2), "end_time": round(row["end_time"], 2)})
            bus_entry = { 
                "schedule_id": schedule_id,
                "total_distance": total_distance,
                "dead_mileage": total_shuttle_distance,
                "revenue_distance": total_revenue_distance,
                "power_consumed": power_consumed,
                "gvw": int(gvw),  
                "np_bc": int(np_bc),  
                "depot_id": depot,
                "bus_charging": bus_charging
            }
            bus_schedules.append(bus_entry)
    bus_schedules_df = pd.DataFrame(bus_schedules)
    # TdeadMileage = sum(bus_schedules_df["dead_mileage"])
    # TrevenueDistance = sum(bus_schedules_df["revenue_distance"])

    # Tdistance = sum(bus_schedules_df["total_distance"])
    # Tdistance = sum(schedule_df['trip_distance'])

    # Tpower_consumed = sum(bus_schedules_df["power_consumed"])
    # Tpower_consumed = Tdistance * power_consumption_per_km

    depot_distances = []
    for depot in bus_schedules_df['depot_id'].unique():
        select_depot = bus_schedules_df[bus_schedules_df['depot_id'] == depot]
        deadMileage = sum(select_depot['dead_mileage'])
        
        # Add the value from y_depot_dead_dict if the depot exists in the dictionary
        if depot in y_depot_dead_dict:
            deadMileage += y_depot_dead_dict[depot]
        
        revenueDistance = sum(select_depot['revenue_distance'])
        totalDistance = deadMileage + revenueDistance
        powerConsumed = sum(select_depot['power_consumed'])
        
        d_data = {
            "charging_station": depot,
            "dead_mileage": int(round(deadMileage, 3)),
            "revenue_distance": int(round(revenueDistance, 3)),
            "total_distance": int(round(totalDistance, 3)),
            # "power_consumed": round(powerConsumed, 3)
        }
        depot_distances.append(d_data)

    depot_distances_df = pd.DataFrame(depot_distances)
    TdeadMileage = sum(depot_distances_df["dead_mileage"])
    Tdistance = sum(depot_distances_df["total_distance"])

    charging_schedule_df_stat = charging_schedule_df[(charging_schedule_df['start_time'] < 2880) & (charging_schedule_df['end_time'] > 1440)]
    eff_charging_day2 = []
    for i,dp in charging_schedule_df_stat.iterrows():
        if dp.start_time < 1440:
            eff_charging_day2.append(dp.end_time - 1440)
        elif dp.end_time > 2880:
            eff_charging_day2.append(2880-dp.start_time)
        else:
            eff_charging_day2.append(dp.end_time-dp.start_time)
    charging_schedule_df_stat['eff_ch_duration'] = eff_charging_day2

    bus_schedules_data = []
    for depot in schedule_df['depot_id'].unique():
        depot_schedule = schedule_df[schedule_df['depot_id'] == depot]
        depot_entry = {
            "depot_id": depot,
            "bus_schedules": []
        }
        for schedule_id in depot_schedule['schedule_id'].unique():
            charging_schedule = charging_schedule_df_stat[charging_schedule_df_stat["schedule_id"] == schedule_id]
            schedule = depot_schedule[depot_schedule['schedule_id'] == schedule_id]
            bus_charging = []
            bus_trip = []
            for i, row in charging_schedule.iterrows():
                bus_charging.append({"start_time": int(row["start_time"]), 
                                     "end_time": int(row["end_time"]), 
                                     "duration": int((row["charging_duration"])),
                                     "route_num": row["route_number"],
                                     })
            for i, row in schedule.iterrows():
                bus_trip.append({"start_time":int(row["start_time"]), 
                                 "end_time": int(row["end_time"]),
                                 "duration": int((row["travel_time"])),
                                 "route_num": row["route_number"],
                                 })
            bus_entry = { 
                "schedule_id": schedule_id,
                "bus_charging": bus_charging,
                "bus_trip": bus_trip
            }
            depot_entry["bus_schedules"].append(bus_entry)
        bus_schedules_data.append(depot_entry)
    
    charger_system = pd.DataFrame(charger_system)
    Tpower_available = sum(charger_system['charger_capacity'])
    apparent_power = []
    for station in charger_system["location"].unique():
        x = charger_system[charger_system["location"] == station]
        xpower = sum(x['charger_capacity'])
        app_power = int(xpower / 0.9)
        a_data = {
            "charging_station": station,
            "apparent_power": app_power
        }
        apparent_power.append(a_data)
    apparent_power_df = pd.DataFrame(apparent_power)

    station_charger = []
    for station in charger_system["location"].unique():
        select_station = charger_system[charger_system["location"] == station]  
        capacity = select_station['charger_capacity']
        ch_capacity = sum(capacity)/len(capacity)
        ch_count = 0
        for charger_item in select_station['charger_type'].unique():
            for c_type in select_station['charger_type']:
                if c_type == charger_item:
                    ch_count += 1  
        dc_data = {
            "charging_station": station,
            "charger_type": c_type,
            "charger_capacity": int(ch_capacity),
            "total_chargers": ch_count
            }
        station_charger.append(dc_data)
    station_charger_df = pd.DataFrame(station_charger)
    Tchargers = sum(station_charger_df['total_chargers'])
    
    # charger_data = []
    # depots = charging_schedule_df['location'].unique()
    # for depot in depots:
    #     charger_ids = charging_schedule_df[charging_schedule_df['location'] == depot]['charger_id'].unique()
    #     x = charger_system[charger_system["location"] == depot]
    #     capacity = x["charger_capacity"]
    #     for charger_id in charger_ids:
    #         charger_schedule = charging_schedule_df[
    #             (charging_schedule_df['location'] == depot) & (charging_schedule_df['charger_id'] == charger_id)]
    #         timeslot = []
    #         for i, row in charger_schedule.iterrows():
    #             timeslot.append({"start_time": round(row["start_time"], 2), "end_time": round(row["end_time"], 2)})

    #         charger_entry = {
    #             "Charger_ID": charger_id,
    #             "charging_station": depot,
    #             "charging_schedule": timeslot
    #         }
    #         charger_data.append(charger_entry)
    # charger_data_df = pd.DataFrame(charger_data)
    
    charger_schedule_data = []
    stations = charging_schedule_df['location'].unique()

    for station in stations:
        charger_ids = charging_schedule_df[charging_schedule_df['location'] == station]['charger_id_'].unique()
        station_entry = {
            "charging_station": station,
            "total_power_consumption": 0,
            "charging_schedule": [],
        }
        total_power = 0  
        
        for charger_id in charger_ids:
            charger_schedule = charging_schedule_df_stat[
                (charging_schedule_df_stat['location'] == station) & (charging_schedule_df_stat['charger_id_'] == charger_id)]
            timeslot = []
            for i, row in charger_schedule.iterrows():
                power_consumption = row["top_up"]
                timeslot.append({
                    "start_time": int(row["start_time"]),
                    "end_time": int(row["end_time"]),
                    "duration": int(row["charging_duration"]),
                    "route_num": row["route_number"],
                    "power_consump": power_consumption
                })
                total_power += power_consumption 
            
            charger_entry = {
                "Charger_ID": charger_id,
                "charging_schedule": timeslot
            }
            station_entry["charging_schedule"].append(charger_entry)
        
        station_entry["total_power_consumption"] = int(round(total_power,3))  
        charger_schedule_data.append(station_entry)
    charger_schedule_data_df = pd.DataFrame(charger_schedule_data)

    # Tpower_consumed = int(sum(charger_schedule_data_df["total_power_consumption"]) / 3)
    power_consumption_data = []
    for station in charger_schedule_data_df["charging_station"].unique():
        p_data = charger_schedule_data_df[charger_schedule_data_df["charging_station"] == station]
        a_data = {
            "charging_station": station,
            # "power_consumpt": int((p_data['total_power_consumption']) / 2.4)
            "power_consumpt": int(p_data['total_power_consumption'])

        }
        power_consumption_data.append(a_data)
    power_consumption_data_df = pd.DataFrame(power_consumption_data)
    Tpower_consumed = int(sum(power_consumption_data_df["power_consumpt"]))

    # utilization = []
    # for location in charging_schedule_df['location'].unique():
    #     id_data = charging_schedule_df[charging_schedule_df['location'] == location]
    #     # uti = round(sum(id_data['charging_duration']) / (24 * len(charging_schedule_df['charger_id_'].unique())), 2)
    #     uti = (round(sum(id_data['charging_duration']) / (2.4*1440 * len(id_data['charger_id_'].unique())), 2))*100
    #     u_data = {
    #         "charging_station": location,
    #         "utility": int(uti)
    #     }
    #     utilization.append(u_data)
    # utilization_df = pd.DataFrame(utilization)
    # Tcharger_utilization = sum(utilization_df['utility'])/ len(utilization_df['utility'])

    # charger utilization

    charger_utilization = charging_schedule_df_stat.groupby(['location']).agg({'eff_ch_duration':sum})

    utilization = []
    for location in charging_schedule_df_stat['location'].unique():
        id_data = charging_schedule_df_stat[charging_schedule_df_stat['location'] == location]
        
        total_duration = sum(id_data['eff_ch_duration'])
        uti = (round(total_duration / (1440 * len(id_data['charger_id_'].unique())), 2)) * 100
        
        u_data = {
            "charging_station": location,
            "utility": int(uti)
        }
        utilization.append(u_data)

    utilization_df = pd.DataFrame(utilization)
    Tcharger_utilization = sum(utilization_df['utility'])/ len(utilization_df['utility'])


    # charging_schedule_df.to_excel('power_demand_data.xlsx', index=False)
    # charging_schedule_df.to_csv('power_demand_data.csv', index=False)

    power_demand_data = []
    stations = charging_schedule_df['location'].unique()
    for station in stations:
        charger_schedule = charging_schedule_df_stat[charging_schedule_df_stat['location'] == station]
        timeslot_data = []
        for i, row in charger_schedule.iterrows():
            timeslot_data.append({
                "time": int(row["start_time"]),
                "power_change": int(row["top_up"]),  # Power increase at start time
                "type": "start"
            })
            timeslot_data.append({
                "time": int(row["end_time"]),
                "power_change": -int(row["top_up"]),  # Power decrease at end time
                "type": "end"
            })
        
        timeslot_data.sort(key=lambda x: x["time"])
        power_consumption_schedule = []
        current_power = 0
        last_time = timeslot_data[0]["time"]
        
        for slot in timeslot_data:
            if slot["time"] != last_time:
                power_consumption_schedule.append({
                    "start_time": last_time,
                    "end_time": slot["time"],
                    "power_consump": current_power
                })
                last_time = slot["time"]
            current_power += slot["power_change"]
        
        power_consumption_schedule.append({
            "start_time": last_time,
            "end_time": slot["time"],
            "power_consump": current_power
        })
        station_entry = {
            "charging_station": station,
            "charging_schedule": power_consumption_schedule
        }
        power_demand_data.append(station_entry)
        
    depot_map_data = []
    terminal_map_data = []
    # Merging dataframes by charging_station
    merged_df1 = station_charger_df.merge(utilization_df, on='charging_station')
    merged_df2 = merged_df1.merge(apparent_power_df, on='charging_station')
    merged_df3 = merged_df2.merge(power_consumption_data_df[['charging_station','power_consumpt']], on='charging_station')
    depotmerged_df = merged_df3.merge(depot_distances_df, on='charging_station')

    depot_df_renamed = depot_df.rename(columns={
        'depot_name': 'charging_station'
    })
    # Merge with depot_df to include latitude and longitude
    merged_df_with_depots = depotmerged_df.merge(depot_df_renamed[['charging_station', 'latitude', 'longitude']], on='charging_station')
    depot_dict = merged_df_with_depots.to_dict(orient='records')
    depot_map_data.extend(depot_dict)

    terminal_df_renamed = terminal_df.rename(columns={
        'terminal_name': 'charging_station'
    })
    # Merge the terminal_df with the merged_df_with_depots
    merged_df_with_terminals = merged_df3.merge(terminal_df_renamed[['charging_station', 'latitude', 'longitude']], on='charging_station')
    terminal_dict = merged_df_with_terminals.to_dict(orient='records')
    terminal_map_data.extend(terminal_dict)

    analytics_response_data = {
        # "Bus_schedule": bus_schedules,
        # "Charger_schedule": charger_data,
        "TChargers": int(Tchargers),
        "TPower_consumed": int(Tpower_consumed),  
        "TApparent_power": int(Tpower_available), 
        "TDead_mileage": int(TdeadMileage),
        "TSystem_Vehicle_Utilization": int(Tdistance),
        "TCharger_Utilization": int(Tcharger_utilization),
        "Depot_charger": station_charger,
        "Charger_utilization": utilization,
        "Apparent_power": apparent_power,
        "Power_consumption_data": power_consumption_data,
        "Depot_distance_power": depot_distances,
        "Final_depot_MAP": depot_map_data,
        "Final_terminal_MAP": terminal_map_data,
        "Bus_schedules": bus_schedules_data,
        "Charger_schedules": charger_schedule_data,
        "power_demand": power_demand_data
    }

    # # Save the result as a JSON file
    # with open('result.json', 'w') as json_file:
    #     json.dump(analytics_response_data, json_file, indent=4) 

    return analytics_response_data
