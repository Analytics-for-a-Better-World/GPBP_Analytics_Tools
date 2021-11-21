import pandas as pd

root_dir = './'
res_file = root_dir + 'Data/simulation_112121.csv'
res_df = pd.read_csv(res_file, header=None)
res_df.columns = ['time_req', 'coords', 'prov_code', 'drive_time', 'harv_dist',
                  'resp_time', 'total_time']

import numpy as np
from copy import deepcopy
from tqdm import tqdm
import math
from datetime import datetime

row_count = res_df.shape[0]
template_array = np.ones(row_count) * np.nan
# add fastest drive time, and the position
res_df['fastest_drive'] = deepcopy(template_array)
res_df['closest_facs'] = deepcopy(template_array)
res_df['failed'] = [False for x in range(row_count)]
res_df['rush_hour'] = [False for x in range(row_count)]
res_df['top_9'] = deepcopy(template_array)
res_df['top_18'] = deepcopy(template_array)
res_df['top_27'] = deepcopy(template_array)
for i in tqdm(range(row_count)):
    time_req = datetime.strptime(res_df['time_req'][i],
                                 '%Y-%m-%d %H:%M:%S')
    res_df['time_req'][i] = time_req
    if 7 <= time_req.hour <= 9 or 17 <= time_req.hour <= 19:
        res_df['rush_hour'] = True
    all_time = res_df['drive_time'][i].split(',')
    time_array = []
    for j in all_time:
        try:
            time_array.append(round(float(j) / 3600, 2))
        except:
            time_array.append(np.inf)
    min_time = min(time_array)
    if not math.isnan(min_time):
        res_df['failed'][i] = False
        res_df['fastest_drive'][i] = min_time
        res_df['closest_facs'][i] = int(np.argmin(time_array))
        time_array = sorted(time_array)
        res_df['top_9'][i] = time_array[8]
        res_df['top_18'][i] = time_array[17]
        res_df['top_27'][i] = time_array[16]
