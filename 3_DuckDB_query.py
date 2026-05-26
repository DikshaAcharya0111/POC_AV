import duckdb
import json
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Polygon

parquet_input = r"C:\\Work\\github\\POC_AV\\data\\fixpunkte-lfp1_2056_5728.gdb\\FIDA.parquet"
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
#con.install_extension("spatial")
#con.load_extension("spatial")
# df = con.execute(f"""
#     SELECT *
#     FROM read_parquet('{parquet_input}')
# """).df()
#print(f"Total points: {len(df)}")

result_DB = con_DuckDB.execute(f"""
    SELECT *
    FROM read_parquet('{parquet_input}')
    WHERE CAST(E95 AS DOUBLE) BETWEEN {minx} AND {maxx}
    AND   CAST(N95 AS DOUBLE) BETWEEN {miny} AND {maxy}
""").df()

print(f"Points in bounding box: {len(result_DB)}")

## spatial filter in gpd
gdf = gpd.GeoDataFrame(
    result_DB,
    geometry=gpd.GeoSeries.from_wkb(result_DB["geometry"].apply(bytes)),
    crs="EPSG:2056"
)

LFP1_polygon = gdf[gdf.geometry.intersects(glarus_polygon)]
print(f"Found {len(result_DB)} points inside Glarus Süd")

# save json file 
LFP1_polygon.to_crs("EPSG:4326").to_file(query_OUT, driver="GeoJSON")
print(f"Saved to {query_OUT}")

# Print each feature's NBIDENT and PUNKTNAME
with open(query_OUT, "r", encoding="utf-8") as f:
    geojson = json.load(f)

print(f"Number of features in JSON: {len(geojson['features'])}")

for i, feature in enumerate(geojson["features"]):
    props = feature["properties"]
    print(f"  {i+1}. NBIDENT: {props['NBIDENT']} | PUNKTNAME: {props['PUNKTNAME']}")

final = LFP1_polygon.drop_duplicates(subset=["NBIDENT", "NUMMER"])
print(f"After removing duplicates: {len(final)} points")

# Check all 7 bbox points against the polygon
for idx, row in gdf.iterrows():
    point = row.geometry
    print(f"{row['PUNKTNAME']:20} | within: {point.within(glarus_polygon)} | covered_by: {point.covered_by(glarus_polygon)} | intersects: {point.intersects(glarus_polygon)}")