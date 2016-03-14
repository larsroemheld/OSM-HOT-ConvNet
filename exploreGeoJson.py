'''
Query geojson files from a downloaded dataset, reading in each map-square's geojson and looking for certain objects
(used to get an overview of proportion of buildings/roads/etc in a dataset)

building
highway (road)
natural: water
water: reservoir
waterway: river
landuse: meadow
landuse: farmland

Lars Roemheld, roemheld@stanford.edu
'''
__author__ = 'Lars Roemheld'
import os, json
import getOSMmap

look_for_tag = "landuse"

nl = 0
ntag = 0

print "starting to read files"
for fn in os.listdir('.'):
    if len(fn) > 5 and fn[-5:] == '.json':
        if nl % 100 == 0:
            print "now in file: " + fn + " #total: " + str(nl) + " #withTag: " + str(ntag)
        with open(fn, 'r') as f:
            map_data = json.load(f)
            nl += 1
            ntag += getOSMmap.osmMapHasTag(map_data, look_for_tag)

print "done"
print look_for_tag
print "total files: " + str(nl)
print "thereof with tag: " + str(ntag)
print "percentage: " + str(1.0 * ntag / nl)
