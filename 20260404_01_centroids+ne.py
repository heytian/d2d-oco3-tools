#%%

# 20260404
# Step 1: Adding city names and population from Natural Earth data to clasp report centroid csv

import pandas as pd
from shapely import wkt
from sklearn.neighbors import BallTree
import numpy as np

targets = pd.read_csv('datasource/clasp_report_379cities.csv') # replace with local path
cities = pd.read_csv('datasource/ne_10m_populated_places.csv') # replace with local path

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

targets['City'] = cities.iloc[flat]['NAMEASCII'].values
targets['Country'] = cities.iloc[flat]['ADM0NAME'].values
targets['Population'] = cities.iloc[flat]['POP_MAX'].values

output_path = "./output/csv/"
targets.to_csv(output_path+'clasp_report_379cities_plus_v2.csv', index=False)

#%%

