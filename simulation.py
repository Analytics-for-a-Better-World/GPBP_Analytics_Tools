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
from Scripts.haversine_vectorize import haversine_vectorize


def random_gps(bounds: Polygon):
    """
    Modular function to automatically random a new gps point based on the polygon boundary
    :param bounds: the Polygon object passed from the geojson df
    :return: new GPS point
    """
    inside_poly = False
    min_lon, min_lat, max_lon, max_lat = bounds.bounds
    # I understand this randomization process is very inefficient, but ...
    # deadline is more important, so I will leave this to whoever is better to solve it for me
    while not inside_poly:
        new_lon = round(np.random.uniform(min_lon, max_lon), 5)
        new_lat = round(np.random.uniform(min_lat, max_lat), 5)
        new_gps = Point(new_lon, new_lat)
        if bounds.contains(new_gps):
            inside_poly = True
            return new_lon, new_lat
    return False


def open_connection():
    """
    Create connection to MySQL DB
    :return: MySQL connector object
    """
    mydb = connect(
        # fixed to connect to db server here
        host="localhost",
        user="nyfed",
        password="Test@123",
        database='GPBP'
    )
    return mydb


def travel_time_req(source_lon, source_lat, to_list):
    """
    Request Mapbox API to calculate drive-time from a source point to list of facilities
    :param source_lon: source's longitude
    :param source_lat: source's latitude
    :param to_list: list of coordinates from different facilities
    :return: a list driving-time with index corresponding to the order of facilities in the original to_list
    """
    # the coordinate pair come in the form of: (longitude. latitude)
    coordinate_str = str(source_lon) + ',' + str(source_lat)
    for destination in to_list:
        coordinate_str += ';' + str(destination[0]) + ',' + str(destination[1])
    token = """pk.eyJ1IjoicGFydmF0aHlrcmlzaG5hbmsiLCJhIjoiY2tybGFoMTZwMGJjdDJybnYyemwxY3QxMSJ9.FXaVYsMF3HIzw7ZQFQPhSw"""
    # Mapbox API is used with max of 10 coordinates per request
    # maximum is 30 request per minute
    # coordinate request is in the form of : /lon1, lat1;lon2, lat2;.../
    # one can use the parameter {sources} to point which coordinate pair is the destination to reduce request time
    # same can be said about {destination}
    request_url = """https://api.mapbox.com/directions-matrix/v1/mapbox/driving-traffic/"""
    request_params = """?annotations=duration&sources=0&access_token="""
    request_mapbox_driving = request_url + coordinate_str + request_params + token
    try:
        request_pack = json.loads(requests.get(request_mapbox_driving).content)
        if 'messsage' in request_pack.keys():
            if request_pack['durations'] == "Too Many Requests":
                print('Use too many at ' + str(datetime.today()))
                return False
        duration_minutes = request_pack['durations'][0][1:]
        return duration_minutes
    except Exception as e:
        print(e)
        # I did a blind try-except since I dont know which error might come from the MapBox API
        # either they dont have the calculation or the token has reached its minutely limit
        return False


def record_result(res_list: tuple):
    """
    record the result into mysql db to preserve data
    :param res_list: the tuple of the queried result. The tuple must contain these data:
        - Time of request: DATE
        - Coordinates: list of (lon, lat) saved in TEXT
        - Province Name: VARCHAR
        - Driving time for 45 facilities: the list are saved as a full string in TEXT in the DB
        - Haversine distance for 45 facilities: the list are saved as a full string in TEXT in the DB
        - Mapbox API's response time: list of request times across all 5 queries
        - Total time for one full run on each GPS point: one
    :return:
    """
    mydb = open_connection()
    cursor = mydb.cursor()
    insert_query = """  INSERT INTO gpbp(req_time, source_point, prov_name, drive_times, harv_dist, resp_time, runtime) 
                        VALUES(%s ,%s ,%s ,%s ,%s ,%s ,%s)"""
    cursor.execute(insert_query, res_list)
    mydb.commit()
    cursor.close()
    mydb.close()
    return


def return_closest_45(source_lon, source_lat, facs_df):
    """
    Return the closest 45 facilities in haversine distance. The returned df is sort ascendingly
    :param source_lon: longitude of the source GPS
    :param source_lat: latitude of the source GPS
    :param facs_df: facilities df
    :return:
    """
    res_df = deepcopy(facs_df)
    harv_dist = np.zeros(res_df.shape[0], dtype=float)
    for i in range(len(harv_dist)):
        dest_lon = res_df['Lon'].iloc[i]
        dest_lat = res_df['Lat'].iloc[i]
        harv_dist[i] = haversine_vectorize(source_lon, source_lat, dest_lon, dest_lat)
    res_df['Harversine_Dist'] = harv_dist
    res_df.sort_values('Harversine_Dist', inplace=True)
    res_df.reset_index(inplace=True, drop=True)
    return res_df.iloc[:45, :]


# it is just me tired and dont know how to name this function
def sth(prov_name, prov_df: pd.DataFrame, facs_df: pd.DataFrame):
    """
    Core part of the simulation. It requests the driving-time API and calculate result.
    This would later become the core for the main API
    :param prov_name: code name of the province
    :param prov_df: province df
    :param facs_df: facilities df
    :return:
        - final_drive_res: str of the list of the driving time from the source to 45 closest facilities
        - final_request_time: str of the list of the request time from MapBox API
        - str of the coordinates for the source GPS
        - harv_dist_str: str of the list of the harvesine distances from the source to 45 closest facilities
    """
    # take out the rows of the interested province
    prov_geometry = prov_df.where(prov_df['GID_1'] == prov_name)
    prov_geometry.dropna(inplace=True)
    # randomly choose one of the polygon from the rows of polygons forming the province
    geo_choice = np.random.randint(0, prov_geometry.shape[0])
    # create a randomized gps point from the boundary
    gps_lon, gps_lat = random_gps(prov_geometry["geometry"].iloc[geo_choice])

    # data preparation for the facilities list
    facs_df_45 = return_closest_45(gps_lon, gps_lat, facs_df)
    harv_dist_list = facs_df_45['Harversine_Dist'].to_numpy().tolist()
    facs_list = facs_df_45[['Lon', 'Lat']].to_numpy().tolist()

    final_drive_res = ''
    final_request_time = ''

    for i in range(5):
        start_idx = i * 9
        end_idx = (i + 1) * 9
        # the queried_res come in the form of list of drive time in seconds with corresponding index with the facilities
        start_time = datetime.now()
        queried_res = travel_time_req(gps_lon, gps_lat, facs_list[start_idx: end_idx])
        # here is to capture the case of failed connection and limited access from Mapbox API
        if not queried_res:
            queried_res = []
        end_time = datetime.now()
        cost = round((end_time - start_time).microseconds / 1000, 2)
        # transform the result list into str for db log
        final_drive_res += ','.join(str(x) for x in queried_res)
        final_request_time = final_request_time + ',' + str(cost)
    # remove unnecessary comma and data prep before returning result
    final_drive_res = final_drive_res.strip()
    final_request_time = final_request_time.strip()
    harv_dist_str = ','.join(str(x) for x in harv_dist_list).strip()
    return final_drive_res, final_request_time[1:], str(gps_lon) + ',' + str(gps_lat), harv_dist_str


def main():
    """
    Main simulation function
    :return: None
    """
    file_name = './Data/gadm_vietnam.geojson'
    province_bounds = gpd.read_file(file_name, driver='GeoJSON')
    province_bounds = deepcopy(province_bounds[['GID_1', 'NAME_1', 'geometry']])
    province_list = list(set(province_bounds['GID_1'].to_numpy().tolist()))
    stroke_facs = pd.read_csv('./Data/stroke_facs_latest.csv')
    stroke_facs = deepcopy(stroke_facs[['Name_English', 'longitude', 'latitude', 'pro_name_e', 'dist_name_e']])
    stroke_facs.columns = ['Facility_Name', 'Lon', 'Lat', 'Province', 'District']
    number_of_province = 63
    number_of_simulation = 5000
    # the number is 5000 not 30000 because for each minute,
    # I can send 30 requests with 9 stroke centres each request
    # thus, for each minute, I can simulate 6 GPS points at the same time
    # (roughly, since I will not try to do multithreading, it will all be sequential request)
    simulate_list = province_list + np.random.choice(province_list, 57).tolist()
    np.random.shuffle(simulate_list)
    for _ in tqdm(range(number_of_simulation)):
        # for the distribution of time request across all 63 provinces
        # in each hour, I will do a subset of 60 provinces from the list of 63
        start_time = datetime.now()
        for idx in range(6):
            # if the list run out of candidate to use, recreate the list
            if len(simulate_list) == 0:
                simulate_list = province_list + np.random.choice(province_list, 57).tolist()
                np.random.shuffle(simulate_list)

            start_each = datetime.today()
            # main simulation
            # 2 provinces for each run
            # this is the first one
            first_prov = simulate_list.pop()
            final_drive_res, final_request_time, gps_str, harv_dist_str = sth(first_prov, province_bounds, stroke_facs)
            end_first = datetime.now()
            cost_first = round((start_each - end_first).microseconds / 1000, 2)
            record_result((start_each, gps_str, first_prov,
                           final_drive_res, harv_dist_str, final_request_time, cost_first))

        end_time = datetime.now()
        # cost time is used to control if we have reached the maximum request per minute set out by MapBox or not
        cost_time = (end_time - start_time).total_seconds()
        if cost_time < 60:
            time.sleep(60 - cost_time)
    return


if __name__ == '__main__':
    # HERE LIES MY UNIT TEST
    # file_name = './Data/gadm_vietnam.geojson'
    # edges = gpd.read_file(file_name, driver='GeoJSON')
    # temp = edges.iloc[0]
    #
    # # start = datetime.now()
    # # temp = random_gps(temp["geometry"])
    # # end = datetime.now()
    # # print((end - start).microseconds)
    #
    # stroke_facs = pd.read_csv('./Data/stroke_facs_latest.csv')
    # stroke_facs = deepcopy(stroke_facs[['Name_English', 'longitude', 'latitude', 'pro_name_e', 'dist_name_e']])
    # stroke_facs.columns = ['Facility_Name', 'Lon', 'Lat', 'Province', 'District']
    #
    # start = datetime.today()
    # print(start)
    # temp = return_closest_45(temp[0], temp[1], stroke_facs)
    # end = datetime.now()
    # print((end - start).microseconds)
    # temp = travel_time_req(-122.42, 37.78, [[-122.45, 37.91], [-122.48, 37.73]])

    # start = datetime.now()
    # temp, a, b, c = sth('VNM.8_1', edges[['GID_1', 'NAME_1', 'geometry']], stroke_facs)
    # end = datetime.now()
    # print((end - start))
    # print(temp)
    # print(a)
    # print(b)
    # print(c)
    # pass
    # AND HERE IS THE MAIN SIMULATION
    main()
