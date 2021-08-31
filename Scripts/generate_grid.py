def generate_grid_in_polygon(spacing, polygon):
    import numpy as np
    from shapely.geometry import Point,Polygon
    from shapely.ops import cascaded_union
    import geopandas as gpd
    ''' This Function generates evenly spaced points within the given GeoDataFrame.
        The parameter 'spacing' defines the distance between the points in coordinate units. '''
    # Convert the GeoDataFrame to a single polygon
    poly_in = cascaded_union([poly for poly in polygon.geometry])
    # Get the bounds of the polygon
    minx, miny, maxx, maxy = poly_in.bounds    
    # Square around the country with the min, max polygon bounds
    # Now generate the entire grid
    x_coords = list(np.arange(np.floor(minx), int(np.ceil(maxx)), spacing))
    y_coords = list(np.arange(np.floor(miny), int(np.ceil(maxy)), spacing))
    grid = [Point(x) for x in zip(np.meshgrid(x_coords, y_coords)[0].flatten(), np.meshgrid(x_coords, y_coords)[1].flatten())]
    grid_df = gpd.GeoDataFrame(grid)
    grid_df.columns = ['geometry']
    grid_df = grid_df.set_crs(epsg=3763)
    
    extracted_grid = gpd.clip(grid_df, polygon)
    extracted_grid1 = extracted_grid.to_crs(epsg=4326)
    return (extracted_grid1)