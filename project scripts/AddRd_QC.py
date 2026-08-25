# Creates:
#   X\Arcdata\ArcMap\APRX\APRX.gdb\CriticalDataQC\AddPt_OutRange
#   X\Arcdata\ArcMap\APRX\APRX.gdb\CriticalDataQC\RCL_Fishbone
#
# Temporary:
#   X\Arcdata\ArcMap\APRX\APRX.gdb\CriticalDataQC\RCL_Fishbone_Intersections
#   Deleted automatically at end.

import arcpy
import os
import re

arcpy.env.overwriteOutput = True

# -------------------------------------------------------------------
# Output locations
# -------------------------------------------------------------------

out_gdb = r"X\Arcdata\ArcMap\APRX\APRX.gdb"

out_dataset = os.path.join(out_gdb, "CriticalDataQC")

# -------------------------------------------------------------------
# Source feature classes
# -------------------------------------------------------------------

roads_fc = r"X\Arcdata\ArcMap\Scripts\zzDatabase_Connections\wcva_dev.sde\wcva_dev.dbo.Street_Network\wcva_dev.dbo.e911roads"

addr_fc = r"X\Arcdata\ArcMap\Scripts\zzDatabase_Connections\wcva_dev.sde\wcva_dev.dbo.Parcel_Details\wcva_dev.dbo.e911address"

# -------------------------------------------------------------------
# Output feature classes
# -------------------------------------------------------------------

out_range_fc = os.path.join(out_dataset, "AddPt_OutRange")

fishbone_fc = os.path.join(out_dataset, "RCL_Fishbone")

fishbone_x_fc = os.path.join(
    out_dataset,
    "RCL_Fishbone_Intersections"
)

# -------------------------------------------------------------------
# Road fields
# -------------------------------------------------------------------

ROAD_STREET = "street"
LLO = "llo"
LHI = "lhi"
RLO = "rlo"
RHI = "rhi"

# -------------------------------------------------------------------
# Address fields
# -------------------------------------------------------------------

ADDR_FULL = "full_address"
ADDR_NUM = "hsnum"
ADDR_UNIT = "unitnumber"

# -------------------------------------------------------------------
# Utility functions
# -------------------------------------------------------------------

def norm_street(value):

    if value is None:
        return ""

    value = str(value).upper().strip()
    value = re.sub(r"\s+", " ", value)

    return value


def to_int(value):

    try:

        if value is None:
            return None

        value = str(value).strip()

        if value == "":
            return None

        return int(float(value))

    except Exception:
        return None


def in_range(num, low, high):

    if num is None:
        return False

    if low is None:
        return False

    if high is None:
        return False

    lo = min(low, high)
    hi = max(low, high)

    return lo <= num <= hi


def get_street_from_full_address(full_addr, hsnum, unitnumber):

    if full_addr is None:
        return ""

    text = str(full_addr).upper().strip()
    text = re.sub(r"\s+", " ", text)

    unit_text = ""

    if unitnumber is not None:
        unit_text = str(unitnumber).upper().strip()

    if unit_text != "":

        # -----------------------------------------------------------
        # CASE 1
        # Unit attached directly to house number
        # Example:
        #   236C ESA LN
        # Result:
        #   236 ESA LN
        # -----------------------------------------------------------

        text = re.sub(
            r"^\s*" + re.escape(str(hsnum)) + re.escape(unit_text) + r"\s+",
            str(hsnum) + " ",
            text
        )

        # -----------------------------------------------------------
        # CASE 2
        # Fractional units
        # Example:
        #   236 1/2 ESA LN
        # Result:
        #   236 ESA LN
        # -----------------------------------------------------------

        text = re.sub(
            r"^\s*" + re.escape(str(hsnum)) + r"\s+" + re.escape(unit_text) + r"\s+",
            str(hsnum) + " ",
            text
        )

        # -----------------------------------------------------------
        # CASE 3
        # Unit at end of address
        # -----------------------------------------------------------

        patterns = [

            r"\s+STE\s+" + re.escape(unit_text) + r"$",
            r"\s+SUITE\s+" + re.escape(unit_text) + r"$",
            r"\s+APT\s+" + re.escape(unit_text) + r"$",
            r"\s+APARTMENT\s+" + re.escape(unit_text) + r"$",
            r"\s+UNIT\s+" + re.escape(unit_text) + r"$",
            r"\s+BLDG\s+" + re.escape(unit_text) + r"$",
            r"\s+BUILDING\s+" + re.escape(unit_text) + r"$",
            r"\s+#\s*" + re.escape(unit_text) + r"$",
            r"\s+" + re.escape(unit_text) + r"$"
        ]

        for pattern in patterns:
            text = re.sub(pattern, "", text).strip()

    # ---------------------------------------------------------------
    # Remove house number from beginning
    # Example:
    #   236 ESA LN -> ESA LN
    # ---------------------------------------------------------------

    if hsnum is not None:

        text = re.sub(
            r"^\s*" + re.escape(str(hsnum)) + r"\s+",
            "",
            text
        ).strip()

    text = re.sub(r"\s+", " ", text)

    return norm_street(text)

# -------------------------------------------------------------------
# Verify output dataset exists
# -------------------------------------------------------------------

if not arcpy.Exists(out_dataset):

    raise Exception(
        "Output feature dataset does not exist: {0}".format(out_dataset)
    )

# -------------------------------------------------------------------
# 1. Load roads into memory by street name
# -------------------------------------------------------------------

roads_by_street = {}

road_fields = [
    "OID@",
    "SHAPE@",
    ROAD_STREET,
    LLO,
    LHI,
    RLO,
    RHI
]

with arcpy.da.SearchCursor(roads_fc, road_fields) as rows:

    for oid, geom, street, llo, lhi, rlo, rhi in rows:

        key = norm_street(street)

        if not key:
            continue

        item = {
            "oid": oid,
            "geom": geom,
            "street": street,
            "llo": to_int(llo),
            "lhi": to_int(lhi),
            "rlo": to_int(rlo),
            "rhi": to_int(rhi)
        }

        roads_by_street.setdefault(key, []).append(item)

print("Loaded roads into memory.")

# -------------------------------------------------------------------
# 2. Create AddPt_OutRange
# -------------------------------------------------------------------

if arcpy.Exists(out_range_fc):
    arcpy.management.Delete(out_range_fc)

arcpy.management.CreateFeatureclass(
    out_path=out_dataset,
    out_name="AddPt_OutRange",
    geometry_type="POINT",
    template=addr_fc,
    spatial_reference=arcpy.Describe(addr_fc).spatialReference
)

addr_fields = [
    f.name for f in arcpy.ListFields(addr_fc)
    if f.type not in (
        "OID",
        "Geometry",
        "Blob",
        "Raster",
        "GUID",
        "GlobalID"
    )
]

insert_fields = ["SHAPE@"] + addr_fields

out_range_count = 0

with arcpy.da.InsertCursor(out_range_fc, insert_fields) as icur:

    with arcpy.da.SearchCursor(addr_fc, insert_fields) as rows:

        for row in rows:

            vals = dict(zip(addr_fields, row[1:]))

            hsnum = to_int(vals.get(ADDR_NUM))
            full_addr = vals.get(ADDR_FULL)
            unitnumber = vals.get(ADDR_UNIT)

            addr_street = get_street_from_full_address(
                full_addr,
                hsnum,
                unitnumber
            )

            candidate_roads = roads_by_street.get(addr_street, [])

            valid = False

            for road in candidate_roads:

                if in_range(hsnum, road["llo"], road["lhi"]):
                    valid = True
                    break

                if in_range(hsnum, road["rlo"], road["rhi"]):
                    valid = True
                    break

            if not valid:

                icur.insertRow(row)
                out_range_count += 1

print("Created AddPt_OutRange.")
print("Out-of-range count: {0}".format(out_range_count))

# -------------------------------------------------------------------
# 3. Create fishbone lines
# -------------------------------------------------------------------

if arcpy.Exists(fishbone_fc):
    arcpy.management.Delete(fishbone_fc)

spatial_ref = arcpy.Describe(addr_fc).spatialReference

arcpy.management.CreateFeatureclass(
    out_path=out_dataset,
    out_name="RCL_Fishbone",
    geometry_type="POLYLINE",
    spatial_reference=spatial_ref
)

arcpy.management.AddField(fishbone_fc, "ADDR_OID", "LONG")
arcpy.management.AddField(fishbone_fc, "ROAD_OID", "LONG")
arcpy.management.AddField(fishbone_fc, "FULL_ADDR", "TEXT", field_length=255)
arcpy.management.AddField(fishbone_fc, "HSNUM", "LONG")
arcpy.management.AddField(fishbone_fc, "UNITNUMBER", "TEXT", field_length=50)
arcpy.management.AddField(fishbone_fc, "STREET", "TEXT", field_length=100)
arcpy.management.AddField(fishbone_fc, "SIDE", "TEXT", field_length=10)
arcpy.management.AddField(fishbone_fc, "INTERSECTIONS", "LONG")

fishbone_count = 0

with arcpy.da.InsertCursor(
    fishbone_fc,
    [
        "SHAPE@",
        "ADDR_OID",
        "ROAD_OID",
        "FULL_ADDR",
        "HSNUM",
        "UNITNUMBER",
        "STREET",
        "SIDE",
        "INTERSECTIONS"
    ]
) as icur:

    with arcpy.da.SearchCursor(
        addr_fc,
        [
            "OID@",
            "SHAPE@",
            ADDR_FULL,
            ADDR_NUM,
            ADDR_UNIT
        ]
    ) as rows:

        for addr_oid, addr_geom, full_addr, hsnum_raw, unitnumber in rows:

            hsnum = to_int(hsnum_raw)

            if hsnum is None:
                continue

            if addr_geom is None:
                continue

            addr_street = get_street_from_full_address(
                full_addr,
                hsnum,
                unitnumber
            )

            candidate_roads = roads_by_street.get(addr_street, [])

            best = None

            for road in candidate_roads:

                side = None
                low = None
                high = None

                if in_range(hsnum, road["llo"], road["lhi"]):

                    side = "LEFT"
                    low = road["llo"]
                    high = road["lhi"]

                elif in_range(hsnum, road["rlo"], road["rhi"]):

                    side = "RIGHT"
                    low = road["rlo"]
                    high = road["rhi"]

                if side is None:
                    continue

                line = road["geom"]

                if line is None:
                    continue

                if high == low:
                    ratio = 0.5
                else:
                    ratio = float(hsnum - low) / float(high - low)

                ratio = max(0.0, min(1.0, ratio))

                if high < low:
                    ratio = 1.0 - ratio

                distance = line.length * ratio

                match_point = line.positionAlongLine(
                    distance,
                    False
                )

                fishbone = arcpy.Polyline(
                    arcpy.Array([
                        addr_geom.centroid,
                        match_point.centroid
                    ]),
                    spatial_ref
                )

                best = (
                    fishbone,
                    road["oid"],
                    road["street"],
                    side
                )

                break

            if best:

                fishbone, road_oid, street, side = best

                icur.insertRow([
                    fishbone,
                    addr_oid,
                    road_oid,
                    full_addr,
                    hsnum,
                    unitnumber,
                    street,
                    side,
                    0
                ])

                fishbone_count += 1

print("Created RCL_Fishbone.")
print("Fishbone count: {0}".format(fishbone_count))

# -------------------------------------------------------------------
# 4. Count fishbone intersections
# -------------------------------------------------------------------

if arcpy.Exists(fishbone_x_fc):
    arcpy.management.Delete(fishbone_x_fc)

arcpy.analysis.Intersect(
    in_features=[fishbone_fc],
    out_feature_class=fishbone_x_fc,
    join_attributes="ALL",
    output_type="POINT"
)

counts = {}

fid_field = "FID_RCL_Fishbone"

fishbone_x_fields = [
    f.name for f in arcpy.ListFields(fishbone_x_fc)
]

if fid_field not in fishbone_x_fields:

    for f in fishbone_x_fields:

        if f.upper().startswith("FID_"):
            fid_field = f
            break

with arcpy.da.SearchCursor(fishbone_x_fc, [fid_field]) as rows:

    for fid, in rows:

        if fid is None:
            continue

        if fid < 0:
            continue

        counts[fid] = counts.get(fid, 0) + 1

with arcpy.da.UpdateCursor(
    fishbone_fc,
    ["OID@", "INTERSECTIONS"]
) as rows:

    for oid, intersections in rows:

        rows.updateRow([
            oid,
            counts.get(oid, 0)
        ])

# -------------------------------------------------------------------
# Delete temporary intersection points
# -------------------------------------------------------------------

if arcpy.Exists(fishbone_x_fc):
    arcpy.management.Delete(fishbone_x_fc)

print("Updated fishbone intersection counts.")
print("Deleted temporary intersection points.")
print("Complete.")
print("Out-of-range address points: {0}".format(out_range_fc))
print("Fishbone lines: {0}".format(fishbone_fc))