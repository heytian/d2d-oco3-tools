
import pandas as pd
import numpy as np

# These parquets are outputs from nc4-timezone-pop.ipynb in this same repo
co2 = pd.read_parquet("co2_sam.parquet") # path to CO2 parquet
sif = pd.read_parquet("sif_sam.parquet") # path to SIF parquet
c40emissions = pd.read_csv("Ahn_etal_2025_c40_emissions.csv", sep=",") # path to CO2 emissions data

co2["datetime"] = pd.to_datetime(co2["datetime"])
sif["datetime"] = pd.to_datetime(sif["datetime"])
# because Annual CO2 emissions estimated using OCO-3 v11 data from 2019/09 to 2023/11
start, end = "2019-09-01", "2023-11-30"
co2 = co2[(co2["datetime"] >= start) & (co2["datetime"] <= end)]
sif = sif[(sif["datetime"] >= start) & (sif["datetime"] <= end)]

co2_mean = (
    co2.groupby("city")["xco2"]
    .mean().reset_index().rename(columns={"xco2": "xco2_ppm"})
)
sif_mean = (
    sif.groupby("city")["Daily_SIF_757nm"]
    .mean().reset_index().rename(columns={"Daily_SIF_757nm": "sif_757nm"})
)

merged = co2_mean.merge(sif_mean, on="city", how="outer")

emissions_cols = [
    "TargetName", "Country", "TargetRegion", "Population", "GDP [billion USD]",
    "Annual CO2 Emissions, OCO-3 [MtCO2 year-1]",
    "Annual CO2 Emissions, OCO-3, 1-sig uncertainty [MtCO2 year-1]",
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

merged.to_csv("c40cities-co2-em-conc.csv", index=False)


