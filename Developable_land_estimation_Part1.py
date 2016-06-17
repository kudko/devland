# Script Name: Developable and developed land in the USA: Part 1.
# Description: The script automates the procedure of
#              obtaining the total amount (area) of
#              developable and developed land in the USA.
# Inputs:      NED raster data, NLCD raster data, coordinate system
# Output:      Raster file with developed and developable land
# Created By:  Ievgenii Kudko.
# Date:        October 16th 2014.

# Set the environment settings
import os, arcpy, tempfile, shutil 
from arcpy.sa import *

# Set the environment settings
arcpy.env.overwriteOutput = True
root = r"Z:\ievgenii On My Mac\Google Drive\Developable_land_and_Average_slope\GIS_data\NED"

# Input pathes for the coordinate system and NLCD files
# Define the coordinate system
coordSys = r"Z:\ievgenii On My Mac\Google Drive\Developable_land_and_Average_slope\GIS_data\Albers_Conical_Equal_Area.prj"
# Define the location for NLCD raster data
inNLCD = r"Z:\ievgenii On My Mac\Google Drive\Developable_land_and_Average_slope\GIS_data\nlcd_2001_landcover_2011_edition_2014_03_31\nlcd_2001_landcover_2011_edition_2014_03_31.img"
# Define the location for log files
logErrors = open(r"Z:\ievgenii On My Mac\Google Drive\Developable_land_and_Average_slope\GIS_data\errors.txt", "w")
logSuccess = open(r"Z:\ievgenii On My Mac\Google Drive\Developable_land_and_Average_slope\GIS_data\successes.txt", "w")

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# Loop through all subdirectories of the root directory and get the NED raster file names
for dirpath, dirnames, filenames in arcpy.da.Walk(root,
                                                  datatype="RasterCatalog",
                                                  type="JPG"):
    for filename in filenames:
        # Create a temporary database to work with the current raster file
        temp_dir = tempfile.mkdtemp()
        temp_gdb = "temp.gdb"
        arcpy.CreateFileGDB_management(temp_dir, temp_gdb)
        arcpy.env.workspace = os.path.join(temp_dir, temp_gdb)

        # Define the output folder for the final output raster (the same as the current folder)
        rasterLocation = os.path.dirname(dirpath)
        # Define some other local IO paths
        # [to list all files: rasterList.append(os.path.join(dirpath))]
        inNED = dirpath
        outNED_prj = filename[3:-1] + "PRJ" 
        outSlopeSVD = filename[3:-1] + "SLP" #"in_memory" + "/" + 
        SQLClauseField = filename.upper()[3:-1] + "SI"
        outSlope_toInt = SQLClauseField
        outCombineSVD = filename[3:-1] + "CMB"

        attExtractDevelopableSVD = filename[3:-1] + "BLT"
        cleanNEDDevelopableSVD = rasterLocation + "\\" + filename[3:-1] + "PBL"

        attExtractOut_developedSVD = filename[3:-1] + "PDT"
        cleanNEDDevelopedSVD = rasterLocation + "\\" + filename[3:-1] + "LPD"
        

        # Projecting the NED data into compatible with NLCD format
        arcpy.ProjectRaster_management(inNED, outNED_prj, coordSys, "NEAREST", "30")
        # Calculate the slope
        outSlope = Slope(outNED_prj, 'PERCENT_RISE')
        outSlope.save(outSlopeSVD)
        # Change the pixel type from float to integer
        outSlope_int = Int(outSlopeSVD)
        outSlope_int.save(outSlope_toInt)

        try:
            # Combine NED slope data with NLCD data
            outCombine = Combine([inNLCD, outSlope_toInt])
            outCombine.save(outCombineSVD)


            ##### This part will cover the statistics for the DEVELOPABLE land #####
            # Extract the cells suitable for the developable land
            # (!) The importance here is in the question what cells to include in the analysis. For example, one might
            # also want to remove cells, which have nlcd code 90 (Woody Wetlands) and 95 (Emergent Herbaceous Wetlands).
            SQLClauseDevelopable= SQLClauseField + ' <= 15 AND "nlcd_2001_landco" IN ( 31, 41, 42, 43, 51, 52, 71, 72, 73, 81, 82)'
            attExtractDevelopable = ExtractByAttributes(outCombineSVD, SQLClauseDevelopable)
            attExtractDevelopable.save(attExtractDevelopableSVD)
            # Get back the NED raster file with elevation value in Value field using Lookup tool
            cleanNEDDevelopable = Lookup(attExtractDevelopableSVD, SQLClauseField)
            cleanNEDDevelopable.save(cleanNEDDevelopableSVD)
            
    
            ###### This part will cover the statistics for the DEVELOPED land ######
            # Extract the cells where the land have already been developed
            SQLClauseDeveloped= '"nlcd_2001_landco" IN (21, 22, 23, 24)'
            attExtractDeveloped = ExtractByAttributes(outCombineSVD, SQLClauseDeveloped)
            attExtractDeveloped.save(attExtractOut_developedSVD)

            # Get back the NED raster file with elevation value in Value field using Lookup tool
            cleanNEDDeveloped = Lookup(attExtractOut_developedSVD, SQLClauseField)
            cleanNEDDeveloped.save(cleanNEDDevelopedSVD)

        except:
            logErrors.write(filename[3:-2] + "\n")
            pass

        shutil.rmtree(temp_dir, True)
        logSuccess.write(filename[3:-2] + "\n")
        print filename[3:-2] + " is  done!"
        

logErrors.close()
logSuccess.close()
print "All done!"



