# import library
from pulp import LpMinimize, LpProblem, lpSum, LpVariable  # pre-requsite
from decimal import Decimal


def generate_combinations(dictionary):
    keys = list(dictionary.keys())
    result = [[]]
    for key in keys:
        new_result = []
        for value in dictionary[key]:
            for item in result:
                new_result.append(item + [value])
        result = new_result
    return result

def check_feasibility(data):
    result = {}
    order = []
    constraints = {}
    assignment_preference_keys = data["assignment_preferences"].keys()
    for attribute_name in assignment_preference_keys:
        preferences_checked = data["assignment_preferences"][attribute_name]
        if len(preferences_checked) > 0:
            order = order+[attribute_name]
            constraints[attribute_name] = data["assignment_preferences"][attribute_name] + [f'Unchecked_options']
    combinations_to_evaluate = generate_combinations(constraints)
    result['column_names'] = ['S'] + order + ['depot_capacity', 'number_of_buses']
    count = 0
    for combination in combinations_to_evaluate:
        count += 1
        depots_selected = list(data["depot_data"].keys())
        schedules_selected = list(data["schedule_data"].keys())
        for attribute_name, attribute_value in zip(order, combination):
            if attribute_value != 'Unchecked_options':
                depots_selected = [depot for depot in depots_selected if data['depot_data'][depot][attribute_name] == attribute_value]
                # print('identifier', data['schedule_data']['US1'][0])
                schedules_selected = [schedule for schedule in schedules_selected if data['schedule_data'][schedule]["start_shuttle"][attribute_name] == attribute_value]
            else:
                attribute_values_to_exclude = constraints[attribute_name][:len(constraints[attribute_name])-1]
                depots_selected = [depot for depot in depots_selected if data['depot_data'][depot][attribute_name] not in attribute_values_to_exclude]
                schedules_selected = [schedule for schedule in schedules_selected if data['schedule_data'][schedule]["start_shuttle"][attribute_name] not in attribute_values_to_exclude]
        depot_capacity_for_combination = sum([int(data['depot_data'][depot]['capacity']) for depot in depots_selected])
        number_of_schedules_for_combination = len(schedules_selected)
        result[count] = {}
        for name, value in zip(order, combination):
            result[count][name] = value
        result[count]['depot_capacity'] = depot_capacity_for_combination
        result[count]['number_of_buses'] = number_of_schedules_for_combination
        result[count]['Feasible'] = depot_capacity_for_combination>=number_of_schedules_for_combination
    return result

def process_feasibility_result(result):
    column_names = result["column_names"]

    column_names.append("feasible")
    column_names.remove("S")
    column_names.append("s_no")

    processed_data = {
        "column_names": column_names,
        "data": [],
    }

    for key in result.keys():
        if key == "column_names":
            continue

        entry = {}
        entry["s_no"] = key
        entry["feasible"] = result[key]["Feasible"]
        for column_name in column_names:
            if column_name == "s_no" or column_name == "feasible":
                continue
            entry[column_name] = result[key][column_name]
        processed_data["data"].append(entry)

    return processed_data

def map_schedule_data(data):
    # Mapping original schedule data keys to new keys
    new_keys = ["SS" + str(num) for num in range(len(data["schedule_data"]))]

    # create a mapping dictionary for original keys to the new keys
    map_keys = {key: new_keys[i] for i, key in enumerate(data["schedule_data"].keys())}

    # create a new dictionary with the new set of dictionary keys with empty values
    schedule_data_mapped = {val: "" for val in new_keys}

    # assign the values of original schedule_data to this new dict with empty values
    for key2 in data["schedule_data"].keys():
        schedule_data_mapped[map_keys[key2]] = data["schedule_data"][key2]

    # Remap the schedule data back to original keys
    # create a remapping dictionary for new keys back to original keys
    remap_keys = {v: k for k, v in map_keys.items()}

    # Remap the schedule data
    remapped_schedule_data = {}
    for key in remap_keys:
        if key in data["schedule_data"]:
            remapped_schedule_data[remap_keys[key]] = data["schedule_data"][key]

    # Modify the data with remapped schedule data
    data["schedule_data"] = remapped_schedule_data

    return schedule_data_mapped, remap_keys

# the function with data as argument
def optimize_deadkm(data):
   
    # Mapping schedule data and getting remap keys
    schedule_data_mapped, remap_keys = map_schedule_data(data)

    # Run optimization with mapped data
    # 1. exclusions
    # for each exclusion
    for exclusion in data["exclusions"].keys():
        exclusion_values = data["exclusions"][exclusion]
        if exclusion != "depot_id":

            # remove unrequired depot data
            for depot in list(data["depot_data"].keys()):
                if data["depot_data"][depot][exclusion] in exclusion_values:
                    data["depot_data"].pop(depot)
                    # print("poping depot ", depot)
        else:

            # if depot id remove depot depot data
            data["depot_data"] = {
                i: data["depot_data"][i]
                for i in data["depot_data"].keys()
                if i not in exclusion_values
            }

        # remove unrequired schedule data
        for schedule in list(schedule_data_mapped.keys()):
            if (
                schedule_data_mapped[schedule]["start_shuttle"][exclusion]
                in exclusion_values
            ):
                schedule_data_mapped.pop(schedule)
                # print("poping schedule ", schedule)

    # 2. create decision variables and dead km
    variables = {}
    for schedule in schedule_data_mapped:
        for depot in data["depot_data"]:
            start_terminal = schedule_data_mapped[schedule]["start_shuttle"][
                "end_terminal"
            ]
            end_terminal = schedule_data_mapped[schedule]["end_shuttle"][
                "start_terminal"
            ]

            # if start_terminal is None or end_terminal is None:
            #     print("\nERROR: start_terminal or end_terminal is None\n")

            # depot_to_start_terminal_dist = data["depot_terminal_matrix"][depot][
            #     start_terminal
            # ]["distance"]

            # end_terminal_to_depot_dist = data["terminal_depot_matrix"][end_terminal][
            #     depot
            # ]["distance"]

            # if (
            #     depot_to_start_terminal_dist is None
            #     or end_terminal_to_depot_dist is None
            # ):
            #     print(
            #         "\nERROR: depot to terminal or terminal to depot distance is None\n"
            #     )

            # # dead km of all possible combinations
            # variables[f"{schedule}|{depot}"] = (
            #     depot_to_start_terminal_dist + end_terminal_to_depot_dist
            # )

            # dead km of all possible combinations
            if schedule_data_mapped[schedule]['start_shuttle']['start_terminal'] == depot:
                allocation_cost = 0
            else:
                allocation_cost = 0.0001

            # variables[f'{schedule}|{depot}'] = data['depot_terminal_matrix'][depot][start_terminal]['distance'] + data['terminal_depot_matrix'][end_terminal][depot]['distance'] + allocation_cost
            variables[f'{schedule}|{depot}'] = (data['depot_terminal_matrix'][depot][start_terminal]['distance'] + data['terminal_depot_matrix'][end_terminal][depot]['distance'] + Decimal(allocation_cost))

    act_var = [
        LpVariable(i, lowBound=0, upBound=1, cat="Integer") for i in variables.keys()
    ]

    # linear function model
    model = LpProblem(name="Depot Allocation", sense=LpMinimize)  # syntax

    # dead km list
    dead_km_list = [variables[i] for i in variables.keys()]

    # 3. objective function
    objective = lpSum([act_var[i] * dead_km_list[i] for i in range(len(act_var))])
    model.setObjective(objective)  # syntax

    # 4. constraints
    # 1 - every schedule must be allocated once
    for schedule in list(schedule_data_mapped):
        model += lpSum(
            [i for i in act_var if schedule == str(i).split("|")[0]]
        ) == 1, "schedule_constraint-" + str(schedule)

    # 2 - depot constraint
    for depot in list(data["depot_data"]):
        capacity = data["depot_data"][depot]["capacity"]
        act_vars = [j for j in act_var if depot == str(j).split("|")[1]]
        model += lpSum(act_vars) <= int(capacity), "depot_constraint-" + str(depot)

    # 3 - other user constraint
    for preference in data["assignment_preferences"]:
        preference_values = data["assignment_preferences"][preference]
        depots = [
            depot
            for depot in list(data["depot_data"].keys())
            if data["depot_data"][depot][preference] in preference_values
        ]
        schedules = [
            schedule
            for schedule in list(schedule_data_mapped.keys())
            if schedule_data_mapped[schedule]["start_shuttle"][preference]
            in preference_values
        ]
        act_vars = [
            j
            for j in act_var
            if (str(j).split("|")[1] in (depots))
            and (str(j).split("|")[0] in (schedules))
        ]  # act_var_replace-------
        number_of_schedules = len(list(set([str(i).split("|")[0] for i in act_vars])))
        model += lpSum(
            act_vars
        ) == number_of_schedules, "user_defined_constraint-" + str(preference)
    model.solve()

    feasibility_check = check_feasibility(data)
    feasibility_status = model.status
    print(feasibility_check)
    print(feasibility_status)
    processed_feasibility_check = process_feasibility_result(feasibility_check)

    # Re-map the schedule IDs and return
    result_array = [[remap_keys[schedule.split("|")[0]], schedule.split("|")[1]] for schedule in variables.keys() if act_var[list(variables.keys()).index(schedule)].varValue == 1]

    return result_array, feasibility_status, processed_feasibility_check