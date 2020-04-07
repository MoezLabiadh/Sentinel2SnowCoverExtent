# -*- coding: utf-8 -*-
"""
Created on Thu Apr 06 13:03:40 2020
@author: MLABIADH

This script creates a Snow Cover Extent Layer based on Sentinel-2 Level 2A imagery.

"""
import os
import numpy as np
import rasterio
from rasterio.enums import Resampling

Workspace = 'H:/Profile/Desktop/TRAINING/RS/SnowCoverProject'
S2_path = os.path.join (Workspace, 'raw_data/S2B_MSIL2A_20191208T184749_N0213_R070_T11UNQ_20191208T205518.SAFE')

#Browse through the S2 product folder and retrieve the following bands: Green, Red, NIR, SWIR and Cloud probability
for root, dirs, files in os.walk(S2_path):
    for name in files:
        if name.endswith("B03_10m.jp2"):
            Gpath = os.path.join (root, name)
        elif name.endswith("B04_10m.jp2"):
            Rpath = os.path.join (root, name)
        elif name.endswith("B08_10m.jp2"):
            NIRpath = os.path.join (root, name)            
        elif name.endswith("B11_20m.jp2"):
            SWIR1path = os.path.join (root, name)
        elif name.endswith("B12_20m.jp2"):
            SWIR2path = os.path.join (root, name)            
        elif name.endswith("CLDPRB_20m.jp2"):
            CLDprobpath = os.path.join (root, name)
        else:
            pass
print ('Bands G, R, NIR, SWIR and Cloud probability retrieved from the Sentinel-2 product')

#Read the bands as arrays. Resample (upscale) SWIR and Cloud bands to 10m.
upscale_factor = 2

with rasterio.open(Gpath) as green:
    GREEN = green.read()
    Gcrs = green.crs
    profile = green.profile
    
with rasterio.open(Rpath) as red:
    RED = red.read()

with rasterio.open(NIRpath) as nir:
    NIR = nir.read()
    
with rasterio.open(SWIR1path) as swir1:
    ## resample data to target shape
    print ('Resampling SWIR and Cloud bands to 10m')
    SWIR1 = swir1.read(
                     out_shape = (swir1.count, int(swir1.width * upscale_factor), int(swir1.height * upscale_factor)), 
                     resampling = Resampling.bilinear
                     )
    ## Transform from pixel row/column coordinates to spatial coordinates (in the dataset’s coordinate reference system).
    transform = swir1.transform * swir1.transform.scale((swir1.width / SWIR1.shape[-2]),(swir1.height / SWIR1.shape[-1]))
       
with rasterio.open(CLDprobpath) as cloud:
    CLOUD  = cloud.read(
                        out_shape = (cloud.count, int(cloud.width * upscale_factor), int(cloud.height * upscale_factor)), 
                        resampling = Resampling.bilinear
                        )
    transform = cloud.transform * cloud.transform.scale((cloud.width / CLOUD.shape[-2]),(cloud.height / CLOUD.shape[-1]))
    
#Create the Cloud Mask.
print ("Calculating the Cloud Mask")

 ## Expression: IF Cloudprob >= 90 THEN 2. ELIF (Cloudprob >= 50 AND NIR > 0.3) OR (Cloudprob >= 20 AND NIR > 0.9) THEN 1. ELSE 0
 ## 2 is High Probability Cloud. 1 is Low probability Cloud or Haze. 0 is No cloud.
Cloud_mask = np.where((CLOUD >= 90), 2, np.where(((CLOUD >= 50) & (NIR > 3000) | ((CLOUD >= 20) & (NIR > 9000))),1,0))
       
#Calculate the Normalized Difference Snow Index 
print ("Calculating the NDSI")
ndsi= (GREEN.astype(float) - SWIR1.astype(float)) / (GREEN+SWIR1)

# Create the Snow Cover (SCE) Extent Layer
 ## Expression: IF CloudMask = 0 AND NDSI > 0.3 AND RED > 0.3 THEN 2. ELIF CloudMask > 0 THEN 1. ELSE 0
 ##2 is Snow. 1 is Cloud or Haze. 0 is No Snow
print ("Calculating the Snow Cover Extent")
SCE = np.where(((Cloud_mask == 0) & (ndsi >= 0.3) & (RED >= 1000)), 2, np.where (((Cloud_mask > 0)),1,0))

#Create a new folder that will hold the script outputs
Output_dir = os.path.join (Workspace, 'Script_Outputs')
if not os.path.exists(Output_dir):
    os.makedirs (Output_dir)
else:
    pass 

#Export the final outputs
 ## Update profile saved from the Green band. Set the driver to Gtiff and type to Float, apply compression...
profile.update(driver='GTiff' , dtype=rasterio.uint16 , crs = Gcrs , compress='lzw')

print ("Exporting the Snow Cover Extent")
 ##Include the tile number and acquisition date in the outputs names. 
SnowCover = os.path.join (Workspace, Output_dir, 'S2A_' + os.path.basename(Gpath)[:15] + '_Snow_cover_extent.tif')

## Write the SCE array to the drive as Geotiff image. 
with rasterio.open(SnowCover, 'w', **profile) as sce_out:
    sce_out.write (SCE.astype(rasterio.uint16))
    sce_out.close ()
    
print ("Exporting the Band Composite (SWIR2, SWIR1, GREEN)")
b12_swir2 = rasterio.open (SWIR2path)
b11_swir1 = rasterio.open (SWIR1path)
b03_G= rasterio.open (Gpath)

profile.update(count=3) # Update the profile again to change the number of bands to 3.

BandComposite = os.path.join (Workspace, Output_dir, 'S2A_' + os.path.basename(Gpath)[:15] + '_Band_Composite.tif') 
 
## Write the Band Composite array to the drive as Geotiff image. Composite is SWIR2, SWIR1, Green 
with rasterio.open(BandComposite, 'w', **profile) as bandcomp_out:
   bandcomp_out.write (b12_swir2.read(1),1)
   bandcomp_out.write (b11_swir1.read(1),2)
   bandcomp_out.write (b03_G.read(1),3)
   bandcomp_out.close ()
    
    
print ("Process Completed. Output location is: {}" .format (os.path.join (Workspace, Output_dir)))
