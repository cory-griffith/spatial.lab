import arcpy
import os
import datetime
import pandas as pd

# --- Setup ---
arcpy.env.overwriteOutput = True

# Paths
sde_conn = r"P:\Arcdata\ArcMap\Scripts\zzDatabase_Connections\X.sde"
input_fc = os.path.join(sde_conn, r"X.DBO.Street_Network\X.DBO.e911roads")
aprx_gdb = r"P:\Arcdata\ArcMap\APRX\APRX.gdb"
output_fc = os.path.join(aprx_gdb, "MapBookRoadRoster_DISS")
output_folder = r"P:\Arcdata\Addressing\New Roads\zRoad Rosters"

# Temporary layer
filtered_layer = "e911roads_filtered"
where_clause = r"""
STREET NOT IN ('UNNAMED ST', 'XOVER')
AND CLASS NOT IN (98, 99)
"""
arcpy.management.MakeFeatureLayer(input_fc, filtered_layer, where_clause)

# Dissolve
arcpy.management.Dissolve(
    in_features=filtered_layer,
    out_feature_class=output_fc,
    dissolve_field=["STREET", "ROUTENUM", "CLASS"],
    multi_part="MULTI_PART"
)

# Add MILES field
arcpy.management.AddField(output_fc, "MILES", "DOUBLE")
arcpy.management.CalculateField(
    output_fc,
    "MILES",
    "!SHAPE.length@feet! / 5280",
    expression_type="PYTHON3"
)

# Add LOW and HIGH fields
arcpy.management.AddField(output_fc, "LOW", "LONG")
arcpy.management.AddField(output_fc, "HIGH", "LONG")

# Create lookup for LOW and HIGH from filtered_layer (read-only, does not change source)
low_high_dict = {}
fields = ["STREET", "ROUTENUM", "CLASS", "LLO", "RLO", "LHI", "RHI"]

with arcpy.da.SearchCursor(filtered_layer, fields) as cursor:
    for street, route, cls, llo, rlo, lhi, rhi in cursor:
        key = (street, route, cls)
        lows = [v for v in (llo, rlo) if v is not None]
        highs = [v for v in (lhi, rhi) if v is not None]
        if key not in low_high_dict:
            low_high_dict[key] = {"low": [], "high": []}
        low_high_dict[key]["low"].extend(lows)
        low_high_dict[key]["high"].extend(highs)

# Update dissolved with LOW and HIGH
with arcpy.da.UpdateCursor(output_fc, ["STREET", "ROUTENUM", "CLASS", "LOW", "HIGH"]) as cursor:
    for row in cursor:
        key = (row[0], row[1], row[2])
        if key in low_high_dict:
            lows = low_high_dict[key]["low"]
            highs = low_high_dict[key]["high"]
            row[3] = min(lows) if lows else None
            row[4] = max(highs) if highs else None
            cursor.updateRow(row)

# --- Build DataFrame directly from dissolved FC (no CSV hop) ---

# Get all non-OID, non-geometry fields
fields_for_df = [
    f.name for f in arcpy.ListFields(output_fc)
    if f.type not in ("OID", "Geometry")
]

data = []
with arcpy.da.SearchCursor(output_fc, fields_for_df) as cursor:
    for row in cursor:
        data.append(row)

df = pd.DataFrame(data, columns=fields_for_df)

# Drop unwanted fields if they exist
fields_to_drop = [col for col in ["OID_", "Shape_Length"] if col in df.columns]
if fields_to_drop:
    df.drop(columns=fields_to_drop, inplace=True)

# Ensure MILES is a float and round to 3 decimal places
if "MILES" in df.columns:
    df["MILES"] = pd.to_numeric(df["MILES"], errors="coerce").round(3)

# Create XLSX filename and write to Excel
today_str = datetime.datetime.today().strftime("%Y%m%d")
xlsx_filename = "Local Road Roster - {0}.xlsx".format(today_str)
xlsx_path = os.path.join(output_folder, xlsx_filename)

df.to_excel(xlsx_path, index=False)

# Cleanup: delete temporary dissolved FC
arcpy.management.Delete(output_fc)

# Remove temporary layer from the map
aprx = arcpy.mp.ArcGISProject("CURRENT")
for m in aprx.listMaps():
    for lyr in m.listLayers():
        if lyr.name == filtered_layer:
            m.removeLayer(lyr)
            break

print("Script completed successfully.")
print("Excel file saved to:", xlsx_path)