import sys

import folium
import webbrowser
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def vizualize_depot_terminal_in_map(depot_df, terminal_df):
    #visualize locations
    first_point = [list(depot_df['Latitude'])[0], list(depot_df['Longitude'])[0]]
    project_map = folium.Map(location = first_point, zoom_start = 11)
    terminal_df.apply(lambda row: folium.Marker([row['Latitude'], row['Longitude']], popup=f"Name: {row['Terminal Name']}; type:Terminal", icon=folium.Icon(color="black")).add_to(project_map), axis=1)
    depot_df.apply(lambda row: folium.Marker([row['Latitude'], row['Longitude']], popup=f"Name: {row['Depot Name']}; type:Depot").add_to(project_map), axis=1)
    project_map.save (r'c:\temp\example.html')
    webbrowser.open(r'c:\temp\example.html')


def vizualize_schedule_in_bar(data, unique_x, start_time, event_duration, event_type, day_to_show, yaxis_title):

    elements_to_color = list(data[event_type].unique())
    colors = ['#011f4b', '#005b96', '#317256', '#52bf90', '#419873', '#b3cde0']
    # colors = ['#A9A9A9', '#DAF7A6', '#FFC300', '#FF5733','#C70039','#900C3F', '#7B68EE', '#FFE4B5', '#FF6347', '#DB7093', '#DC143C', '#FFA07A', '#6495ED'
    #           '#40E0D0', '#008080', '#20B2AA', '#808000', '#98FB98', '#800000', '#A0522D', '#BC8F8F', '#DEB887', '#FFEBCD', '#FFF8DC', '#191970', '#000000', '#2F4F4F', '#708090', '#696969']

    elements_color_dict = {i:j for i,j in zip(elements_to_color, colors)}

    #visualize schedule
    fig, ax = plt.subplots(figsize=(12,len(data[unique_x].unique())/2))
    i = 0
    charger_ids_to_plot = list(data[unique_x].unique())
    charger_ids_to_plot.sort()

    legend_patches = []
    [legend_patches.append(mpatches.Patch(color=value, label=key)) for key, value in elements_color_dict.items()]

    for sch in charger_ids_to_plot:
        x = data[data[unique_x] == sch]
        for key,value in elements_color_dict.items():
            event_data = [(i,j) for i,j,k in zip(x[start_time], x[event_duration],x[event_type]) if k == key]
            ax.broken_barh(event_data, (i, 0.5), facecolors= value)

        i = i+1

    if max(data[start_time]) <= 1440:
        hours = 24
        x_labels = list(range(24))
    else:
        hours = 48
        x_labels = list(range(24)) + list(range(24))




    ax.grid(True)
    ax.set_yticks(list(range(len(data[unique_x].unique()))))
    ax.set_yticklabels(charger_ids_to_plot)
    ax.set_xticks(list(map(lambda x: x * 60, range(hours))))
    ax.set_xticklabels(x_labels)
    ax.set_xlim(1440*(day_to_show-1), 1440*(day_to_show))
    # Set the x-axis title
    ax.set_xlabel(f'Hour of the day - Day {day_to_show}', fontsize=11)
    # Set the y-axis title
    ax.set_ylabel(yaxis_title, fontsize=11)  # Replace 'Y Axis Title' with your desired title

    # Add legend
    ax.legend(handles=legend_patches, loc='upper left', bbox_to_anchor=(1, 1))
    plt.show()