import arcpy

# Set the workspace to the SDE connection
arcpy.env.workspace = r'Database Connections\wcva_default.sde\wcva.DBO.Utilities'

# Specify the layer name within the SDE
layer_name = 'wcva.DBO.hydrant'

# Add a new field for the Unique IDs if it doesn't exist already
if not arcpy.ListFields(layer_name, 'Hydrant_ID'):
    arcpy.AddField_management(layer_name, 'Hydrant_ID', 'TEXT', field_length=15)  # Set maximum length to 15 characters

# Update the Hydrant_ID field based on X and Y
with arcpy.da.UpdateCursor(layer_name, ['Latitude', 'Longitude', 'Hydrant_ID']) as cursor:
    for row in cursor:
        lat_str = str(row[0])
        lon_str = str(row[1])

        # Ensure latitude and longitude strings are long enough for slicing
        if len(lat_str) > 6 and len(lon_str) > 7:
            # Construct the unique ID in the specified format
            unique_id = '{}{}{}{}-{}{}-{}{}{}{}-{}{}'.format(
                lat_str[1], lon_str[2], lat_str[2], lon_str[3],  # First group
                lat_str[3], lon_str[4],  # Second group
                lat_str[4], lon_str[5], lat_str[5], lon_str[6],  # Third group
                lat_str[6], lon_str[7]  # Fourth group
            )

            # Truncate the unique ID if it exceeds 15 characters
            if len(unique_id) > 15:
                unique_id = unique_id[:15]

            row[2] = unique_id
            cursor.updateRow(row)

print("Unique IDs generated successfully!")
