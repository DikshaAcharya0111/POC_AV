import duckdb
import json
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Polygon

parquet_input = r"C:\\Work\\github\\POC_AV\\data\\fixpunkte-lfp1_2056_5728.gdb\\FIDA.parquet"
glarus_sud_json = Path(r"C:\Work\github\POC_AV\data\Glarus_sud.json")
query_OUT = Path(r"C:\\Work\\github\\POC_AV\\data\\fixpunkte-lfp1_2056_5728.gdb") / "query.json"
query_OUT.parent.mkdir(parents=True, exist_ok=True)

with open(glarus_sud_json, "r", encoding="utf-8") as f:
    geojson = json.load(f)

rings = geojson["features"][0]["geometry"]["rings"]
glarus_polygon = Polygon([(pt[0], pt[1]) for pt in rings[0]])

# with point number
con = duckdb.connect()
df = con.execute(f"SELECT * FROM read_parquet('{parquet_input}')").df()
print(df.columns.tolist())

NBINDNENT = con.execute(f"""
    SELECT DISTINCT NBIDENT 
    FROM read_parquet('{parquet_input}')
    ORDER BY NBIDENT
""").df()
print(f"NBINDNENT: {NBINDNENT}")

result = con.execute(f"""
    SELECT *
    FROM read_parquet('{parquet_input}')
    WHERE NBIDENT IN ('CH0300001174', 'CH0300001173')
""").df()

print(result.to_string())

# with polygone
con = duckdb.connect()
con.install_extension("spatial")
con.load_extension("spatial")

df = con.execute(f"""
    SELECT *
    FROM read_parquet('{parquet_input}')
""").df()

print(f"Total points: {len(df)}")

## spatial filter
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.GeoSeries.from_wkb(df["geometry"]),
    crs="EPSG:2056"
)

result = gdf[gdf.geometry.within(glarus_polygon)]
print(f"Found {len(result)} points inside Glarus Süd")

result.to_crs("EPSG:4326").to_file(query_OUT, driver="GeoJSON")
print(f"Saved to {query_OUT}")