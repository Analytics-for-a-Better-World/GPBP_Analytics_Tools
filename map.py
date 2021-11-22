import plotly.express as px
import pandas as pd
import folium
import geopandas as gpd


vn_prov = gpd.read_file('./Data/gadm_vietnam.geojson')
vn_prov.explore()

