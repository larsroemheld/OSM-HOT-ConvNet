'''
Gets data for a specified Open Street Map (OSM) Task Manager (OTM) task, esp. for HOT (Humanitarian OSM Team) and mapgive.
Outputs all map tiles belonging to the task joined into one large image, by crawling all TMS tiles (slippy map) belonging
to a task.

Lars Roemheld, roemheld@stanford.edu
'''
__author__ = 'Lars Roemheld'

from bs4 import BeautifulSoup
import requests
import logging
import math
import os, sys, getopt
from PIL import Image
from StringIO import StringIO

def deg2num(lat_deg, lon_deg, zoom):
    '''
    http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames (see explanation there)
    :param lat_deg:
    :param lon_deg:
    :param zoom:
    :return: (x, y) value in slippy map logic for given lat/lon/zoom position
    '''
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1.0 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def getTaskBoundaries(projectID, taskID, zoom):
    try:
        task_boundary_r = requests.get("http://tasks.hotosm.org/project/{0}/task/{1}.gpx".format(str(projectID), str(taskID)))
        logging.info('Getting boundary for task {0} of project {1}: HTTP {2}'.format(taskID, projectID, task_boundary_r.status_code))
        task_boundary_r.raise_for_status()
    except:
        logging.error('Getting the GPX file failed: {0}'.format(sys.exc_info()[0]))
        return None

    # GPX is not html, but an xml format. BeautifulSoup is lenient enough to allow this slight abuse, though.
    try:
        taskSoup = BeautifulSoup(task_boundary_r.text, 'html.parser')
        points = taskSoup.find_all('trkpt')
    except:
        logging.error('Reading in the GPX xml failed: {0} \n\n GPX data: {1}'.format(sys.exc_info()[0], task_boundary_r.text))
        return False

    x_min, x_max, y_min, y_max         = float('inf'), float('-inf'), float('inf'), float('-inf')
    lat_min, lat_max, lon_min, lon_max = float('inf'), float('-inf'), float('inf'), float('-inf')
    for pt in points:
        lat = float(pt['lat'])
        lon = float(pt['lon'])
        lat_min = min(lat, lat_min)
        lat_max = max(lat, lat_max)
        lon_min = min(lon, lon_min)
        lon_max = max(lon, lon_max)
        x, y = deg2num(lat, lon, zoom)
        x_min = min(x, x_min)
        x_max = max(x, x_max)
        y_min = min(y, y_min)
        y_max = max(y, y_max)
    return (lat_min, lon_min, lat_max, lon_max), (x_min, y_min, x_max, y_max)

def getTaskImage(projectID, taskID, TMSurl, zoom=18):
    '''
    Downloads all tiles belonging to an OSM task and joins them into one image.
    NB: the image may have real padding, in that the tiles joined together expand further than the task boundaries.
    Padding < 256pixels in either direction.
    :param projectID:
    :param taskID:
    :param TMSurl: The base-url for the slippy map server, like so: http://hiu-maps.net/hot/1.0.0/caracol-23dec2014-flipped/{z}/{x}/{y}.png
    :param zoom:
    :return: True if success, False otherwise
    '''
    (lat_min, lon_min, lat_max, lon_max), (x_min, y_min, x_max, y_max) = \
        getTaskBoundaries(projectID, taskID, zoom)
    taskWidth  = x_max - x_min + 1
    taskHeight = y_max - y_min + 1
    logging.info('Found bounding box {0},{1} - {2},{3}, comprising {4} TMS/slippy map tiles'.format(lat_min, lon_min, lat_max, lon_max, taskWidth * taskHeight))

    # folder = 'task{0}'.format(str(taskID))
    folder = 'osm-hot-images'
    if not os.path.exists(folder): os.makedirs(folder)
    completeFileName = folder + '/project{0}task{1}_complete.png'.format(str(projectID), str(taskID))

    # Note: this only makes sense for relatively small maps, as a complete task is kept in memory.
    completeImage = Image.new('RGB', (taskWidth * 256, taskHeight * 256))

    imageURL = TMSurl.replace('{z}', str(zoom))
    for x in range(x_min, x_max+1):
        for y in range(y_min ,y_max+1):
            url = imageURL.replace('{x}', str(x)).replace('{y}', str(y))
            try:
                r = requests.get(url)
            except:
                logging.error('Downloading an image failed: {0} \n\n image url: {1}'.format(sys.exc_info()[0], url))
                return False

            try:
                tileImage = Image.open(StringIO(r.content))
            except:
                logging.error('A downloaded image could not be read: {0} \n\n image url: {1}'.format(sys.exc_info()[0], url))
                return False

            completeImage.paste(tileImage, ((x-x_min) * 256, (y-y_min) * 256))
    try:
        completeImage.save(completeFileName)
    except:
        logging.error('Saving the composite image failed: {0} \n\n image filename: {1}'.format(sys.exc_info()[0], completeFileName))
        return False
    else:
        logging.info('Downloaded task map to ' + completeFileName)
        logging.warning('NB: the image may have real padding, in that the tiles joined together expand further than the task boundaries.')
        return True

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    HELPTEXT = 'getTaskData.py -p <HOT OSM project ID> -u <affiliated TMS url> [-t <taskID>]'
    try:
        opts, args = getopt.getopt(sys.argv,"hp:u:t:",["project=","tmsurl=","task="])
    except getopt.GetoptError:
        print HELPTEXT
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print HELPTEXT
            sys.exit()
        elif opt in ("-p", "--project"):
            project_id = int(arg)
        elif opt in ("-u", "--tmsurl"):
            TMS_url = arg
        elif opt in ("-t", "--task"):
            task_ids = [arg]
    if project_id is None or TMS_url is None:
        print HELPTEXT
        sys.exit()

    if task_ids is None:
        print "No task specified. Trying all tasks starting at 0 (until 10 failures, assuming incremental numbering)"
        numFails = 0
        t_id = 0
        while numFails < 10:
            print "### getting task...", t_id
            success = getTaskImage(project_id, t_id, TMS_url)
            print ' Success' if success else ' FAILED.'
            numFails = numFails + 1 if not success else 0
            t_id += 1
    else:
        for t_id in task_ids:
            print "### getting task...", t_id,
            success = getTaskImage(project_id, t_id, TMS_url)
            print ' Success' if success else ' FAILED.'
