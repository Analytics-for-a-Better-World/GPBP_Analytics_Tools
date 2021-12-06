import pandas as pd
import numpy as np
import math
from datetime import datetime

# a = pd.DataFrame({'a': [1, 2, 3],
#                   'b': [4, 5, 6]})
# print(a)
# temp = a.median(axis=0)[0]
# b = a['a'][1]
# print(temp)
#
# a = [[1, 2], [3, 4], [5, 6]]
# print(pd.DataFrame(a))
#
# a = [np.nan, np.nan]
# print(math.isnan(max(a)))
# print(datetime.today())

# if [False, False, True]:
#     print('a')
#
# idx_df = pd.read_csv('./Data/CHIRPS/chirps_daily_idx.csv')
# idx_df.sort_values('Lon', inplace=True)
# sq_size = 5
# dec_level = 2
# lon = 106.6
# lat = 17.47
# upper_longitude = lon + sq_size * math.pow(10, -dec_level)
# lower_longitude = lon - sq_size * math.pow(10, -dec_level)
# upper_latitude = lat + sq_size * math.pow(10, -dec_level)
# lower_latitude = lat - sq_size * math.pow(10, -dec_level)
# new_flood_df = idx_df.where(idx_df["Lon"] <= upper_longitude).dropna()
# new_flood_df = new_flood_df.where(new_flood_df["Lon"] >= lower_longitude).dropna()
# new_flood_df = new_flood_df.where(new_flood_df["Lat"] <= upper_latitude).dropna()
# new_flood_df = new_flood_df.where(new_flood_df["Lat"] >= lower_latitude).dropna()
# print(new_flood_df['idx'].to_numpy())

x = [1, 2, 3]
y = [4, 5, 6]
print([z + (0, ) for z in zip(x, y)])
