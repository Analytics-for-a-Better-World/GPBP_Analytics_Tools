from flask import json
import requests
from datetime import datetime
from shapely.geometry import Polygon, MultiPolygon
import geopandas as gpd
from shapely.ops import cascaded_union
from shapely import wkt

vn_prov = gpd.read_file('./Data/gadm_vietnam.geojson')
vn_bound = vn_prov.geometry.unary_union
time_frame = [20, 40, 60, 90, 120, 150, 180, 210, 240, 300, 360]


def iso_req(coor_pair: str, req_min: int):
    # 300 requests per minute
    token = """pk.eyJ1IjoicGFydmF0aHlrcmlzaG5hbmsiLCJhIjoiY2tybGFoMTZwMGJjdDJybnYyemwxY3QxMSJ9.FXaVYsMF3HIzw7ZQFQPhSw"""
    request_url = """https://api.mapbox.com/isochrone/v1/mapbox/driving/"""
    # after the request URL, add the coordinates and isochrone's rule
    # {coordinates}?{contours_minutes|contours_meters}
    time_param = '?contours_minutes=' + str(req_min)
    # to be added the last
    token_param = "&polygons=true&generalize=100.0&denoise=1.0&access_token="
    req_iso = request_url + coor_pair + time_param + token_param + token
    request_pack = json.loads(requests.get(req_iso).content)
    if 'features' not in request_pack.keys():
        print('Failed at' + str(datetime.today()))
        return False
    poly_geo = request_pack['features'][0]['geometry']
    iso_poly = Polygon(poly_geo['coordinates'][0])
    return iso_poly


def in_vn_check(poly: Polygon):
    if vn_bound.contains(poly):
        return poly
    return vn_bound.intersection(poly)


if __name__ == '__main__':
    a = 1
    hosp_1 = iso_req('105.496,21.117', 60)
    hosp_2 = iso_req('105.790, 21.051', 60)
    polygons = [hosp_1, hosp_2]
    boundary = cascaded_union(polygons)
    if isinstance(boundary, MultiPolygon):
        boundaries = list(boundary.geoms)
    # this is for rounding
    boundary = wkt.loads(wkt.dumps(boundary, rounding_precision=2))
    # this is for taking the exterior coordinate
    x, y = boundary.exterior.xy
    new_group = list(set(zip(x, y)))
    # this is for taking the interiors' coordinate
    temp = [x.coords for x in boundary.interiors]
    pass
