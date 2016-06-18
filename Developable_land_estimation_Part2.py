# Script Name: Developable and developed land in the USA: Part 2.
# Description: This script is used to get a zonal statistics on
#              the developable and developed land. 
# Created By:  Ievgenii Kudko.
# Date:        December 19th 2014.

# Set the environment settings
import os, arcpy, math 
from arcpy.sa import *

#Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# Set the environment settings and define some parameters
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"Z:\Google Drive\Developable_land_and_Average_slope\GIS_data\NewApp.gdb"
coordSys = r"Z:\Google Drive\Developable_land_and_Average_slope\GIS_data\Albers_Conical_Equal_Area.prj"
rootStateShape = r"Z:\Google Drive\Developable_land_and_Average_slope\GIS_data\Tracts"
rootRasters = r"Z:\Google Drive\Developable_land_and_Average_slope\GIS_data\NED"
outBound = "in_memory/featureBound"


# Loop through all the subdirectories of the root directory and get the tracts feature files 
for dirpath, dirnames, filenames in arcpy.da.Walk(rootStateShape,
                                                  datatype="FeatureClass",
                                                  type="Polygon"):
    for filename in filenames:
        # In case we need to create a list with all shapefiles:
        # tractFeatureList.append(os.path.join(dirpath, filename))
        # Get the current shapefile to work with
        inTractFeature = os.path.join(dirpath, filename)
        # Create output names for raster files, which will contain developable and developed land
        state = filename[8:10]
        developableMrgd = "pbl_mrgd_" + state
        developedMrgd = "lpd_mrgd_" + state
        featureProjected = "feature_prj"
        landStatDevelopable = "Developable_Land_Stat" + state
        landStatDeveloped = "Developed_Land_Stat" + state  

        #Projecting the feature in the same coordinate system as rasters from part1
        arcpy.Project_management(inTractFeature, featureProjected, coordSys)
        # Find the coordinates of state's extreme points (upper left and bottom rigth corners)
        arcpy.MinimumBoundingGeometry_management(inTractFeature, outBound, "ENVELOPE", "ALL")
        for row in arcpy.da.SearchCursor(outBound, ["SHAPE@"]):
            extent = row[0].extent
            # The coordinates of the top left corner
            top = int(math.ceil(round(extent.YMax, 2)))
            left = int(abs(math.floor(round(extent.XMin, 2))))
            # The coordinates of the bottom right corner
            bottom = int(math.ceil(round(extent.YMin, 2)))
            right = int(abs(math.floor(round(extent.XMax, 2))))
            
            # Given the coordinates of these 2 extreme points, we may create a list of folders
            # names which contains only the rasters required to cover this particular state
            n = range(bottom, top+1)
            w = range(right, left+1)
            
            rasterFolders = []
            for i in n:
                for j in w:
                    rasterFolder = rootRasters+"\\"+"n"+str(i)+"w"+str(j)
                    rasterFolders.append(rasterFolder)
                    

            # Loop through all the subdirectories of the rasters' root directory and get the list
            # of only the rasters required to cover this particular state
            developableRasterDirsList = []  # Rasters for developable land 
            developedRasterDirsList = []    # Rasters for developed land  
            for dirpath, dirnames, filenames in arcpy.da.Walk(rootRasters,
                                                  datatype="RasterCatalog",
                                                  type="JPG"):
                for filename in filenames:
                    # Match for developable rasters 
                    if (os.path.dirname(dirpath) in rasterFolders) and (filename[-3:] == "pbl"):
                        developableRasterDirsList.append(os.path.join(dirpath))
                    # Match for developed rasters 
                    if (os.path.dirname(dirpath) in rasterFolders) and (filename[-3:] == "lpd"):
                        developedRasterDirsList.append(os.path.join(dirpath))

            #arcpy.MosaicToNewRaster_management(developableRasterDirsList, arcpy.env.workspace, developableMrgd, "", "8_BIT_SIGNED", "", 1)
            arcpy.MosaicToNewRaster_management(developedRasterDirsList, arcpy.env.workspace, developedMrgd, "", "8_BIT_UNSIGNED", "", 1)

            #Obtain the developable land sttistics on the tracts level
            outZSat_Developable = ZonalStatisticsAsTable(featureProjected, "CTIDFP00", developableMrgd, landStatDevelopable, "DATA", "MEAN_STD")

            #Obtain the developed land statistcs on the tracts level
            outZSaT_Developed = ZonalStatisticsAsTable(featureProjected, "CTIDFP00", developedMrgd, landStatDeveloped, "DATA", "MEAN_STD")