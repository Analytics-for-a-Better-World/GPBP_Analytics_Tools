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
from datetime import date, timedelta
from matplotlib import pyplot as plt


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


mydb = open_connection()
cursor = mydb.cursor()
insert_query = """select * from chirps_d"""
cursor.execute(insert_query)
chirps_daily_data = cursor.fetchall()
mydb.commit()
cursor.close()
mydb.close()
chirps_daily_df = pd.DataFrame(chirps_daily_data)
chirps_daily_df.columns = ['max_rain', 'timeframe']

yrs_list = [str(int(x)) for x in np.arange(1981, 2022, 1)]

sdate = date(2008, 1, 1)  # start date
edate = date(2008, 12, 31)  # end date

delta = edate - sdate  # as timedelta
date_list = []
for i in range(delta.days + 1):
    day = sdate + timedelta(days=i)
    date_list.append(str(day)[5:])
chirps_daily_df_new = pd.DataFrame()
for col in date_list:
    chirps_daily_df_new[col] = np.zeros(len(yrs_list))

chirps_daily_df_new.index = yrs_list
for idx in tqdm(range(chirps_daily_df.shape[0])):
    mon_day = chirps_daily_df['timeframe'][idx][5:]
    yr = chirps_daily_df['timeframe'][idx][:4]
    chirps_daily_df_new[mon_day][yr] = chirps_daily_df['max_rain'][idx]

fig, ax = plt.subplots(figsize=(10, 5))
mean_daily_chirps = chirps_daily_df_new.mean(axis=0)
max_daily_chirps = chirps_daily_df_new.max(axis=0)
min_daily_chirps = chirps_daily_df_new.min(axis=0)
temp_plt = ax.errorbar(chirps_daily_df_new.columns,
                       mean_daily_chirps,
                       [mean_daily_chirps - min_daily_chirps,
                        max_daily_chirps - mean_daily_chirps],
                       fmt='.k', ecolor='gray', lw=1)
temp_plt.plot(ax=ax)
pass
