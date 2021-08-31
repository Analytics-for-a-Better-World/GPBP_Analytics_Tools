#!/usr/bin/env python
# coding: utf-8

def get_corrected_distance(x):
    if(x['euclidean_distance'])<=1:
        return x['euclidean_distance']
    else:
        if (x['pop_dist_road_estrada']>=x['euclidean_distance']):
            return x['euclidean_distance']
        else:
            return x['total_network_distance']
    

def haversine_vectorize(lon1, lat1, lon2, lat2):
    import numpy as np
    
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    newlon = lon2 - lon1
    newlat = lat2 - lat1
    haver_formula = np.sin(newlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(newlon/2.0)**2
    dist = 2 * np.arcsin(np.sqrt(haver_formula ))
    km = 6367 * dist #6367 for distance in KM for miles use 3958
    return round(km,2)


def DistanceCalculation(network, hospitals, population, pop_subset, S1):
    
    import pandas as pd
    import swifter
    
    df_matrix = pd.DataFrame()
    for each_hospital in hospitals[['nearest_node','Longitude','Latitude']].values:
        hosp_node = each_hospital[0]
        hosp_lon = each_hospital[1]
        hosp_lat = each_hospital[2]
    
        pop_subset['hosp_node'] = hosp_node
        pop_subset['hosp_lon'] = hosp_lon
        pop_subset['hosp_lat'] = hosp_lat
    
        pop_subset['euclidean_distance'] = haversine_vectorize(pop_subset['xcoord'],pop_subset['ycoord'],pop_subset['hosp_lon'],pop_subset['hosp_lat'])
        nearest_nodes = pop_subset[pop_subset['euclidean_distance']<=S1]['nearest_node'].unique()
    
        matrix_selected = pd.DataFrame([(a,b) for a in [int(hosp_node)] for b in nearest_nodes])
        df_matrix = df_matrix.append(matrix_selected)
    
    df_matrix = df_matrix.drop_duplicates()
    df_matrix.columns = ['nearest_node_hosp','nearest_node_pop']
    df_matrix['shortest_path_length'] = network.shortest_path_lengths(df_matrix['nearest_node_pop'],df_matrix['nearest_node_hosp'])
    df_matrix = pd.merge(df_matrix, population[['ID','nearest_node','pop_dist_road_estrada','household_count','xcoord','ycoord']],right_on='nearest_node',left_on='nearest_node_pop')
    df_matrix = pd.merge(df_matrix, hospitals,right_on='nearest_node',left_on='nearest_node_hosp')

    df_matrix['euclidean_distance'] = haversine_vectorize(df_matrix['xcoord'],df_matrix['ycoord'],df_matrix['Longitude'],df_matrix['Latitude'])
    df_matrix['total_network_distance'] = df_matrix['pop_dist_road_estrada']+df_matrix['hosp_dist_road_estrada']+df_matrix['shortest_path_length']
    
    df_matrix['distance_corrected'] = df_matrix[['pop_dist_road_estrada','euclidean_distance','total_network_distance']].swifter.apply(get_corrected_distance,axis=1)
    
    return df_matrix
    

