# ---------------------------------------------------------------------------
# Parcel / Vision Account Number QC
#
# Exports parcels, matches Vision records by TPIN,
# compares Parcel.rec400 to Vision.mrecno,
# exports mismatches, then deletes temp FC.
#
# SDE Parcels and Vision tables are READ ONLY.
# ---------------------------------------------------------------------------

import arcpy
import os

arcpy.env.overwriteOutput = True

# ---------------------------------------------------------------------------
# INPUTS
# ---------------------------------------------------------------------------

sde_parcels = r"P:\Arcdata\ArcMap\Scripts\zzDatabase_Connections\wcva_dev.sde\wcva_dev.dbo.Parcel_Details\wcva_dev.dbo.Parcels"

sde_vision = r"P:\Arcdata\ArcMap\Scripts\zzDatabase_Connections\wcva_dev.sde\wcva_dev.dbo.Vision"

out_gdb = r"P:\Arcdata\ArcMap\APRX\APRX.gdb"
out_dataset = "CriticalDataQC"

temp_name = "temp_parcels_vision_qc"
mismatch_name = "AcctNum_Mismatches"

temp_fc = os.path.join(out_gdb, out_dataset, temp_name)
mismatch_fc = os.path.join(out_gdb, out_dataset, mismatch_name)

# Parcel fields
parcel_tpin_field = "tpin"
parcel_account_field = "rec400"

# Vision fields
vision_tpin_field = "tpin"
vision_account_field = "mrecno"

# Temporary field
vision_join_field = "VISION_MRECNO"

# ---------------------------------------------------------------------------
# PROCESS
# ---------------------------------------------------------------------------

try:

    print "Starting Parcel / Vision Account QC..."

    # -----------------------------------------------------------------------
    # Remove previous outputs
    # -----------------------------------------------------------------------

    for fc in [temp_fc, mismatch_fc]:
        if arcpy.Exists(fc):
            print "Deleting existing output: " + fc
            arcpy.Delete_management(fc)

    # -----------------------------------------------------------------------
    # Export Parcels
    # -----------------------------------------------------------------------

    print "Exporting parcels..."

    arcpy.FeatureClassToFeatureClass_conversion(
        sde_parcels,
        os.path.join(out_gdb, out_dataset),
        temp_name
    )

    # -----------------------------------------------------------------------
    # Add temp Vision account field
    # -----------------------------------------------------------------------

    print "Adding Vision account field..."

    arcpy.AddField_management(
        temp_fc,
        vision_join_field,
        "LONG"
    )

    # -----------------------------------------------------------------------
    # Read Vision records into dictionary
    # -----------------------------------------------------------------------

    print "Reading Vision table..."

    vision_lookup = {}

    with arcpy.da.SearchCursor(
        sde_vision,
        [vision_tpin_field, vision_account_field]
    ) as cursor:

        for row in cursor:

            tpin = row[0]
            account = row[1]

            if tpin is not None:

                tpin_key = str(tpin).strip()

                vision_lookup[tpin_key] = account

    print "Vision records loaded: " + str(len(vision_lookup))

    # -----------------------------------------------------------------------
    # Populate Vision account values
    # -----------------------------------------------------------------------

    print "Joining Vision account values..."

    with arcpy.da.UpdateCursor(
        temp_fc,
        [parcel_tpin_field, vision_join_field]
    ) as cursor:

        for row in cursor:

            parcel_tpin = row[0]

            if parcel_tpin is not None:

                tpin_key = str(parcel_tpin).strip()

                row[1] = vision_lookup.get(tpin_key)

            else:

                row[1] = None

            cursor.updateRow(row)

    # -----------------------------------------------------------------------
    # Select mismatches
    # -----------------------------------------------------------------------

    parcel_field_sql = arcpy.AddFieldDelimiters(
        temp_fc,
        parcel_account_field
    )

    vision_field_sql = arcpy.AddFieldDelimiters(
        temp_fc,
        vision_join_field
    )

    mismatch_where = """
    ({0} IS NULL AND {1} IS NOT NULL)
    OR
    ({0} IS NOT NULL AND {1} IS NULL)
    OR
    ({0} <> {1})
    """.format(
        parcel_field_sql,
        vision_field_sql
    )

    print mismatch_where

    lyr = "parcel_vision_qc_lyr"

    print "Selecting mismatches..."

    arcpy.MakeFeatureLayer_management(temp_fc, lyr)

    arcpy.SelectLayerByAttribute_management(
        lyr,
        "NEW_SELECTION",
        mismatch_where
    )

    mismatch_count = int(
        arcpy.GetCount_management(lyr).getOutput(0)
    )

    print "Mismatch count: " + str(mismatch_count)

    # -----------------------------------------------------------------------
    # Export mismatches
    # -----------------------------------------------------------------------

    if mismatch_count > 0:

        print "Exporting mismatches..."

        arcpy.FeatureClassToFeatureClass_conversion(
            lyr,
            os.path.join(out_gdb, out_dataset),
            mismatch_name
        )

        print "Mismatch export created:"
        print mismatch_fc

    else:

        print "No mismatches found."

    # -----------------------------------------------------------------------
    # Cleanup temp FC
    # -----------------------------------------------------------------------

    if arcpy.Exists(temp_fc):

        print "Deleting temp export..."

        arcpy.Delete_management(temp_fc)

    print "QC complete."

except Exception as e:

    print "QC failed."
    print str(e)
    print arcpy.GetMessages(2)

    if arcpy.Exists(temp_fc):

        try:
            arcpy.Delete_management(temp_fc)
        except:
            pass