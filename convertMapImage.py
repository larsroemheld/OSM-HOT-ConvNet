'''
Load an image and replace colors given a map. Used to convert images in the HOT-OSM format to pixelwise class labels.

Lars Roemheld, roemheld@stanford.edu
'''
__author__ = 'Lars Roemheld'

from PIL import Image
import sys

HOT_labels_map ={   'default':       0,
                    (220, 214, 214): 1,	  #	building
                    (210, 147, 142): 2,	  #	road-primary
                    (233, 203, 176): 2,	  #	road-secondary
                    (219, 222, 153): 2,	  #	road-tertiary
                    (221, 220, 189): 3,	  #	farm
                    (226, 232, 225): 4,	  #	wetland1
                    (222, 229, 221): 4,	  #	wetland2
                    (178, 194, 157): 5,	  #	forrest
                    (116, 116, 115): 0, #	icons
                    (114, 137, 142): 0, #	text-center
                    (238, 238, 237): 0, #	text-shadow
                    (144, 204, 203): 6}	  #	river

# HOT_labels_map ={   'default':       (0, 0, 0),
#                     (220, 214, 214): (255,0,0),	  #	building
#                     (210, 147, 142): (0,255,0),	  #	road-primary
#                     (233, 203, 176): (0,255,0),	  #	road-secondary
#                     (219, 222, 153): (0,255,0),	  #	road-tertiary
# #                    (246, 245, 241): (0,255,0),	  #	road-pvdresl -- this leads to overlap :(
#                     (221, 220, 189): (0,0,255),	  #	farm
#                     (226, 232, 225): (128,0,0),	  #	wetland1
#                     (222, 229, 221): (128,0,0),	  #	wetland2
#                     (178, 194, 157): (0,128,0),	  #	forrest
#                     (116, 116, 115): (255,0,255), #	icons
#                     (114, 137, 142): (255,0,255), #	text-center
#                     (238, 238, 237): (255,0,255), #	text-shadow
#                     (144, 204, 203): (0,0,128)}	  #	river

def recolorImage(baseImage, colorMap):
    baseImage = baseImage.convert('RGB')
    pixels = baseImage.getdata()
    newPixels = []
    for p in pixels:
        found = False
        for oldColor in colorMap:
            if oldColor == 'default':
                continue
            distance = sum([(oldColor[i] - p[i]) ** 2.0 for i in range(3)]) # L2 color distance
            if distance < 3:
                newPixels.append(colorMap[oldColor])
                found = True
                break
        if not found:
            if 'default' in colorMap:
                newPixels.append(colorMap['default'])
            else:
                newPixels.append(p)

    newImage = Image.new('L', (baseImage.size[0], baseImage.size[1]))
    newImage.putdata(newPixels)
    return newImage

filename = sys.argv[1]
img = Image.open(filename)
newImg = recolorImage(img, HOT_labels_map)
newImg.save(filename + "_recolor1.png", "PNG")
