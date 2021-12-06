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
import geopandas as gpd
from geopandas import GeoDataFrame
from shapely.geometry import Point
import matplotlib.pyplot as plt
from tqdm import tqdm

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
list_df = pd.read_csv('./Data/idx_file.csv')
idx_list = list_df['idx'].to_numpy()
check_df = pd.read_csv('./Data/CHIRPS/Raw/chirps-v2.0.2020.10.csv')
check_df.columns = ['Lon', 'Lat', 'mm']
check_df = check_df.loc[idx_list, ['Lon', 'Lat', 'mm']]
max_idx = np.argmax(check_df['mm'])
heaviest = check_df.iloc[max_idx, :]

pass
