# ---------------------------------------------------------------------------
# Parcel TPIN / TMEGID QC
# Exports parcels, calculates TPIN with spaces replaced by hyphens,
# exports TPIN <> TMEGID mismatches, then deletes the temp export.
# ---------------------------------------------------------------------------

import arcpy
import os
import datetime

arcpy.env.overwriteOutput = True

# Inputs
sde_parcels = r"X\Arcdata\ArcMap\Scripts\zzDatabase_Connections\wcva_dev.sde\wcva_dev.dbo.Parcel_Details\wcva_dev.dbo.Parcels"

out_gdb = r"X\Arcdata\ArcMap\APRX\APRX.gdb"
out_dataset = "CriticalDataQC"

temp_name = "temp_parcels_qc"
mismatch_name = "Parcel_TPIN_TMEGID_Mismatches"

temp_fc = os.path.join(out_gdb, out_dataset, temp_name)
mismatch_fc = os.path.join(out_gdb, out_dataset, mismatch_name)

try:
    print "Starting Parcel TPIN / TMEGID QC..."

    # Delete old temp and mismatch outputs if they exist
    for fc in [temp_fc, mismatch_fc]:
        if arcpy.Exists(fc):
            print "Deleting existing output: " + fc
            arcpy.Delete_management(fc)

    # Export parcels to temp feature class
    print "Exporting parcels to temp feature class..."
    arcpy.FeatureClassToFeatureClass_conversion(
        sde_parcels,
        os.path.join(out_gdb, out_dataset),
        temp_name
    )

    # Calculate TPIN = TPIN.replace(" ", "-")
    print "Calculating TPIN field..."
    arcpy.CalculateField_management(
        temp_fc,
        "TPIN",
        "!TPIN!.replace(' ', '-') if !TPIN! is not None else None",
        "PYTHON_9.3"
    )

    # Select mismatches
    mismatch_where = """
    (TPIN IS NULL AND TMEGID IS NOT NULL)
    OR
    (TPIN IS NOT NULL AND TMEGID IS NULL)
    OR
    (TPIN <> TMEGID)
    """

    lyr = "parcel_qc_lyr"

    print "Selecting TPIN / TMEGID mismatches..."
    arcpy.MakeFeatureLayer_management(temp_fc, lyr)
    arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", mismatch_where)

    mismatch_count = int(arcpy.GetCount_management(lyr).getOutput(0))
    print "Mismatch count: " + str(mismatch_count)

    # Export mismatches
    if mismatch_count > 0:
        print "Exporting mismatches..."
        arcpy.FeatureClassToFeatureClass_conversion(
            lyr,
            os.path.join(out_gdb, out_dataset),
            mismatch_name
        )
        print "Mismatch export created: " + mismatch_fc
    else:
        print "No mismatches found. No mismatch feature class created."

    # Clean up temp export
    if arcpy.Exists(temp_fc):
        print "Deleting temp parcel export..."
        arcpy.Delete_management(temp_fc)

    print "QC complete."

except Exception as e:
    print "QC failed."
    print str(e)
    print arcpy.GetMessages(2)

    # Best-effort cleanup
    if arcpy.Exists(temp_fc):
        try:
            arcpy.Delete_management(temp_fc)
        except:
            pass