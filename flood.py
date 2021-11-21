import pandas as pd

root_dir = './'
chirps_file = root_dir + "Data/vietnam/fluvial_defended/FD_1in5.csv"
chirps_data = pd.read_csv(chirps_file)
chirps_data.dropna(inplace=True)
chirps_data.columns = ['Lon', 'Lat', 'FD_5yrs_level']

chirps_data = chirps_data.where(chirps_data['FD_5yrs_level'] < 999)
chirps_data.dropna(inplace=True)
chirps_data.reset_index(drop=True, inplace=True)

facs_file = root_dir + "/Data/stroke_facs_latest.csv"
# facs_file = root_dir + "/Data/stroke-facs.csv"
stroke_data = pd.read_csv(facs_file)[
    ['Name_English', 'longitude', 'latitude', 'pro_name_e', 'dist_name_e']]
stroke_data.columns = ['Facility_Name', 'Lon', 'Lat', 'Province', 'District']
stroke_data['Lon'] = stroke_data['Lon'].apply(lambda x: round(x, 3))
stroke_data['Lat'] = stroke_data['Lat'].apply(lambda x: round(x, 3))
stroke_data = stroke_data

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
             'P_5yrs_level': "Data/vietnam/pluvial/P_1in5.csv",
             'P_10yrs_level': "Data/vietnam/pluvial/P_1in5.csv",
             'P_20yrs_level': "Data/vietnam/pluvial/P_1in5.csv",
             'P_50yrs_level': "Data/vietnam/pluvial/P_1in5.csv",
             'P_75yrs_level': "Data/vietnam/pluvial/P_1in5.csv",
             'P_100yrs_level': "Data/vietnam/pluvial/P_1in5.csv",
             'P_200yrs_level': "Data/vietnam/pluvial/P_1in5.csv",
             'P_250yrs_level': "Data/vietnam/pluvial/P_1in5.csv",
             'P_500yrs_level': "Data/vietnam/pluvial/P_1in5.csv",
             'P_1000yrs_level': "Data/vietnam/pluvial/P_1in1000.csv",
             }
all_flood_cases = ['FD_5yrs_level'] + list(file_dict.keys())

from copy import deepcopy
from tqdm import tqdm
import math
import numpy as np

square_size = 5
decimal_level = 3
round_facs_df = deepcopy(stroke_data)
round_facs_df['FD_5yrs_level'] = np.zeros(round_facs_df.shape[0])
# round them accordingly
round_facs_df['Lon'] = round_facs_df['Lon'].apply(
    lambda x: round(x, decimal_level))
round_facs_df['Lat'] = round_facs_df['Lat'].apply(
    lambda x: round(x, decimal_level))
# round_facs_df = round_facs_df.transpose()
# iterate through all the facilities to find the corresponding point
for i in tqdm(range(round_facs_df.shape[0])):
    current_facs = round_facs_df.iloc[i, :]
    facs_lon = current_facs["Lon"]
    facs_lat = current_facs["Lat"]

    upper_lon = facs_lon + square_size * math.pow(10, -decimal_level)
    lower_lon = facs_lon - square_size * math.pow(10, -decimal_level)
    upper_lat = facs_lat + square_size * math.pow(10, -decimal_level)
    lower_lat = facs_lat - square_size * math.pow(10, -decimal_level)

    flood_df = chirps_data.where(chirps_data["Lon"] < upper_lon).dropna()
    flood_df = flood_df.where(flood_df["Lon"] > lower_lon).dropna()
    flood_df = flood_df.where(flood_df["Lat"] < upper_lat).dropna()
    flood_df = flood_df.where(flood_df["Lat"] > lower_lat).dropna()
    if flood_df.shape[0] == 0:
        # print(facs_lon, facs_lat)
        continue
    flood_level_list = max(flood_df['FD_5yrs_level'].to_numpy())
    round_facs_df.iloc[i, 5] = flood_level_list
fd_5yrs_df = round_facs_df.where(round_facs_df['FD_5yrs_level'] != 0).dropna()
fd_5yrs_df.sort_values('FD_5yrs_level', ascending=False)


def find_closest_points(flood_df_full, flood_scenario, facs_df, aggregate_func,
                        sq_size=5, dec_level=3):
    new_facs_df = deepcopy(facs_df)
    # round them accordingly
    new_facs_df['Lon'] = new_facs_df['Lon'].apply(
        lambda x: round(x, dec_level))
    new_facs_df['Lat'] = new_facs_df['Lat'].apply(
        lambda x: round(x, dec_level))
    new_facs_df[flood_scenario] = np.zeros(new_facs_df.shape[0], dtype=float)
    # iterate through all the facilities to find the corresponding point
    for idx in range(new_facs_df.shape[0]):
        current_facs_df = new_facs_df.iloc[idx, :]
        facs_longitude = current_facs_df["Lon"]
        facs_latitude = current_facs_df["Lat"]

        upper_longitude = facs_longitude + sq_size * math.pow(10, -dec_level)
        lower_longitude = facs_longitude - sq_size * math.pow(10, -dec_level)
        upper_latitude = facs_latitude + sq_size * math.pow(10, -dec_level)
        lower_latitude = facs_latitude - sq_size * math.pow(10, -dec_level)

        new_flood_df = flood_df_full.where(
            flood_df_full["Lon"] < upper_longitude).dropna()
        new_flood_df = new_flood_df.where(
            new_flood_df["Lon"] > lower_longitude).dropna()
        new_flood_df = new_flood_df.where(
            new_flood_df["Lat"] < upper_latitude).dropna()
        new_flood_df = new_flood_df.where(
            new_flood_df["Lat"] > lower_latitude).dropna()

        if new_flood_df.shape[0] == 0:
            # print(facs_lon, facs_lat)
            continue

        new_facs_df.iloc[idx, 5] = aggregate_func(
            new_flood_df[flood_scenario].to_numpy())
    return new_facs_df[flood_scenario].to_numpy()


for flood_case in tqdm(list(file_dict.keys())):
    file_data = pd.read_csv(root_dir + file_dict[flood_case])
    file_data.columns = ['Lon', 'Lat', flood_case]
    file_data = file_data.where(file_data[flood_case] < 999)
    file_data.dropna(inplace=True)
    file_data.reset_index(drop=True, inplace=True)
    round_facs_df[flood_case] = find_closest_points(file_data, flood_case,
                                                    stroke_data, max)
round_facs_df.to_csv('./Data/save_time.csv', index=False)
