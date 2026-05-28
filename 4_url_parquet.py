import duckdb
import json
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Polygon

parquet_url = "https://data.geo.admin.ch/ch.swisstopo.swisseo_vhi_v100/1991-12-01t235959/ch.swisstopo.swisseo_vhi_v100_1991-12-01t235959_forest-warnregions.parquet"
polygone_json = Path(r"C:\\Work\\github\\POC_AV\\data\\polygone\\Glarus_Sd.json")
query_OUT = Path(r"C:\\Work\\github\\POC_AV\\data\\fixpunkte-lfp1_2056_5728.gdb") / "query_intersect.json"
query_OUT.parent.mkdir(parents=True, exist_ok=True)

# Bbox of polygone
with open(polygone_json, "r", encoding="utf-8") as f:
    geojson = json.load(f)

rings = geojson["features"][0]["geometry"]["rings"]
glarus_polygon = Polygon([(pt[0], pt[1]) for pt in rings[0]])

# Get bounding box for DuckDB SQL filter
minx, miny, maxx, maxy = glarus_polygon.bounds
print(f"Bounding box: {minx}, {miny}, {maxx}, {maxy}")

# DuckDb query
print("Connecting DuckDB")
con_DuckDB = duckdb.connect()
con_DuckDB.execute("LOAD httpfs;")

# Inspect schema before writing your WHERE clause
schema = con_DuckDB.execute(f"""
    DESCRIBE SELECT * FROM read_parquet('{parquet_url}') LIMIT 1
""").df()
print(schema)

