# devland

### Python scripts to obtain the amount of developable and developed land in the U.S. on the Census Tract level

This repository contains two scripts which complement each other and can be used to obtain the amount of developed and developable land in the United States using Python and ArcGIS (`arcpy` library). The approach utilized here is based on the definition of developable land described by Saiz (2010). To define the land that can be developable, it uses the very basic restrictions that are described below. These restrictions can be further complemented by placing the additional limitations if needed. The idea behind these scripts is to provide a very basic core that can be further extended.

The data required to run these scripts is as follows:

  1. National Land Cover Database (NLCD): 2001 Land cover;
  2. National Elevation Dataset (NED): 1x1 second tiles;
  3. Census Tiger shapefiles with Census Tracts.

### The workflow
#### Part 1 script
This code is the first part of the algorithm, which aims to automate the procedure of obtaining the total amount (area) of developable and developed land in the USA.

Required on this stage: 

  1. National Land Cover Database (NLCD): 2001 Land cover;
  2. National Elevation Dataset (NED): 1x1 second tiles.

The script combines two raster datasets (NED and NLCD) together and produces two raster data files as an output. One of them contains data on developed land and has the file name that ends with `LPD` (shortcut for "developed") and another file with the name that ends with `PBL` (shortcut for "developable"). Each output raster file will contain 30x30 meter cells with the data on slope in percentage. These raster files will then be written back to the location of their NED predecessors that corresponds to 1x1-degree NED tiles.

Conditions for developable land:

  1. Slope is less than 15% (following Saiz).
  2. Parcells that according to the NLCD classification description are not defined as water, developed land or waterlands. 

Conditions for developed land:

  1. Parcells that according to the NLCD classification description are defined as developed.


#### Part 2 script
This code is the second part of the algorithm, which aims to estimate the amount of developable and developed land in each census tract of the selected state. It should be run only after the first part is completely done. 

Required on this stage: 
1. Output files generated by Part 1 script;
2. Census Tiger shapefiles.

This script loops through the folder with shapefiles. For each shapefile it determines the coordinates of the 4 extreme corners that form a rectangular, which covers each shapefile. Then it selects the correct 1x1-degree NED tiles and merges them together to cover the whole each shapefile. Finally, it applies a zonal statistics tool to get the amount of developable and developed land in each census tract. The resulting zonal statistics tables contains data on the amount of developable and developed land, as well as the mean and standard deviation of the slope in each Census Tract.

### Directions on how to use the scripts 
#### Part 1 script
The application of this script is pretty straightforward. A user needs to specify a set of input paths that are defined at the beginning of the script. Besides of that, a user might want to alter SQL clause that defines what parcels should be used for developable land.

#### Part 2 script
It is important that a user follows the specified here directory structures and naming convention for the input files. Two root paths should be specified: the one, which contains all the raster files with developable and developed land obtained by Part 1 and another one, which contains state features with census tracts.

Rasters:
Raster files for one arc-second each are located in separate subdirectories of the root directory. The user should specify a root directory path for rasters in "rootRasters" at the beginning of the file. The name of each subdirectory should follow the following pattern: `nXXwYYY`, where `XX` is the latitude and `YYY` is a longitude in seconds. Each of these directories should contain 3 raster files: the first one - original, the second one with the name `nXXwYYY_PBL` - raster containing the information on developable land and the third one - `nXXwYYY_LPD`, containing the information on developed land.

Only the second and the third rasters will be used. Eventually, selected rasters will be mosaiced (merged) together in two separate combined raster files, which cover the whole state. One for the developable land and another one for the developed land. After this step a zonal statistics tool is applied to the both files, providing a user with the amount of developable land and the average slope separately for developable (PBL extension) and developed land (LPD extension) in each Census Tract.

Census tracts:
A user should have another directory, which contains the shapefiles of census tracts. Each such shapefile should cover the whole state and be placed in a separate subdirectory. The name of the subdirectory does not matter, but the name of the shapefile should follow the pattern: `tl_2010_XX_tract00`, where `XX` stands for the state FIPS code.


References: 

  * Saiz, A. 2010. The Geographic Determinants of Housing Supply. Quarterly Journal of Economics.
  * [NLCD data](http://www.mrlc.gov/nlcd01_data.php)
  * [NED data](http://nationalmap.gov/elevation.html)
  * [Census Tiger](https://www.census.gov/geo/maps-data/data/tiger-line.html)
