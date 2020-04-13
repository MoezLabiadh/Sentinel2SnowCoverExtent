# -*- coding: utf-8 -*-
"""
Created on Thu Apr 06 13:03:40 2020

This script searches and downloads Sentinel-2 (level-2A) imageryfrom the Copernicus Sci Hub servers.

@author: moez.labiadh
"""
import os
import geopandas as gpd
from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt

#Defining the Area of interest (must be GeoJson)
workspace = 'C:/...../workspace'
AOI= os.path.join (workspace, "AOI.geojson")

#Setting connection parameters to the Sentinel Hub server
user = '*****' ## change this!
password = '******' ## change this!
api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')

#Setting the search footprint using a Geojson file
footprint = geojson_to_wkt(read_geojson(AOI))

#Setting the search query parameters
products = api.query(footprint,
                     date = ('20200101', '20200331'),
                     platformname = 'Sentinel-2',
                     processinglevel = 'Level-2A',
                     cloudcoverpercentage = (0, 20))

#Printing the number of products found
print("The number of products found is: {} " .format (len(products)))

#Creating a table with all the product search results
products_table = api.to_geodataframe(products)

#This part downloads the product(s) in the same folder where your code is located

 ## OPTION 1: Download single product
api.download('df132697-676e-43ce-b7bd-45211696119f')

 ## OPTION 2:Download all products
download_list = []
for index, row in products_table.iterrows():    
   download_list.append (row['title'])
   print ("The following products will be downloaded: {}" . format (download_list))
   api.download (row['uuid'])
 
