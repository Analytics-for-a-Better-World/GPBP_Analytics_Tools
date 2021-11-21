#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import plotly.express as px
import pandas as pd
import folium


# In[ ]:


def ParetoCurve(df_combined_output, current_hospitals):
    fig = px.line(df_combined_output.sort_values(by=['km', 'number_of_hospitals']),
                  x='number_of_hospitals', y='%', color='km',
                  labels={
                      "number_of_hospitals": "Number of Health Facilities",
                      "%": "Percentage of households with access",
                      "km": "Distance (KM)"
                  })
    fig.update_xaxes(range=[0, 960])
    fig.update_yaxes(range=[0, 110])

    fig.add_annotation(x=165, y=105,
                       text="Current health facilities:" + str(len(current_hospitals)),
                       showarrow=False,
                       arrowhead=1)

    fig.add_shape(type="line",
                  x0=len(current_hospitals), y0=0, x1=len(current_hospitals), y1=120,
                  line=dict(color="RoyalBlue", width=1)
                  )

    return (fig)


# In[ ]:


def CreateMap(dist_threshold, hosp_added, population, current_hospitals, new_hospitals, df_combined, df_combined_output,
              filename):
    # get pop coordinates
    pop_id = pd.DataFrame(df_combined.reset_index()['Pop_ID'])
    pop_coordinates = pd.merge(pop_id, population, right_on='ID', left_on='Pop_ID')

    # get (potential) hospital coordinates
    new_hospitals_sel = new_hospitals[['Cluster_ID', 'Longitude', 'Latitude', 'hosp_dist_road_estrada']]
    new_hospitals_sel.columns = ['Hosp_ID', 'Longitude', 'Latitude', 'hosp_dist_road_estrada']
    tot_hosp_cordinates = pd.concat([current_hospitals, new_hospitals_sel])
    df_cordinates_hosp = tot_hosp_cordinates[['Hosp_ID', 'Longitude', 'Latitude']]

    # pick wanted value and select needed data
    opt_sel_df = df_combined_output[
        (df_combined_output['km'] == dist_threshold) & (df_combined_output['number_of_new_hospitals'] == hosp_added)]

    hosp_present = opt_sel_df['array_hosp'].values[0]
    df_cordinates_hosp = df_cordinates_hosp.sort_values(by='Hosp_ID')
    df_cordinates_hosp['present_index'] = hosp_present
    only_present_health_fac = df_cordinates_hosp[df_cordinates_hosp.present_index == 1]

    # Create subset of served population
    population = population.sort_values(by='ID')
    served1_population = population[['ID', 'xcoord', 'ycoord', 'household_count']]
    x = opt_sel_df['array_hh'].values[0]
    x1 = x[:len(population)]
    served1_population['served'] = x1

    served_population = served1_population[served1_population['served'] == 1]
    served_population['x_roun'] = served_population['xcoord'].round(2)
    served_population['y_roun'] = served_population['ycoord'].round(2)
    served_population['household_count'] = served_population['household_count'].round()

    # Create points on the map for served population
    served = served_population.groupby(['x_roun', 'y_roun', 'served'])['household_count'].sum().reset_index()
    q1 = served['household_count'].describe()['25%']
    q2 = served['household_count'].describe()['50%']
    q3 = served['household_count'].describe()['75%']

    def get_color(x, q1=q1, q2=q2, q3=q3):
        if (x <= q1):
            return 0.1
        else:
            if (x <= q2):
                return 0.3
            else:
                if (x <= q3):
                    return 0.5
                else:
                    return 1

    served['opacity'] = served['household_count'].apply(get_color, q1=q1, q2=q2, q3=q3)

    # Same for unserved
    unserved_population = served1_population[served1_population['served'] == 0]

    unserved_population['x_roun'] = unserved_population['xcoord'].round(2)
    unserved_population['y_roun'] = unserved_population['ycoord'].round(2)
    unserved_population['household_count'] = unserved_population['household_count'].round()

    unserved = unserved_population.groupby(['x_roun', 'y_roun', 'served'])['household_count'].sum().reset_index()

    q1 = unserved['household_count'].describe()['25%']
    q2 = unserved['household_count'].describe()['50%']
    q3 = unserved['household_count'].describe()['75%']

    unserved['opacity'] = unserved['household_count'].apply(get_color, q1=q1, q2=q2, q3=q3)

    # Create the map
    map_osm = folium.Map(location=[16, 106], zoom_start=5, prefer_canvas=True)

    for x in only_present_health_fac.values:
        hosp_name = x[0]
        lon = x[1]
        lat = x[2]

        if hosp_name in current_hospitals['Hosp_ID'].unique():
            color_marker = 'green'
        else:
            color_marker = 'blue'
        folium.Marker([lat, lon], icon=folium.Icon(color=color_marker, icon='hospitals', prefix='fa', size=1)).add_to(
            map_osm)

    for each_val in served.values:
        lon = each_val[0]
        lat = each_val[1]

        hh_count = each_val[3]
        color_circle = 'green'
        opacity = each_val[4]

        folium.Circle(location=[lat, lon], radius=10, color=color_circle, fill_color=color_circle,
                      opacity=opacity).add_to(map_osm)

    for each_val in unserved.values:
        lon = each_val[0]
        lat = each_val[1]

        hh_count = each_val[3]
        color_circle = 'red'
        opacity = each_val[4]

        folium.Circle(location=[lat, lon], radius=10, color=color_circle, fill_color=color_circle,
                      opacity=opacity).add_to(map_osm)

    # Export map
    map_osm.save(filename + '.html')
