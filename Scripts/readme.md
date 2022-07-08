# Scripts
This folder includes all the Python Scripts required to execute and test the different functionalities of the Geospatial Planning and Budgeting Platform

- Population/Facilities
  - Calculating raster statistics within a Polygon
  - Calculating vector point stats within a Polygon
  - Health Catchment Area Calculation with Mapbox
  - Health Cachment Area Calculation with Road Network Data
  
- Road Network Data
  - [Converting road vector in shapefile or geojson format into a Pandana network for accessibility analytics](https://github.com/parvathykrishnank/gpbp/blob/39b54b9ab8355483b6debb807a684b67c64316a8/Scripts/network_gpbp.py) 
  
- Accessibility Analytics
  - [Haversine vectorise for calculating haversine distance between lat-lon pairs](https://github.com/parvathykrishnank/gpbp/blob/2fb6a8e3b1d07c92b25987e6eb3d64f1752a77af/Scripts/haversine_vectorize.py)
  - [Distance matrix calculation](https://github.com/parvathykrishnank/gpbp/blob/b1744dbb03528d1b9226fec9da74c85eb4808ca5/Scripts/distance_matrix.py) with contraction hierarchies in Python using [Pandana](https://udst.github.io/pandana/network.html)

- Optimization Algorithm
  - Creating a grid of n\*n km within a polygon  
  - [Gurobi optimization model](https://github.com/parvathykrishnank/gpbp/blob/cf3597a73cf18bca1ac2477df87f40c7cda32cc4/Scripts/optimization_model.py)

