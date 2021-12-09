import geopandas as gpd
import pandas as pd
import numpy as np
from raster2xyz.raster2xyz import Raster2xyz
from tqdm import tqdm
import os
from flask import Flask, flash, redirect, render_template, request, session, \
    abort, json
import json
import requests
import math
from copy import deepcopy
from geopandas import GeoDataFrame
from shapely.geometry import Point
import matplotlib.pyplot as plt
from tqdm import tqdm

# transform tif image from CHIRPS to csv

# input_raster = "./Data/CHIRPS/tif/"
# save_dir = "./Data/CHIRPS/Raw/"
# # out_csv = "demo_out_xyz.csv"
# rtxyz = Raster2xyz()
# file_names = os.listdir(input_raster)
# file_names = ['chirps-v2.0.2016.12.13.tif']
# for file_name in file_names:
#     if 'tif' not in file_name:
#         continue
#     input_tif = input_raster + file_name
#     out_csv = save_dir + file_name[:-4] + '.csv'
#     rtxyz.translate(input_tif, out_csv)

# chirps_file = "./Data/vietnam/pluvial/P_1in5.csv"
# chirps_data = pd.read_csv(chirps_file)
# print(chirps_data.describe())

# facs_lon = 106.694
# facs_lat = 10.804
# sq_size = 5
# dec_level = 3
# temp_file = "./Data/vietnam/fluvial_undefended/FU_1in200.csv"
# temp_ori = pd.read_csv(temp_file)
# temp_ori.columns = ['Lon', 'Lat', 'flood_level']
# temp_ori = temp_ori.where(temp_ori['flood_level'] < 999)
# temp_ori.dropna(inplace=True)
# temp_ori.reset_index(drop=True, inplace=True)
#
# upper_lon = facs_lon + sq_size * math.pow(10, -dec_level)
# lower_lon = facs_lon - sq_size * math.pow(10, -dec_level)
# upper_lat = facs_lat + sq_size * math.pow(10, -dec_level)
# lower_lat = facs_lat - sq_size * math.pow(10, -dec_level)
#
# flood_df = temp_ori.where(temp_ori["Lon"] < upper_lon).dropna()
# flood_df = flood_df.where(flood_df["Lon"] > lower_lon).dropna()
# flood_df = flood_df.where(flood_df["Lat"] < upper_lat).dropna()
# flood_df = flood_df.where(flood_df["Lat"] > lower_lat).dropna()
#
# flood_df

import numpy as np

# from tqdm import tqdm
#
# file_dir = "./Data/CHIRPS/Raw/"
# file_names = os.listdir(file_dir)
# chirps_df = pd.DataFrame()
# for csv_file in tqdm(file_names):
#     if '.csv' not in csv_file:
#         continue
#     new_df = pd.read_csv(file_dir + csv_file)
#     year, month = csv_file.split('.')[2:4]
#     new_df.columns = ['Lon', 'Lat', str(month)+'-'+str(year)]
#
#     # because CHIRPS is in quasi-global format
#     # we need to transform it back to normal format
# #     new_df['Lat'] = np.multiply(new_df['Lat'], 3.6)
#     if chirps_df.shape[0] == 0:
#         chirps_df = new_df
#     else:
#         chirps_df = chirps_df.merge(new_df,
#                                     how='outer',
#                                     on=['Lat', 'Lon'])
# chirps_df.to_csv("./Data/CHIRPS/chirps_full_data.csv", index=False)
# chirps_df = pd.read_csv("./Data/CHIRPS/chirps_full_data.csv")
# new_df = pd.read_csv("./Data/CHIRPS/Raw/chirps-v2.0.2019.09.csv")
# year, month = ['2019', '09']
# new_df.columns = ['Lon', 'Lat', str(month)+'-'+str(year)]
# chirps_df = chirps_df.merge(new_df,
#                             how='outer',
#                             on=['Lat', 'Lon'])
# chirps_df.to_csv("./Data/CHIRPS/chirps_full_data.csv", index=False)
# chirps_df.to_csv("./Data/CHIRPS/chirps_full_data.csv", index=False)

# vn_prov = gpd.read_file('./Data/gadm_vietnam.geojson')
# vn_bound = vn_prov.geometry.unary_union
# chirps_df = pd.read_csv('./Data/CHIRPS/chirps_full_data.csv')
#
# min_lon, min_lat, max_lon, max_lat = vn_bound.bounds
# chirps_df = chirps_df.where(chirps_df['Lon'] < max_lon).dropna()
# chirps_df.reset_index(inplace=True, drop=True)
# chirps_df = chirps_df.where(chirps_df['Lon'] > min_lon).dropna()
# chirps_df.reset_index(inplace=True, drop=True)
# chirps_df = chirps_df.where(chirps_df['Lat'] < max_lat).dropna()
# chirps_df.reset_index(inplace=True, drop=True)
# chirps_df = chirps_df.where(chirps_df['Lat'] > min_lat).dropna()
# chirps_df.reset_index(inplace=True, drop=True)
#
# from shapely.geometry import Point
#
# drop_list = []
# for idx in range(chirps_df.shape[0]):
#     new_lon = chirps_df["Lon"][idx]
#     new_lat = chirps_df["Lat"][idx]
#     cur_point = Point(new_lon, new_lat)
#     if not vn_bound.contains(cur_point):
#         drop_list.append(idx)
# chirps_df.drop(drop_list, inplace=True)
# chirps_df.to_csv("./Data/CHIRPS/chirps_vn_data.csv",
#                  index=False)

# list_df = pd.read_csv('./Data/idx_file.csv')
# idx_list = list_df['idx'].to_numpy()
# check_df = pd.read_csv('./Data/CHIRPS/Raw/chirps-v2.0.2020.10.csv')
# check_df.columns = ['Lon', 'Lat', 'mm']
# check_df = check_df.loc[idx_list, ['Lon', 'Lat', 'mm']]
# max_idx = np.argmax(check_df['mm'])
# heaviest = check_df.iloc[max_idx, :]
root_dir = './'


# vn_prov = gpd.read_file(root_dir + '/Data/gadm_vietnam.geojson')
# map_data_full = pd.read_csv(root_dir + "/Data/drive_time_res_oog.csv")
# map_data_full.columns = ['req_time', 'Lon', 'Lat', 'min_drive', 'closest_facs_code', 'facs_type']
# map_data = map_data_full.where(map_data_full['facs_type'] == 'Hạng đặc biệt').dropna()
# map_data = map_data[['Lon', 'Lat', 'min_drive']]
# map_data.columns = ['Lon', 'Lat', 'Hạng đặc biệt']
# map_data['Hạng 1'] = map_data_full.where(map_data_full['facs_type'] == 'Hạng 1').dropna()['min_drive'].to_numpy()
# map_data['Hạng 2'] = map_data_full.where(map_data_full['facs_type'] == 'Hạng 2').dropna()['min_drive'].to_numpy()
# map_data['Hạng 3'] = map_data_full.where(map_data_full['facs_type'] == 'Hạng 3').dropna()['min_drive'].to_numpy()
# map_data.reset_index(drop=True, inplace=True)

# from copy import deepcopy
# north_df = deepcopy(map_data)
# north_df['Lat'] += 0.01
#
# south_df = deepcopy(map_data)
# south_df['Lat'] -= 0.01
#
# east_df = deepcopy(map_data)
# east_df['Lon'] += 0.01
#
# west_df = deepcopy(map_data)
# west_df['Lon'] -= 0.01
#
# northeast_df = deepcopy(map_data)
# northeast_df['Lat'] += 0.01
# northeast_df['Lon'] += 0.01
#
# northwest_df = deepcopy(map_data)
# northwest_df['Lat'] += 0.01
# northwest_df['Lon'] -= 0.01
#
# southeast_df = deepcopy(map_data)
# southeast_df['Lat'] -= 0.01
# southeast_df['Lon'] += 0.01
#
# southwest_df = deepcopy(map_data)
# southwest_df['Lat'] -= 0.01
# southwest_df['Lon'] -= 0.01
#
#
# map_data = pd.concat([map_data, north_df])
# map_data = pd.concat([map_data, south_df])
# map_data = pd.concat([map_data, east_df])
# map_data = pd.concat([map_data, west_df])
# map_data = pd.concat([map_data, northeast_df])
# map_data = pd.concat([map_data, northwest_df])
# map_data = pd.concat([map_data, southeast_df])
# map_data = pd.concat([map_data, southwest_df])
#
# map_data.reset_index(drop=True, inplace=True)

# min_drives = []
# for i in range(map_data.shape[0]):
#     min_drives.append(min(map_data.iloc[i, 2:].to_numpy()))
# map_data['min_drive'] = min_drives
# prov_list = []
# for i in tqdm(range(map_data.shape[0])):
#     curr_lon = map_data['Lon'][i]
#     curr_lat = map_data['Lat'][i]
#     check_point = Point(curr_lon, curr_lat)
#     temp = vn_prov.contains(check_point)
#     temp = temp.where(temp == True).dropna()
#     if temp.shape[0] > 0:
#         prov_idx = temp.index[0]
#         prov = vn_prov['NAME_1'][prov_idx]
#         prov_list.append(prov)
#     else:
#         prov_list.append(None)
# map_data['Prov'] = prov_list
# map_data.to_csv('./Data/drive_time_oog_full.csv', index=False)

def find_closest_points(flood_df_full, flood_scenario, facs_df, aggregate_func,
                        sq_size=5, dec_level=3):
    new_facs_df = deepcopy(facs_df)
    # round them accordingly
    new_facs_df['Lon'] = new_facs_df['Lon'].apply(
        lambda x: round(x, dec_level))
    new_facs_df['Lat'] = new_facs_df['Lat'].apply(
        lambda x: round(x, dec_level))
    new_facs_df[flood_scenario] = np.ones(new_facs_df.shape[0], dtype=float) * np.nan
    # iterate through all the facilities to find the corresponding point
    for idx in tqdm(range(new_facs_df.shape[0])):
        current_facs_df = new_facs_df.iloc[idx, :]
        facs_longitude = current_facs_df["Lon"]
        facs_latitude = current_facs_df["Lat"]

        upper_longitude = facs_longitude + sq_size * math.pow(10, -dec_level)
        lower_longitude = facs_longitude - sq_size * math.pow(10, -dec_level)
        upper_latitude = facs_latitude + sq_size * math.pow(10, -dec_level)
        lower_latitude = facs_latitude - sq_size * math.pow(10, -dec_level)

        # queries the dataframe to find the flood risk points
        new_flood_df = flood_df_full.where(
            flood_df_full["Lon"] < upper_longitude).dropna()
        new_flood_df = new_flood_df.where(
            new_flood_df["Lon"] > lower_longitude).dropna()
        new_flood_df = new_flood_df.where(
            new_flood_df["Lat"] < upper_latitude).dropna()
        new_flood_df = new_flood_df.where(
            new_flood_df["Lat"] > lower_latitude).dropna()

        # this is to prevent the case of no suitable data points
        # breaking the function
        if new_flood_df.shape[0] == 0:
            continue

        new_facs_df.iloc[idx, 4] = aggregate_func(
            new_flood_df[flood_scenario].to_numpy())
    return new_facs_df


pop_file = root_dir + '/Data/population_vnm_2018-10-01(Facebook).csv'
fb_pop_data = pd.read_csv(pop_file)
fb_pop_data.columns = ['Lat', 'Lon', 'Pop_2015', 'Pop_2020']
full_df = pd.read_csv('./Data/drive_time_oog_ori.csv')
map_data_90m_pop = find_closest_points(fb_pop_data, 'Pop_2020',
                                       full_df, sum,
                                       15, 3)
map_data_90m_pop.to_csv(root_dir + 'Data/map_w_pop.csv', index=False)
pass
