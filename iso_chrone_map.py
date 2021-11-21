import geopandas as gpd
import pandas as pd
import numpy as np
from datetime import datetime
import json
import requests
from shapely.geometry import Point, Polygon, MultiPolygon
from mysql.connector import connect
import math
import time
from copy import deepcopy
from tqdm import tqdm
from Scripts.haversine_vectorize import haversine_vectorize

max_req_min = 60
max_coord_req = 25


def random_gps(bounds: MultiPolygon):
    """
    Modular function to automatically random a new gps point
    based on the polygon boundary
    :param bounds: the MultiPolygon object passed from the geojson df
    :return: list of GPS points
    """
    min_lon, min_lat, max_lon, max_lat = np.round(bounds.bounds, 2)

    min_lon -= 0.01
    min_lat -= 0.01
    max_lon += 0.01
    max_lat += 0.01

    lon_range = np.arange(min_lon, max_lon, 0.01)
    lat_range = np.arange(min_lat, max_lat, 0.01)
    coor_list = []
    for x in tqdm(lon_range):
        for y in lat_range:
            new_coord = Point(x, y)
            if bounds.contains(new_coord):
                coor_list.append([x, y])
    res_df = pd.DataFrame(coor_list)
    res_df.columns = ["Lon", "Lat"]
    res_df.to_csv('./Data/iso_chrone.csv', index=False)
    return


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
    Request Mapbox API to calculate drive-time from a source point to
    list of facilities
    :param source_lon: source's longitude
    :param source_lat: source's latitude
    :param to_list: list of coordinates from different facilities
    :return: a list driving-time with index corresponding to
                the order of facilities in the original to_list
    """
    # the coordinate pair come in the form of: (longitude. latitude)
    coordinate_str = str(source_lon) + ',' + str(source_lat)
    for destination in to_list:
        coordinate_str += ';' + str(destination[0]) + ',' + str(destination[1])
    token = """pk.eyJ1IjoicGFydmF0aHlrcmlzaG5hbmsiLCJhIjoiY2tybGFoMTZwMGJjdDJybnYyemwxY3QxMSJ9.FXaVYsMF3HIzw7ZQFQPhSw"""
    # Mapbox API is used with max of 10 coordinates per request
    # maximum is 30 request per minute
    # coordinate request is in the form of : /lon1, lat1;lon2, lat2;.../
    # one can use the parameter {sources} to point which coordinate pair is
    # the destination to reduce request time
    # same can be said about {destination}
    request_url = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving/"
    request_params = """?annotations=duration&sources=0&access_token="""
    request_mapbox = request_url + coordinate_str + request_params + token
    try:
        request_pack = json.loads(requests.get(request_mapbox).content)
        if 'messsage' in request_pack.keys():
            if request_pack['durations'] == "Too Many Requests":
                print('Use too many at ' + str(datetime.today()))
                return False
        duration_minutes = request_pack['durations'][0][1:]
        return duration_minutes
    except Exception as e:
        print(e)
        # I did a blind try-except
        # since I dont know which error might come from the MapBox API
        # either they dont have the calculation
        # or the token has reached its minutely limit
        return False


def record_result(res_list: tuple):
    """
    record the result into mysql db to preserve data
    :param res_list: the tuple of the queried result. It must contain these:
        - Time of request: DATE
        - Coordinates: list of (lon, lat) saved in TEXT
        - min_drive: the quickest driving time for the point
    :return:
    """
    mydb = open_connection()
    cursor = mydb.cursor()
    insert_query = """  INSERT INTO isochrone(req_time, source_point, min_drive) 
                        VALUES(%s ,%s ,%s)"""
    cursor.execute(insert_query, res_list)
    mydb.commit()
    cursor.close()
    mydb.close()
    return


def return_closest_facs(source_lon, source_lat, facs_df, facs_return):
    """
    Return the closest 45 facilities in haversine distance.
    The returned df is sort ascendingly
    :param source_lon: longitude of the source GPS
    :param source_lat: latitude of the source GPS
    :param facs_df: facilities df
    :param facs_return
    :return:
    """
    res_df = deepcopy(facs_df)
    harv_dist = np.zeros(res_df.shape[0], dtype=float)
    for i in range(len(harv_dist)):
        dest_lon = res_df['Lon'].iloc[i]
        dest_lat = res_df['Lat'].iloc[i]
        harv_dist[i] = haversine_vectorize(source_lon, source_lat, dest_lon,
                                           dest_lat)
    res_df['Harversine_Dist'] = harv_dist
    res_df.sort_values('Harversine_Dist', inplace=True)
    res_df.reset_index(inplace=True, drop=True)
    return res_df.iloc[:facs_return, :]


def simulation_core(coord_pair, remain_time, req_count, facs_df: pd.DataFrame,
                    facs_return):
    """
    Core part of the simulation. It requests the driving-time API
     and calculate result. This would later become the core for the main API
    :param coord_pair: code name of the province
    :param remain_time: province df
    :param req_count: abc
    :param facs_df: facilities df
    :param facs_return
    :return:
        - final_drive_res: str of the list of the driving time from the source
                            to the 45 closest facilities
        - final_request_time: str of the list of the request time from
                                MapBox API
        - str of the coordinates for the source GPS
        - harv_dist_str: str of the list of the harvesine distances
                        from the source to 45 closest facilities
    """
    start_time = datetime.now()
    gps_lon, gps_lat = coord_pair

    # data preparation for the facilities list
    facs_df_45 = return_closest_facs(gps_lon, gps_lat, facs_df, facs_return)
    facs_list = facs_df_45[['Lon', 'Lat']].to_numpy().tolist()

    final_drive_res = []
    coord_per_req = max_coord_req - 1
    num_req = math.ceil(facs_return / coord_per_req)
    for i in range(num_req):
        start_idx = i * coord_per_req
        end_idx = (i + 1) * coord_per_req
        # the queried_res come in the form of list of drive time in seconds
        # with corresponding index with the facilities
        while True:
            if req_count >= max_req_min:
                time.sleep(remain_time)
            queried_res = travel_time_req(gps_lon, gps_lat,
                                          facs_list[start_idx: end_idx])
            end_time = datetime.now()
            cost_time = (end_time - start_time).total_seconds()
            # here is to capture the case of failed connection
            # and limited access from Mapbox API
            if queried_res:
                remain_time -= cost_time
                break
            else:
                remain_time = 60
                req_count = 0
                time.sleep(remain_time)
        # add to list
        final_drive_res += queried_res
    # remove unnecessary comma and data prep before returning result
    min_drive = min(final_drive_res)
    req_count += 1
    return min_drive, req_count, remain_time


def main():
    """
    Main simulation function
    :return: None
    """
    coord_df = pd.read_csv('./Data/iso_chrone.csv')
    stroke_facs = pd.read_csv('./Data/stroke_facs_latest.csv')
    stroke_facs = deepcopy(stroke_facs[['Name_English',
                                        'longitude', 'latitude']])
    stroke_facs.columns = ['Facility_Name', 'Lon', 'Lat']
    number_of_simulation = coord_df.shape[0]

    req_count = 0
    curr_cost = 0
    # I can send 30 requests with 9 stroke centres each request
    # thus, for each minute, I can simulate 6 GPS points at the same time
    # roughly, since I will not try to do multithreading,
    # it will all be sequential request
    for idx in tqdm(range(number_of_simulation)):
        curr_pair = coord_df.iloc[idx, :]
        time_of_req = datetime.now()
        min_drive, req_count, curr_cost = simulation_core(curr_pair,
                                                          curr_cost,
                                                          req_count,
                                                          stroke_facs,
                                                          48)
        start_time = datetime.now()
        source_point = str(curr_pair[0]) + ',' + str(curr_pair[1])
        record_result((time_of_req, source_point, str(min_drive)))
        end_time = datetime.now()
        # cost time is used to control if we have reached the
        # maximum request per minute set out by MapBox or not
        curr_cost += (end_time - start_time).total_seconds()
        if curr_cost >= 60 and req_count <= max_req_min:
            curr_cost = curr_cost - 60
            req_count = 0
        elif req_count >= max_req_min and curr_cost < 60:
            time.sleep(60 - curr_cost)
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
    # stroke_facs = deepcopy(stroke_facs[['Name_English', 'longitude',
    #                                     'latitude',
    #                                     'pro_name_e', 'dist_name_e']])
    # stroke_facs.columns = ['Facility_Name', 'Lon', 'Lat',
    #                        'Province', 'District']
    #
    # start = datetime.today()
    # print(start)
    # temp = return_closest_45(temp[0], temp[1], stroke_facs)
    # end = datetime.now()
    # print((end - start).microseconds)
    # temp = travel_time_req(-122.42, 37.78,
    #                        [[-122.45, 37.91], [-122.48, 37.73]])

    # start = datetime.now()
    # temp, a, b, c = sth('VNM.8_1',
    #                     edges[['GID_1', 'NAME_1', 'geometry']],
    #                     stroke_facs)
    # end = datetime.now()
    # print((end - start))
    # print(temp)
    # print(a)
    # print(b)
    # print(c)
    # pass
    # AND HERE IS THE MAIN SIMULATION
    # vn_prov = gpd.read_file('./Data/gadm_vietnam.geojson')
    # vn_bound = vn_prov.geometry.unary_union
    # random_gps(vn_bound)
    main()
