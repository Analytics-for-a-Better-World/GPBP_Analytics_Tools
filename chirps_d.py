"""
This code is used to extract all CHIRPS daily data for Dong Hoi Hospital
"""
import geopandas as gpd
import pandas as pd
import numpy as np
from datetime import datetime
import json
import requests
from shapely.geometry import Point, Polygon
from mysql.connector import connect
import math
import time
from copy import deepcopy
from tqdm import tqdm


def open_connection():
    """
    Create connection to MySQL DB
    :return: MySQL connector object
    """
    mydb = connect(
        # fixed to connect to db server here
        host="localhost",
        user="root",
        password="Ahihi123",
        database='gpbp'
    )
    return mydb


def record_result(res_list: tuple):
    mydb = open_connection()
    cursor = mydb.cursor()
    insert_query = """  INSERT INTO chirps_d_donghoi(sq1, sq2, sq3, sq4, timeframe) 
                        VALUES(%s,%s,%s, %s ,%s)"""
    cursor.execute(insert_query, res_list)
    mydb.commit()
    cursor.close()
    mydb.close()
    return


# daily_df = pd.read_csv('./Data/CHIRPS/Daily/Raw/chirps-v2.0.2021.10.01.csv')
# daily_df.columns = ['Lon', 'Lat', 'mm']
# daily_df = daily_df.round(3)
# check_df = pd.read_csv('./Data/CHIRPS/chirps_vn_data_daily.csv')
# idx_list = []
# for i in tqdm(range(check_df.shape[0])):
#     cur_lon = round(check_df['Lon'][i], 3)
#     cur_lat = round(check_df['Lat'][i], 3)
#     idx = daily_df.where(
#         (daily_df['Lon'] == cur_lon) & (
#                 daily_df['Lat'] == cur_lat)).dropna().index
#     if len(idx) >= 1:
#         idx_list.append(idx[0])
#     else:
#         print(cur_lon, cur_lat)
#
# check_df = check_df[['Lon', 'Lat']]
# check_df['idx'] = idx_list
# check_df.to_csv('./Data/CHIRPS/chirps_daily_idx.csv', index=False)
# pass

yrs_list = [str(int(x)) for x in np.arange(1981, 2022, 1)]

from bs4 import BeautifulSoup
import requests
import gzip
import shutil
from raster2xyz.raster2xyz import Raster2xyz


def listFD(url, ext=''):
    page = requests.get(url).text
    # print page
    soup = BeautifulSoup(page, 'html.parser')
    return [node.get('href') for node in soup.find_all('a') if
            node.get('href').endswith(ext)]


def check_time(timeframe):
    mydb = open_connection()
    cursor = mydb.cursor()
    insert_query = """select count(*)
                     from chirps_d_donghoi where timeframe = %s"""
    cursor.execute(insert_query, (timeframe,))
    check_num = cursor.fetchone()
    mydb.commit()
    cursor.close()
    mydb.close()
    return check_num[0]


url = 'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/'
ext = '.gz'
root_dir = 'D:/tmp/'
# list_df = pd.read_csv('./Data/CHIRPS/chirps_daily_idx.csv')
idx_list = [2041154, 2039048, 2041155, 2039049]
for yr in tqdm(yrs_list):
    check_url = url + yr + '/'
    check_urls = listFD(check_url, ext)
    for files in tqdm(check_urls):
        time_frame = files.split('/')[0]
        time_frame = '-'.join(time_frame.split('.')[-5:-2]).strip()
        month = time_frame.split('-')[1]
        if month != '10':
            continue
        temp = check_time(time_frame)
        if temp == 1:
            continue
        with open(root_dir + 'tmp.tif.gz', 'wb') as out_file:
            content = requests.get(check_url + files, stream=True).content
            out_file.write(content)

        with gzip.open(root_dir + 'tmp.tif.gz', 'rb') as f_in:
            with open(root_dir + 'tmp.tif', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        rtxyz = Raster2xyz()
        rtxyz.translate(root_dir + 'tmp.tif',
                        root_dir + 'tmp.csv')

        check_df = pd.read_csv(root_dir + 'tmp.csv')
        check_df.columns = ['Lon', 'Lat', 'mm']
        check_df = np.squeeze(check_df.loc[idx_list, ['mm']].to_numpy()).tolist()
        record_result(tuple(check_df + [time_frame]))

ext = '.tif'
root_dir = 'D:/tmp/'
# list_df = pd.read_csv('./Data/CHIRPS/chirps_daily_idx.csv')
idx_list = [2041154, 2039048, 2041155, 2039049]
for yr in tqdm(yrs_list):
    check_url = url + yr + '/'
    check_urls = listFD(check_url, ext)
    for files in tqdm(check_urls):
        time_frame = files.split('/')[0]
        time_frame = '-'.join(time_frame.split('.')[-4:-1]).strip()
        month = time_frame.split('-')[1]
        if month != '10':
            continue
        temp = check_time(time_frame)
        if temp == 1:
            continue
        with open(root_dir + 'tmp.tif', 'wb') as out_file:
            content = requests.get(check_url + files, stream=True).content
            out_file.write(content)

        # with gzip.open(root_dir + 'tmp.tif.gz', 'rb') as f_in:
        #     with open(root_dir + 'tmp.tif', 'wb') as f_out:
        #         shutil.copyfileobj(f_in, f_out)

        rtxyz = Raster2xyz()
        rtxyz.translate(root_dir + 'tmp.tif',
                        root_dir + 'tmp.csv')

        check_df = pd.read_csv(root_dir + 'tmp.csv')
        check_df.columns = ['Lon', 'Lat', 'mm']
        check_df = np.squeeze(check_df.loc[idx_list, ['mm']].to_numpy()).tolist()
        record_result(tuple(check_df + [time_frame]))