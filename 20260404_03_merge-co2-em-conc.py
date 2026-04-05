
# Step 3: merging Ahn et al 2025 emissions with OCO3 data for 53 cities
# done twice (20260404 as Step 3 & 20260402)

#%%
import pandas as pd
import numpy as np

# Parquet source notes:
# 20260404: parquets are outputs from 20260404_02_updateDuckDB.ipynb in this same repo
# 20260402: parquest used are outputs from nc4-timezone-pop.ipynb (first round of netcdf-to-parquet) in this same repo
co2 = pd.read_parquet("./datasource/co2_sam.parquet") # path to CO2 parquet
sif = pd.read_parquet("./datasource/sif_sam.parquet") # path to SIF parquet
c40emissions = pd.read_csv("./datasource/Ahn_etal_2025_c40_emissions.csv", sep=",") # path to CO2 emissions data

co2["datetime"] = pd.to_datetime(co2["datetime"])
sif["datetime"] = pd.to_datetime(sif["datetime"])
# because Annual CO2 emissions estimated using OCO-3 v11 data from 2019/09 to 2023/11
start, end = "2019-09-01", "2023-11-30"
co2 = co2[(co2["datetime"] >= start) & (co2["datetime"] <= end)]
sif = sif[(sif["datetime"] >= start) & (sif["datetime"] <= end)]

#%%

# 20260405 update: previously extracted mean CO2 conc and sif values from OCO3 data, but now to look at median instead

co2_median = (
    co2.groupby("city")["xco2"]
    .median().reset_index().rename(columns={"xco2": "xco2_ppm"})
)
sif_median = (
    sif.groupby("city")["Daily_SIF_757nm"]
    .median().reset_index().rename(columns={"Daily_SIF_757nm": "sif_757nm"})
)

merged = co2_median.merge(sif_median, on="city", how="outer")

# # diagnostic - compare median with mean
# co2_compare = (
#     co2.groupby("city")["xco2"]
#     .agg(mean="mean", median="median", std="std", n="count")
#     .reset_index()
# )
# co2_compare["co2_mean_median_diff"] = co2_compare["mean"] - co2_compare["median"]
# print(co2_compare.sort_values("co2_mean_median_diff", ascending=False).to_string(index=False))

# sif_compare = (
#     sif.groupby("city")["Daily_SIF_757nm"]
#     .agg(mean="mean", median="median", std="std", n="count")
#     .reset_index()
# )
# sif_compare["sif_mean_median_diff"] = sif_compare["mean"] - sif_compare["median"]
# print(sif_compare.sort_values("sif_mean_median_diff", ascending=False).to_string(index=False))

#%%
emissions_cols = [
    "TargetName", "Country", "TargetRegion", "Population", "GDP [billion USD]",
    "Annual CO2 Emissions, OCO-3 [MtCO2 year-1]",
    "Number of SAMs",
]
merged = merged.merge(
    c40emissions[emissions_cols],
    left_on="city", right_on="TargetName", how="left"
).drop(columns="TargetName")

PERCENTILE = 75 # adjust to your liking

em_col   = "Annual CO2 Emissions, OCO-3 [MtCO2 year-1]"
conc_col = "xco2_ppm"

em_thresh   = np.percentile(merged[em_col].dropna(),   PERCENTILE)
conc_thresh = np.percentile(merged[conc_col].dropna(), PERCENTILE)

print(f"Emissions threshold:     {em_thresh:.2f} MtCO2/yr  (p{PERCENTILE})")
print(f"Concentration threshold: {conc_thresh:.2f} ppm      (p{PERCENTILE})")

def quadrant(row):
    hi_em   = row[em_col]   > em_thresh
    hi_conc = row[conc_col] > conc_thresh
    if hi_em and not hi_conc:  return "HIGH_emissions_LOW_conc"
    if not hi_em and hi_conc:  return "LOW_emissions_HIGH_conc"
    if hi_em and hi_conc:      return "HIGH_both"
    return                            "LOW_both"

merged["quadrant"] = merged.apply(quadrant, axis=1)

print("\nQuadrant counts:")
print(merged["quadrant"].value_counts())
print("\nCities by quadrant:")
print(merged[["city", "Country", "xco2_ppm", em_col, "quadrant"]]
      .sort_values(["quadrant", em_col], ascending=[True, False])
      .to_string(index=False))

output_path = "./output/csv/"
merged.to_csv(output_path+"c40cities-co2-em-conc.csv", index=False)



