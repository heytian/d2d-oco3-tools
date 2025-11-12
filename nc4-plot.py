import os
import xarray as xr
import s3fs
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import rasterio
from rasterio.transform import from_bounds

fs = s3fs.S3FileSystem(anon=False)
files = fs.ls("gesdisc-cumulus-prod-protected/OCO3_DATA/OCO3_L2_Lite_FP.11r/2024")
print(files[:5])  # just preview first 5


# # Output switches
# SAVE_CSV = True       # Save CSV of variables
# SAVE_GEOTIFF = True   # Save gridded GeoTIFF
# SAVE_PNG = True       # Save preview plot

# # Variables to extract for CSV
# CSV_VARS = ["xco2", "latitude", "longitude", "time"]
# GEO_VARS = "xco2"  # Variable to grid for GeoTIFF/PNG

# # Fixed geographic extent (lon_min, lat_min, lon_max, lat_max)
# FIXED_EXTENT = (-120, 32, -116, 36) # for LA  -120, 32, -116, 36
# OUT_WIDTH, OUT_HEIGHT = 360, 180  # grid resolution

# # Output folders
# OUTPUT_DIR = "../output"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # List of S3 NC4 files
# S3_FILES = [
#     "s3://gesdisc-cumulus-prod-protected/OCO3_DATA/OCO3_L2_Lite_FP.11r/2024/oco3_LtCO2_240716_B11072Ar_241126004045s.nc4",
#     # "s3://gesdisc-cumulus-prod-protected/OCO3_DATA/OCO3_L2_Lite_FP.11r/2024/oco3_LtCO2_240716_B11072Ar_241126004045s.nc4"
#     # Add more NC4 links
# ]

# # fs = s3fs.S3FileSystem(key=EARTHDATA_USER, secret=EARTHDATA_TOKEN,client_kwargs={"region_name": "us-west-2"})
# # print(f"Using user: {EARTHDATA_USER}, token set? {EARTHDATA_TOKEN is not None}")

# # -------------------------
# # PROCESS FUNCTION
# # -------------------------
# def process_nc4_file(s3_path):
#     filename = os.path.basename(s3_path)
#     csv_name = os.path.join(OUTPUT_DIR, filename.replace(".nc4", ".csv"))
#     tiff_name = os.path.join(OUTPUT_DIR, filename.replace(".nc4", ".tif"))
#     plot_name = os.path.join(OUTPUT_DIR, filename.replace(".nc4", ".png"))

#     try:
#         with fs.open(s3_path, "rb") as f:
#             ds = xr.open_dataset(f)

#             # -------------------------
#             # CSV OUTPUT
#             # -------------------------
#             if SAVE_CSV:
#                 csv_vars_available = [v for v in CSV_VARS if v in ds.variables]
#                 df = ds[csv_vars_available].to_dataframe().reset_index()
#                 df.to_csv(csv_name, index=False)
#                 print(f"✅ Saved CSV: {csv_name}")

#             # -------------------------
#             # GEO & PNG OUTPUT
#             # -------------------------
#             if SAVE_GEOTIFF or SAVE_PNG:
#                 if not all(v in ds.variables for v in ['latitude','longitude',GEO_VARS]):
#                     raise ValueError(f"Required variables not found in {filename}")

#                 lat = ds['latitude'].values
#                 lon = ds['longitude'].values
#                 data = ds[GEO_VARS].values

#                 # Bin data onto fixed grid
#                 lat_bins = np.linspace(FIXED_EXTENT[1], FIXED_EXTENT[3], OUT_HEIGHT)
#                 lon_bins = np.linspace(FIXED_EXTENT[0], FIXED_EXTENT[2], OUT_WIDTH)
#                 grid_data, _, _ = np.histogram2d(
#                     lat.flatten(), lon.flatten(),
#                     bins=[lat_bins, lon_bins],
#                     weights=data.flatten()
#                 )
#                 counts, _, _ = np.histogram2d(lat.flatten(), lon.flatten(),
#                                               bins=[lat_bins, lon_bins])
#                 grid_data = np.divide(grid_data, counts, out=np.zeros_like(grid_data), where=counts!=0)

#                 # -------------------------
#                 # GeoTIFF
#                 # -------------------------
#                 if SAVE_GEOTIFF:
#                     transform = from_bounds(FIXED_EXTENT[0], FIXED_EXTENT[1],
#                                             FIXED_EXTENT[2], FIXED_EXTENT[3],
#                                             OUT_WIDTH, OUT_HEIGHT)
#                     with rasterio.open(
#                         tiff_name,
#                         'w',
#                         driver='GTiff',
#                         height=grid_data.shape[0],
#                         width=grid_data.shape[1],
#                         count=1,
#                         dtype=grid_data.dtype,
#                         crs="EPSG:4326",
#                         transform=transform
#                     ) as dst:
#                         dst.write(grid_data, 1)
#                     print(f"Saved GeoTIFF: {tiff_name}")

#                 # -------------------------
#                 # PNG Preview
#                 # -------------------------
#                 if SAVE_PNG:
#                     plt.figure(figsize=(12,6))
#                     plt.imshow(grid_data, extent=FIXED_EXTENT, origin='lower', cmap='viridis', aspect='auto')
#                     plt.colorbar(label=GEO_VARS)
#                     plt.xlabel("Longitude")
#                     plt.ylabel("Latitude")
#                     plt.title(filename)
#                     plt.savefig(plot_name, bbox_inches='tight')
#                     plt.close()
#                     print(f"Saved PNG plot: {plot_name}")

#     except Exception as e:
#         print(f"Failed {s3_path}: {e}")

# # -------------------------
# # LOOP OVER FILES
# # -------------------------
# for s3_file in S3_FILES:
#     process_nc4_file(s3_file)
