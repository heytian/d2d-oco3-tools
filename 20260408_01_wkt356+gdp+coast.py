#%%

# 20260408 Building up data set for 300+ cities
# Step 1: Adding World Bank's GDP per capita data (for 266 countries) to clasp report centroid csv (356sam version that has Natural Earth city population added)
# pro-rated GDP by population of each city

import pandas as pd
from shapely import wkt
from sklearn.neighbors import BallTree
import numpy as np
import geopandas as gpd
from geodatasets import get_path

# data sources; replace with local path
targets = pd.read_csv('datasource/clasp_report_356sams-pop-gdp-edit.csv')
cities = pd.read_csv('datasource/ne_10m_populated_places.csv')
gdp = pd.read_csv('datasource/worldbank-gdpcapita.csv')

#%%
# add 3-letter country code from ne to claspreport to prepare for join with worldbank gdp data
def parse_wkt_point(wkt_str):
    try:
        geom = wkt.loads(wkt_str)
        return geom.x, geom.y
    except:
        return None, None

targets[['lon', 'lat']] = targets['Site Center WKT'].apply(
    lambda x: pd.Series(parse_wkt_point(x))
)

ne_coords_rad = np.radians(cities[['LATITUDE', 'LONGITUDE']].values)
tree = BallTree(ne_coords_rad, metric='haversine')

target_coords_rad = np.radians(targets[['lat', 'lon']].values)
_, idx = tree.query(target_coords_rad, k=1)
flat = idx.flatten()

targets['countrycode'] = cities.iloc[flat]['SOV_A3'].values

targets = targets.merge(
    gdp[['Country Code', '2024']],
    left_on='countrycode',
    right_on='Country Code',
    how='left'
)

#%%
# pro-rated city population
targets['gdp_bil_usd'] = ((targets['population'] * targets['2024']) / 1000000000)

#%%
# add coastal city variable
world=gpd.read_file(get_path("naturalearth.land"))
coastlines=world.boundary

# city_gdf = gpd.GeoDataFrame(
#     targets[["city", "Site Center WKT"]].dropna(subset=["Site Center WKT"]),
#     geometry=targets["Site Center WKT"].dropna().apply(wkt.loads),
#     crs="EPSG:4326"
# )

city_gdf = gpd.GeoDataFrame(
    targets[["city", "Site Center WKT", "Target ID"]].dropna(subset=["Site Center WKT"]),
    geometry=targets["Site Center WKT"].dropna().apply(wkt.loads),
    crs="EPSG:4326",
    index=targets[targets["Site Center WKT"].notna()].index  # ← Preserve original index
)

city_gdf["Target ID"] = targets[targets["Site Center WKT"].notna()]["Target ID"].values


city_gdf    = city_gdf.to_crs("EPSG:3857")
coastlines  = coastlines.to_crs("EPSG:3857")
coast_union = coastlines.union_all()

city_gdf["coastal_km"] = city_gdf.geometry.apply(
    lambda pt: pt.distance(coast_union) / 1000
)

city_gdf["is_coastal"] = city_gdf["coastal_km"] < 50

# diagnostic: should see near-0 for coastal, large values for inland
print(city_gdf[["city", "coastal_km", "is_coastal"]]
      .sort_values("coastal_km")
      .to_string(index=False))

# targets = targets.merge(
#     city_gdf[["geometry", "coastal_km", "is_coastal"]].reset_index(),
#     left_on="Site Center WKT",
#     right_on="geometry",
#     how="left"
# )

targets = targets.merge(
    city_gdf[["Target ID", "coastal_km", "is_coastal"]],
    on="Target ID",
    how="left"
)

output_path = "./output/csv/"
targets.to_csv(output_path+'clasp_report_356sams-pop-gdp-coast.csv', index=False)

#%%

#diagnostic for issue of targets becoming 412 instead of 356 after coastal operation

# Quick diagnostic:
print(targets.shape)
print(targets['Target ID'].nunique())  # Should equal number of rows if no duplicates
print(targets[targets.duplicated(subset=['Target ID'], keep=False)].sort_values('Target ID'))

# %%
