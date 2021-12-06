"""
This code is used to extract all daily data for Vietnam from CHIRPS
"""

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

root_dir = './'


def listFD(url, ext=''):
    page = requests.get(url).text
    # print page
    soup = BeautifulSoup(page, 'html.parser')
    return [node.get('href') for node in soup.find_all('a') if
            node.get('href').endswith(ext)]


url = 'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/'
ext = '.gz'

import os


def check_missing_tar(tar_dir, url, ext):
    tar_list = os.listdir(tar_dir)
    tar_list = [x for x in tar_list if
                os.path.isfile(tar_dir + x) or (ext in x)]
    url_files = listFD(url, ext)
    diff = list(set(url_files) - set(tar_list))
    return diff


import requests
import time
from tqdm import tqdm


def download_missing_files(tar_dir, save_dir, url, ext):
    file_list = check_missing_tar(tar_dir, url, ext)
    for file in tqdm(file_list):
        download_url = url + file
        file_dir = save_dir + file
        with open(file_dir, 'wb') as out_file:
            content = requests.get(download_url, stream=True).content
            out_file.write(content)
        time.sleep(1)
    return


import gzip
import shutil


def check_missing_tif(tar_dir, tif_dir):
    tar_list = os.listdir(tar_dir)
    tar_list = [x[:-7] for x in tar_list if
                os.path.isfile(tar_dir + x) or '.gz' in x]
    tif_list = os.listdir(tif_dir)
    tif_list = [x[:-4] for x in tif_list if
                os.path.isfile(tif_dir + x) or '.tif' in x]
    diff = list(set(tar_list) - set(tif_list))
    return diff


def unzip_missing_files(tar_dir, save_dir):
    file_list = check_missing_tif(tar_dir, save_dir)
    for file in tqdm(file_list):
        tif_file = save_dir + file + '.tif'
        tar_file = tar_dir + file + '.tif.gz'
        with gzip.open(tar_file, 'rb') as f_in:
            with open(tif_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    return


from raster2xyz.raster2xyz import Raster2xyz


def check_missing_csv(tif_dir, csv_dir):
    tif_list = os.listdir(tif_dir)
    tif_list = [x[:-4] for x in tif_list if
                os.path.isfile(tif_dir + x) or '.tif' in x]
    csv_list = os.listdir(csv_dir)
    csv_list = [x[:-4] for x in csv_list if
                os.path.isfile(csv_dir + x) or '.csv' in x]
    diff = list(set(tif_list) - set(csv_list))
    return diff


def rasterize(tif_dir, save_dir):
    rtxyz = Raster2xyz()
    file_names = check_missing_csv(tif_dir, save_dir)
    for file_name in tqdm(file_names):
        input_tif = tif_dir + file_name + '.tif'
        out_csv = save_dir + file_name + '.csv'
        rtxyz.translate(input_tif, out_csv)


#
# yrs = np.arange(1981, 2021, 1)
# tar_folder = root_dir + 'Data/CHIRPS/Daily/tar/'
# for yr in yrs:
#     daily_url = url + str(int(yr)) + '/'
#     download_missing_files(tar_folder, tar_folder, daily_url, ext)
# tif_folder = root_dir + 'Data/CHIRPS/Daily/tif/'
# unzip_missing_files(tar_folder, tif_folder)
# csv_folder = root_dir + 'Data/CHIRPS/Daily/Raw/'
# rasterize(tif_folder, csv_folder)

def open_connection():
    """
    Create connection to MySQL DB
    :return: MySQL connector object
    """
    from mysql.connector import connect
    mydb = connect(
        # fixed to connect to db server here
        host="localhost",
        user="root",
        password="Ahihi123",
        database='gpbp'
    )
    return mydb


def record_result(res_list, col_name):
    """
    record the result into mysql db to preserve data
    :param res_list: the tuple of the queried result. It must contain these:
        - Time of request: DATE
        - Coordinates: list of (lon, lat) saved in TEXT
        - min_drive: the quickest driving time for the point
    :param col_name
    :return:
    """
    mydb = open_connection()
    cursor = mydb.cursor()
    insert_query = """  UPDATE chirps_m
                        SET {} = %s
                        WHERE idx= %s """.format(col_name)

    cursor.executemany(insert_query, res_list)
    mydb.commit()
    cursor.close()
    mydb.close()
    return


temp_db = open_connection()
temp_cursor = temp_db.cursor()
idx_query = """SELECT idx from chirps_m"""
temp_cursor.execute(idx_query)
idx_list = np.squeeze(temp_cursor.fetchall())
temp_db.commit()
temp_cursor.close()
temp_db.close()
# curr_df = pd.read_csv('./Data/CHIRPS/chirps_vn_data.csv')
# curr_df = curr_df[['Lon', 'Lat']]
# curr_df['idx'] = np.zeros(curr_df.shape[0])
# curr_df = pd.read_csv('./Data/idx_file.csv')
# curr_df.to_sql('chirps_d', connector, index=False)
file_list = os.listdir('./Data/CHIRPS/Raw')

for file in tqdm(file_list):
    col_name = '_'.join(file.split('.')[-3:-1])
    temp_db = open_connection()
    temp_cursor = temp_db.cursor()
    idx_query = "Alter table chirps_m add {} float".format(col_name)
    temp_cursor.execute(idx_query)
    temp_db.commit()
    temp_cursor.close()

    check_file = pd.read_csv('./Data/CHIRPS/Raw/' + file)
    check_file.columns = ['Lon', 'Lat', 'mm']
    check_file = check_file.loc[idx_list, ['mm']]
    check_values = np.squeeze(check_file.to_numpy()).tolist()
    merge_list = [(float(x), int(y), ) for x, y in zip(check_values, idx_list)]
    record_result(merge_list, col_name)
    pass


