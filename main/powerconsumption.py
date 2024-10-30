import sys
import pandas as pd
import time
import numpy as np

def estimate_power_consumption_per_tonnekm(model_name, power_consumption_per_km, passenger_load, bus_model_data):
    curb_weight = bus_model_data.at[model_name, 'curb_weight']
    gross_vehicle_weight = bus_model_data.at[model_name, 'gross_vehicle_weight']
    bus_weight = (curb_weight + ((gross_vehicle_weight - curb_weight) * passenger_load))/1000
    return round(power_consumption_per_km/bus_weight, 3)

def get_lower_bound_and_upper_bound(values):
    # IQR
    Q1 = np.percentile(values, 25, method='midpoint')
    Q3 = np.percentile(values, 75, method='midpoint')
    IQR = Q3 - Q1
    upper_bound_value = Q3 + 1.5 * IQR
    lower_bound_value = Q1 - 1.5 * IQR
    return lower_bound_value, upper_bound_value

def preprocess_data(historical_data, bus_model_data, base_percentage):
    # Ensure base_percentage is a float
    base_percentage = float(base_percentage)
    
    # Convert columns to appropriate numeric types
    historical_data['start_min'] = pd.to_numeric(historical_data['start_min'], errors='coerce')
    historical_data['end_min'] = pd.to_numeric(historical_data['end_min'], errors='coerce')
    historical_data['start_odo'] = pd.to_numeric(historical_data['start_odo'], errors='coerce')
    historical_data['end_odo'] = pd.to_numeric(historical_data['end_odo'], errors='coerce')
    historical_data['start_soc'] = pd.to_numeric(historical_data['start_soc'], errors='coerce')
    historical_data['end_soc'] = pd.to_numeric(historical_data['end_soc'], errors='coerce')
    historical_data['passenger_load'] = pd.to_numeric(historical_data['passenger_load'], errors='coerce')
    historical_data['short_name'] = historical_data['short_name'].astype(str)  # Ensure short_name is string

    bus_model_data['curb_weight'] = pd.to_numeric(bus_model_data['curb_weight'], errors='coerce')
    bus_model_data['gross_vehicle_weight'] = pd.to_numeric(bus_model_data['gross_vehicle_weight'], errors='coerce')
    bus_model_data['short_name'] = bus_model_data['short_name'].astype(str)  # Ensure short_name is string

    return historical_data, bus_model_data, base_percentage

def get_pc_profile(historical_data, bus_model_data, base_percentage, remove_outliers=1):
    # Preprocess the data
    historical_data, bus_model_data, base_percentage = preprocess_data(historical_data, bus_model_data, base_percentage)

    bus_model_data.set_index('short_name', inplace=True)  # setting index to unique key for bus model data table
    historical_data = historical_data.dropna()  # removing rows with na

    # calculate absolute power consumption, distance, pc per km, pc per tonnekm
    historical_data['PC'] = historical_data['start_soc'] - historical_data['end_soc']
    historical_data['distance'] = historical_data['end_odo'] - historical_data['start_odo']
    historical_data['PC_per_km'] = (historical_data.PC / historical_data.distance).round(2)
    historical_data['PC_per_tonnekm'] = [estimate_power_consumption_per_tonnekm(i, j, k, bus_model_data) for i, j, k in
                                         zip(historical_data['short_name'], historical_data['PC_per_km'],
                                             historical_data['passenger_load'])]
    # Convert PC_per_tonnekm to numeric
    historical_data['PC_per_tonnekm'] = pd.to_numeric(historical_data['PC_per_tonnekm'], errors='coerce')

    # get unique bus models in the historical data
    route_models_unique = historical_data[['route_no', 'short_name']].drop_duplicates(keep='first').values.tolist()

    # power consumption associated to a bus model and a specific route
    PC_per_tonnekm_route_model_dict = {}
    for route_model in route_models_unique:
        # filter data for each bus model in each route
        data = historical_data[(historical_data['short_name'] == route_model[1]) & (historical_data['route_no'] == route_model[0])]

        # remove outliers
        if remove_outliers == 1:
            lower_bound_value, upper_bound_value = get_lower_bound_and_upper_bound(data['PC_per_tonnekm'])
            data = data[(data['PC_per_tonnekm'] <= upper_bound_value) & (data['PC_per_tonnekm'] >= lower_bound_value)]

        # set base value
        p70 = data['PC_per_tonnekm'].quantile(base_percentage)  # user input

        route_model_ = f"{route_model[0]}|{route_model[1]}"  # dictionary key
        PC_per_tonnekm_route_model_dict[route_model_] = [p70 for i in range(0, 1440)]
        # estimate dictionary key value -power consumption per tonnekm
        for i, dp in data.iterrows():
            for minute in range(int(dp.start_min), int(dp.end_min)):
                if dp['PC_per_km'] > p70:
                    PC_per_tonnekm_route_model_dict[route_model_][minute] = dp['PC_per_km']

    model_unique = historical_data['short_name'].unique().tolist()

    # for a bus model not associated to a route
    PC_per_tonnekm_model_dict = {}
    for bus_model in model_unique:
        # filter data
        data = historical_data[historical_data['short_name'] == bus_model]

        # remove outliers
        if remove_outliers == 1:
            lower_bound_value, upper_bound_value = get_lower_bound_and_upper_bound(data['PC_per_tonnekm'])
            data = data[(data['PC_per_tonnekm'] <= upper_bound_value) & (data['PC_per_tonnekm'] >= lower_bound_value)]

        p70 = data['PC_per_tonnekm'].quantile(base_percentage)  # user input
        print('powerconsumption p80', bus_model, p70)
        PC_per_tonnekm_model_dict[bus_model] = [round(p70, 3) for i in range(0, 1440)]
        for i, dp in data.iterrows():
            for minute in range(int(dp.start_min), int(dp.end_min)):
                if dp['PC_per_tonnekm'] > p70:
                    PC_per_tonnekm_model_dict[bus_model][minute] = round(dp['PC_per_tonnekm'], 3)
    return PC_per_tonnekm_route_model_dict, PC_per_tonnekm_model_dict
