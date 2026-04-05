import geopandas as gpd
import pandas as pd
from shapely import wkt
import numpy as np
from geodatasets import get_path

merged = pd.read_csv("./output/csv/c40cities-co2-em-conc-wkt.csv")

world=gpd.read_file(get_path("naturalearth.land"))
coastlines=world.boundary

city_gdf = gpd.GeoDataFrame(
    merged[["city", "wkt_center"]].dropna(subset=["wkt_center"]),
    geometry=merged["wkt_center"].dropna().apply(wkt.loads),
    crs="EPSG:4326"
)

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

merged = merged.merge(
    city_gdf[["city", "coastal_km", "is_coastal"]],
    on="city", how="left"
)

output_path = "./output/csv/"
merged.to_csv(output_path+"c40cities-co2-em-conc-wkt-coast.csv", index=False)
