'''
Just a playground to come to grips with lat/lon and y/x and pixels within tiles.
'''
__author__ = 'lars'
import math
import getTaskData

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def deg2float(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = (lon_deg + 180.0) / 360.0 * n
    ytile = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
    return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

# (lat_min, lon_min, lat_max, lon_max), (x_min, y_min, x_max, y_max) = \
#         getTaskData.getTaskBoundaries(1080, 1, 18)

bbox = ((19.6352401871, -72.0713124871), (19.6415875306, -72.060326159))

NWx, NWy = deg2num(*bbox[0], zoom=18)
SEx, SEy = deg2num(*bbox[1], zoom=18)

print "lon {0} / lat {1} -- x {2} / y {3}".format(bbox[0][1], bbox[0][0], NWx, NWy)
print "lon {0} / lat {1} -- x {2} / y {3}".format(bbox[1][1], bbox[1][0], SEx, SEy)

x_f, y_f = deg2float(*bbox[0], zoom = 18)
offset_X_top = int((x_f - int(x_f)) * 256.0)
offset_Y_top = int((y_f - int(y_f)) * 256.0)

x_f, y_f = deg2float(*bbox[1], zoom = 18)
offset_X_bottom = int((1 - x_f + int(x_f)) * 256.0)
offset_Y_bottom = int((1 - y_f + int(y_f)) * 256.0)

print "offset top: ", (offset_X_top, offset_Y_top)
print "offset bottom: ", (offset_X_bottom, offset_Y_bottom)

