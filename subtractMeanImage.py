'''
First gets the mean image of a folder. Then subtracts that mean image from every
image file and puts the new copy in a new folder.

Lars Roemheld, roemheld@stanford.edu
'''
__author__ = 'Lars Roemheld'

import sys, os
from scipy import misc
import numpy as np

folder = sys.argv[1]

if not os.path.exists(folder + 'minusmean/'):
    os.mkdir(folder + 'minusmean/')

print "getting average"
averageIm = np.zeros((256, 256, 4))
countIm = 0
for file in os.listdir(folder):
    if file.endswith(".png"):
        oldFilename = folder + file
        if countIm % 250 == 0:
            print "now on file {}, {}".format(countIm, file)
        img = misc.imread(oldFilename)
        # if countIm % 250 == 0:
        #     new = img - averageIm
        #     misc.imsave('ex{}.png'.format(countIm), new)

        averageIm = (countIm * averageIm + img) / (countIm + 1.0)
        countIm += 1

        # if countIm % 1000 == 0:
        #     misc.imsave('avg{}.png'.format(countIm), averageIm)
        #     print "saved"

misc.imsave(folder + 'folder_average.png', averageIm)
print "saved average"

print "Subtracting average from images"
countIm = 0
for file in os.listdir(folder):
    if file.endswith(".png"):
        oldFilename = folder + file
        newFilename = folder + "minusmean/" + file
        if countIm % 250 == 0:
            print "now on file {}, {}".format(countIm, file)
        img = misc.imread(oldFilename)
        new = img - averageIm
        misc.imsave(newFilename, new)
        countIm += 1

print "done"