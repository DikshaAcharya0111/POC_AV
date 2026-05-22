import geopandas as gpd
from pathlib import Path
import fiona

gdb_PATH    = r"C:\\Work\\github\\POC_AV\\data\\fixpunkte-lfp1_2056_5728.gdb\\FIDA.gdb"
parquet_OUT = Path(r"C:\\Work\\github\\POC_AV\\data\\fixpunkte-lfp1_2056_5728.gdb") / "FIDA.parquet"
parquet_OUT.parent.mkdir(parents=True, exist_ok=True)

# Read gdb
gdf = gpd.read_file(gdb_PATH)
print(fiona.listlayers(gdb_PATH))

# Convert
gdf.to_parquet(parquet_OUT)

# Print schema from the Parquet file
gdf_parquet = gpd.read_parquet(parquet_OUT)
print("Columns and types:")
print(gdf_parquet.dtypes)

print("\nCRS (coordinate system):")
print(gdf_parquet.crs)

print("\nBounding box:")
print(gdf_parquet.total_bounds) 

print("\nGeometry types:")
print(gdf_parquet.geometry.geom_type.value_counts())

print("\nFirst few row:")
print(gdf_parquet.head(10))

print("\nOne example per column:")
for col in gdf_parquet.columns:
    print(f"  {col}: {gdf_parquet[col].iloc[0]}")
# Prochaine étape: stocker dans stac s'il faut...

