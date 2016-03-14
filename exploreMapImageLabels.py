'''
Query single-channel map image label files from a downloaded dataset:
reads in the read-made single channel files and counts the number of pixels with each label
(used to get an overview of proportion of buildings/roads/etc in a dataset)

Lars Roemheld, roemheld@stanford.edu
'''
__author__ = 'Lars Roemheld'
import os, json
from collections import Counter
from PIL import Image

numPixels = Counter()

nl = 0
print "starting to read files"
for fn in os.listdir('.'):
    if len(fn) > 12 and fn[-12:] == 'recolor1.png':
        if nl % 100 == 0:
            print "now in file: " + fn + " #total: " + str(nl)
            print numPixels
        i = Image.open(fn)
        imagePixels = Counter()
        pixels = i.getdata()
        imagePixels.update(pixels)

        for label in imagePixels:
            imagePixels[label] = imagePixels[label] / 256.0 / 256.0
        # todo: median

        numPixels.update(pixels)
        nl += 1

print "done"
print "total files: " + str(nl)
print numPixels
