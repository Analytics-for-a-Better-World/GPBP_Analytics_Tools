import geopandas as gpd
import pandas as pd
import numpy as np
from copy import deepcopy
from tqdm import tqdm
import math
import sys

# To use this collab, please take note on how to mount the data drive
# 1. Add shortcut of the Tuan_Analysis_Vietnam_Stroke_Flood folder to your Main Drive
# 2. Done :D.
# Remember, you have to add the shortcut to your Main Drive folder
root_dir = './'
sys.path.append(root_dir)
chirps_file = root_dir + "Data/vietnam/fluvial_defended/FD_1in5.csv"
chirps_data = pd.read_csv(chirps_file)
chirps_data.columns = ['Lon', 'Lat', 'FD_5yrs_level']
chirps_data = chirps_data.where(chirps_data['FD_5yrs_level'] < 999)
chirps_data.dropna(inplace=True)
chirps_data.reset_index(drop=True, inplace=True)

facs_file = root_dir + "Data/stroke_facs_latest.csv"
# facs_file = root_dir + "/Data/stroke-facs.csv"
stroke_data = pd.read_csv(facs_file)[
    ['Name_English', 'longitude', 'latitude', 'pro_name_e', 'dist_name_e']]
stroke_data.columns = ['Facility_Name', 'Lon', 'Lat', 'Province', 'District']
stroke_data['Lon'] = stroke_data['Lon'].apply(lambda x: round(x, 3))
stroke_data['Lat'] = stroke_data['Lat'].apply(lambda x: round(x, 3))
stroke_data = stroke_data[:10]
# stroke_data.head(10)

# Merge all flood dataset
file_dict = {'FD_10yrs_level': "Data/vietnam/fluvial_defended/FD_1in10.csv",
             'FD_20yrs_level': "Data/vietnam/fluvial_defended/FD_1in20.csv",
             'FD_50yrs_level': "Data/vietnam/fluvial_defended/FD_1in50.csv",
             'FD_75yrs_level': "Data/vietnam/fluvial_defended/FD_1in75.csv",
             'FD_100yrs_level': "Data/vietnam/fluvial_defended/FD_1in100.csv",
             'FD_200yrs_level': "Data/vietnam/fluvial_defended/FD_1in200.csv",
             'FD_250yrs_level': "Data/vietnam/fluvial_defended/FD_1in250.csv",
             'FD_500yrs_level': "Data/vietnam/fluvial_defended/FD_1in500.csv",
             'FD_1000yrs_level': "Data/vietnam/fluvial_defended/FD_1in1000.csv",
             'FU_5yrs_level': "Data/vietnam/fluvial_undefended/FU_1in5.csv",
             'FU_10yrs_level': "Data/vietnam/fluvial_undefended/FU_1in10.csv",
             'FU_20yrs_level': "Data/vietnam/fluvial_undefended/FU_1in20.csv",
             'FU_50yrs_level': "Data/vietnam/fluvial_undefended/FU_1in50.csv",
             'FU_75yrs_level': "Data/vietnam/fluvial_undefended/FU_1in75.csv",
             'FU_100yrs_level': "Data/vietnam/fluvial_undefended/FU_1in100.csv",
             'FU_200yrs_level': "Data/vietnam/fluvial_undefended/FU_1in200.csv",
             'FU_250yrs_level': "Data/vietnam/fluvial_undefended/FU_1in250.csv",
             'FU_500yrs_level': "Data/vietnam/fluvial_undefended/FU_1in500.csv",
             'FU_1000yrs_level': "Data/vietnam/fluvial_undefended/FU_1in1000.csv",
             }
all_flood_cases = ['FD_5yrs_level'] + list(file_dict.keys())
# process all data files from CHIRPS
for flood_case in tqdm(file_dict.keys()):
    chirps_file = root_dir + file_dict[flood_case]
    new_chirps_data = pd.read_csv(chirps_file)
    # new_chirps_data.dropna(inplace=True)
    new_chirps_data.columns = ['Lon', 'Lat', flood_case]
    new_chirps_data = new_chirps_data.where(new_chirps_data[flood_case] < 999)
    new_chirps_data.dropna(inplace=True)
    chirps_data = chirps_data.merge(new_chirps_data,
                                    how='outer', on=['Lon', 'Lat'])

chirps_data.reset_index(drop=True, inplace=True)
chirps_data = chirps_data.sort_values(['Lon', 'Lat'], ascending=False)
chirps_data.to_csv('./Data/full_df.csv', index=False)
# chirps_data = pd.read_csv('./Data/full_df.csv')
# chirps_data.head(10)

sq_size = 5
dec_level = 3
round_facs_df = deepcopy(stroke_data)
for flood_case in all_flood_cases:
    round_facs_df[flood_case] = np.zeros(round_facs_df.shape[0])

# round them accordingly
round_facs_df['Lon'] = round_facs_df['Lon'].apply(lambda x: round(x, dec_level))
round_facs_df['Lat'] = round_facs_df['Lat'].apply(lambda x: round(x, dec_level))
# round_facs_df = round_facs_df.transpose()
# iterate through all the facilities to find the corresponding point
for i in tqdm(range(round_facs_df.shape[0])):
    current_facs = round_facs_df.iloc[i, :]
    facs_lon = current_facs["Lon"]
    facs_lat = current_facs["Lat"]
    max_lon = facs_lon + sq_size * math.pow(10, -dec_level)
    min_lon = facs_lon - sq_size * math.pow(10, -dec_level)
    flood_lon_df = deepcopy(chirps_data.where(chirps_data["Lon"] < max_lon))
    flood_lon_df = flood_lon_df.where(flood_lon_df["Lon"] > min_lon)
    flood_lon_df.dropna(inplace=True, how='all')
    if flood_lon_df.shape[0] == 0:
        continue
    min_lat = facs_lat - sq_size * math.pow(10, -dec_level)
    max_lat = facs_lat + sq_size * math.pow(10, -dec_level)
    flood_final_df = flood_lon_df.where(flood_lon_df["Lat"] < max_lat)
    flood_final_df = flood_final_df.where(flood_final_df["Lat"] > min_lat)
    flood_final_df.dropna(inplace=True, how='all')
    if flood_final_df.shape[0] == 0:
        continue
    flood_level_list = flood_final_df.max(skipna=True, axis=0).to_numpy()[2:]
    # temp = round_facs_df.iloc[i, 5:]
    round_facs_df.iloc[i, 5:] = flood_level_list
pass


