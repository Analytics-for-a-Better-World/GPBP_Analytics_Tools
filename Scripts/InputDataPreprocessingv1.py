#!/usr/bin/env python
# coding: utf-8

def haversine_vectorize(lon1, lat1, lon2, lat2):
    import numpy as np

    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    newlon = lon2 - lon1
    newlat = lat2 - lat1
    haver_formula = np.sin(newlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(newlon / 2.0) ** 2
    dist = 2 * np.arcsin(np.sqrt(haver_formula))
    km = 6367 * dist  # 6367 for distance in KM for miles use 3958
    return round(km, 2)


def CurrentHospitals(current_hospitals, network, nodes):
    import pandas as pd

    current_hospitals.columns = ['Hosp_ID', 'Longitude', 'Latitude', 'name']
    current_hospitals_ID = current_hospitals['Hosp_ID'].unique()

    current_hospitals['nearest_node'] = network.get_node_ids(current_hospitals['Longitude'],
                                                             current_hospitals['Latitude'], mapping_distance=None)
    current_hospitals = pd.merge(current_hospitals, nodes, right_on='nodeID', left_on='nearest_node')
    current_hospitals['hosp_dist_road_estrada'] = haversine_vectorize(current_hospitals['Longitude'],
                                                                      current_hospitals['Latitude'],
                                                                      current_hospitals['lon'],
                                                                      current_hospitals['lat'])

    return (current_hospitals_ID, current_hospitals)


def NewHospitalsCSV(current_hospitals, new_hospitals, network, nodes):
    from shapely import geometry, ops
    import numpy as np
    import pandas as pd

    new_hospitals = new_hospitals[['xcoord', 'ycoord']]
    new_hospitals.columns = ['Longitude', 'Latitude']
    new_hospitals['Cluster_ID'] = np.arange(len(new_hospitals)) + len(current_hospitals)
    new_hospitals_ID = new_hospitals['Cluster_ID'].unique()

    new_hospitals['nearest_node'] = network.get_node_ids(new_hospitals['Longitude'], new_hospitals['Latitude'],
                                                         mapping_distance=None)
    new_hospitals = pd.merge(new_hospitals, nodes, right_on='nodeID', left_on='nearest_node')
    new_hospitals['hosp_dist_road_estrada'] = haversine_vectorize(new_hospitals['Longitude'], new_hospitals['Latitude'],
                                                                  new_hospitals['lon'], new_hospitals['lat'])
    return (new_hospitals_ID, new_hospitals)


def NewHospitals(current_hospitals, new_hospitals, network, nodes):
    from shapely import geometry, ops
    import numpy as np
    import pandas as pd

    new_hospitals['Longitude'] = new_hospitals.geometry.x
    new_hospitals['Latitude'] = new_hospitals.geometry.y
    new_hospitals = new_hospitals[['full_id', 'Longitude', 'Latitude']]
    new_hospitals.columns = ['Cluster_ID', 'Longitude', 'Latitude']
    new_hospitals['Name'] = new_hospitals['Cluster_ID'].apply(lambda x: 'potential_' + str(x))
    new_hospitals['Cluster_ID'] = np.arange(len(new_hospitals)) + len(current_hospitals)
    new_hospitals = new_hospitals[['Name', 'Cluster_ID', 'Longitude', 'Latitude']].drop_duplicates()
    new_hospitals_ID = new_hospitals['Cluster_ID'].unique()

    new_hospitals['nearest_node'] = network.get_node_ids(new_hospitals['Longitude'], new_hospitals['Latitude'],
                                                         mapping_distance=None)
    new_hospitals = pd.merge(new_hospitals, nodes, right_on='nodeID', left_on='nearest_node')
    new_hospitals['hosp_dist_road_estrada'] = haversine_vectorize(new_hospitals['Longitude'], new_hospitals['Latitude'],
                                                                  new_hospitals['lon'], new_hospitals['lat'])
    return (new_hospitals_ID, new_hospitals)


def NewHospitalsGrid(current_hospitals, new_hospitals, network, nodes):
    from shapely import geometry, ops
    import numpy as np
    import pandas as pd

    new_hospitals['Longitude'] = new_hospitals.geometry.x
    new_hospitals['Latitude'] = new_hospitals.geometry.y
    new_hospitals = new_hospitals[['id', 'Longitude', 'Latitude']]

    new_hospitals.columns = ['Cluster_ID', 'Longitude', 'Latitude']
    new_hospitals['Name'] = new_hospitals['Cluster_ID'].apply(lambda x: 'potential_' + str(x))
    new_hospitals['Cluster_ID'] = np.arange(len(new_hospitals)) + len(current_hospitals)
    new_hospitals = new_hospitals[['Name', 'Cluster_ID', 'Longitude', 'Latitude']].drop_duplicates()
    new_hospitals_ID = new_hospitals['Cluster_ID'].unique()

    new_hospitals['nearest_node'] = network.get_node_ids(new_hospitals['Longitude'], new_hospitals['Latitude'],
                                                         mapping_distance=None)
    new_hospitals = pd.merge(new_hospitals, nodes, right_on='nodeID', left_on='nearest_node')
    new_hospitals['hosp_dist_road_estrada'] = haversine_vectorize(new_hospitals['Longitude'], new_hospitals['Latitude'],
                                                                  new_hospitals['lon'], new_hospitals['lat'])
    return (new_hospitals_ID, new_hospitals)


def Population(digits_rounding, population, network, nodes):
    import pandas as pd
    population.columns = ['ID', 'xcoord', 'ycoord']
    population['xcoord'] = population['xcoord'].round(digits_rounding)
    population['ycoord'] = population['ycoord'].round(digits_rounding)

    household_count = population.groupby(['xcoord', 'ycoord'])['ID'].nunique().reset_index()
    household_count.columns = ['xcoord', 'ycoord', 'household_count']

    population = population[['xcoord', 'ycoord']].drop_duplicates().reset_index().reset_index()
    del population['index']
    population.columns = ['ID', 'xcoord', 'ycoord']

    population['nearest_node'] = network.get_node_ids(population['xcoord'], population['ycoord'], mapping_distance=None)
    population = pd.merge(population, nodes, right_on='nodeID', left_on='nearest_node')
    population['pop_dist_road_estrada'] = haversine_vectorize(population['xcoord'], population['ycoord'],
                                                              population['lon'], population['lat'])

    population = pd.merge(population, household_count, on=['xcoord', 'ycoord'])

    array_household = population.sort_values(by='ID')['household_count'].values

    return array_household, population


def PopulationFB(digits_rounding, population, network, nodes):
    import pandas as pd
    population.columns = ['ID', 'xcoord', 'ycoord', 'household_count']
    population['xcoord'] = population['xcoord'].round(digits_rounding)
    population['ycoord'] = population['ycoord'].round(digits_rounding)

    household_count = population.groupby(['xcoord', 'ycoord'])['household_count'].sum().round().reset_index()
    household_count.columns = ['xcoord', 'ycoord', 'household_count']

    population = population[['xcoord', 'ycoord']].drop_duplicates().reset_index().reset_index()
    del population['index']
    population.columns = ['ID', 'xcoord', 'ycoord']

    population['nearest_node'] = network.get_node_ids(population['xcoord'], population['ycoord'], mapping_distance=None)
    population = pd.merge(population, nodes, right_on='nodeID', left_on='nearest_node')
    population['pop_dist_road_estrada'] = haversine_vectorize(population['xcoord'], population['ycoord'],
                                                              population['lon'], population['lat'])

    population = pd.merge(population, household_count, on=['xcoord', 'ycoord'])

    array_household = population.sort_values(by='ID')['household_count'].values

    return array_household, population
