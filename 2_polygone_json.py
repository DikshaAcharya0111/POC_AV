### -----------------------------------------------------------------
# Extract polygone from lyrx to json file
### -----------------------------------------------------------------

import arcpy
from pathlib import Path
import json
import re

input_polygone = r"C:\\Work\\github\\POC_AV\\data\\MOPUBLIC_MANAGER.TB_Municipal_boundary.lyrx"
output_dir = Path(r"C:\\Work\\github\\POC_AV\\data\\polygone")
commune    = "Glarus Süd"

safe_name   = commune.replace(" ", "_")
safe_name   = re.sub(r'[\\/:*?"<>|]', "", safe_name)
safe_name = safe_name.encode("ascii", "ignore").decode()
# take commune name
output_json = output_dir / f"{safe_name}.json"     

# input layer 
lyr_file = arcpy.mp.LayerFile(input_polygone)
lyr      = lyr_file.listLayers()[0]

# selection of polygone
features = []

with arcpy.da.SearchCursor(lyr, ["NAME", "SHAPE@JSON"], where_clause=f"NAME = '{commune}'") as cursor:
    for row in cursor:
        features.append({
            "type": "Feature",
            "properties": {
                "name": row[0]
            },
            "geometry": json.loads(row[1])   
        })

# output json
geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

print(f"Exported {len(features)} feature(s) to {output_json}")