'''
Gets data for a specified Open Street Map (OSM) Task Manager (OTM) task, esp. for HOT (Humanitarian OSM Team) and mapgive.
Outputs all map tiles belonging to the task joined into one large image, by crawling all TMS tiles (slippy map) belonging
to a task.

Lars Roemheld, roemheld@stanford.edu
'''
__author__ = 'Lars Roemheld'

from bs4 import BeautifulSoup
from bs4.element import NavigableString
import requests
import json
import logging
import math
import os, sys, getopt
from PIL import Image
from StringIO import StringIO

def getPageSoup(url):
    try:
        r = requests.get(url) # , headers={'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'}
        r.raise_for_status()
    except:
        logging.error('Getting page {0} failed: {1}'.format(url, sys.exc_info()[0]))
        return None

    try:
        soup = BeautifulSoup(r.text, 'html.parser')
    except:
        logging.error('Reading in the page html failed: {0} \n\n http data: {1}'.format(sys.exc_info()[0], r.text))
        return None
    return soup
def getSoupStringConcat(soupTag):
    '''
    Beautiful soup tags return their content text in the .string parameter if there is only one string child.
    Some unfortunate cases on scotus blog have more than one child-string, and this helper just concat's them.
    :param soupTag: a bs4 tag that contains one or more strings
    :return: a string containing all string children of soupTag, concatenated.
    '''
    if isinstance(soupTag, NavigableString): return soupTag.string
    result = ""
    for t in soupTag.descendants:
        if t.string is not None and isinstance(t, NavigableString): # only include NavigableStrings (work around .string default searching behavior)
            if t.parent.name != "script": # prevent reading js
                result = result + t.string
    return result

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
def deg2float(lat_deg, lon_deg, zoom):
    '''
    Same as above -- but as return values are floats we get an exact position within the tile (the tile is given
    by its north-west corner, int(xtile)/int(ytile)
    '''
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = (lon_deg + 180.0) / 360.0 * n
    ytile = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
    return (xtile, ytile)

def getProjectMeta(projectID):
    '''
    Retrieve meta data for a project
    :return: dictionary with meta data
    '''
    project_meta = {}
    # download OTM page to retrieve project info
    otm_url = 'http://tasks.hotosm.org/project/{0}'.format(str(projectID))
    otmSoup = getPageSoup(otm_url)
    project_meta['title']             = otmSoup.title.string.replace('\n', '')
    project_meta['description']       = getSoupStringConcat(otmSoup.find(id='description'))
    project_meta['entities']          = otmSoup.find(id='instructions').find_all('dd')[0].string
    project_meta['changeset_comment'] = otmSoup.find(id='instructions').find_all('dd')[1].string.replace('\n', '')
    return project_meta

def getTaskBoundaries(projectID, taskID, zoom=18):
    '''
    Get the bounding box for a given HOT OTM task. Both lat/long coordinates, and x/y coordinates are returned.
    :param projectID:
    :param taskID:
    :param zoom: Only needed for calculation of x/y coordinates (lat/long are invariant to this)
    :return: (lat_min, lon_min, lat_max, lon_max), (x_min, y_min, x_max, y_max)
    '''
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

def getTaskStatus(projectID, taskID):
    '''
    Retrieve work status for the given task
    :return: status \in ["Ready", "Invalidated", "Done", "Validated"]
    '''
    # This is hacky: this url is an ajax endpoint that is somewhat "hidden" -- hence the special header required.
    task_url = 'http://tasks.hotosm.org/project/{0}/task/{1}'.format(str(projectID), str(taskID))
    try:
        task_r = requests.get(task_url, headers = {'X-Requested-With' : 'XMLHttpRequest'})
        task_r.raise_for_status()
    except:
        logging.error('Failed to download the OTM task page: {0}'.format(sys.exc_info()[0]))
        return None
    try:
        taskSoup = BeautifulSoup(task_r.text, 'html.parser')
        status = taskSoup.find(class_ = 'status').find('i')['title']
    except:
        logging.error('Failed to read the OTM task html (or locate the status tag): {0} \n\n html data: {1}'.format(sys.exc_info()[0], ''))
        return None
    return status

def getBboxImage(lat_min, lon_min, lat_max, lon_max, TMSurl, zoom, filename):
    x_min_t, y_min_t = deg2num(lat_min, lon_min, zoom)
    x_max_t, y_max_t = deg2num(lat_max, lon_max, zoom)

    x_min = min(x_min_t, x_max_t)
    x_max = max(x_min_t, x_max_t)
    y_min = min(y_min_t, y_max_t)
    y_max = max(y_min_t, y_max_t)

    taskWidth  = x_max - x_min + 1
    taskHeight = y_max - y_min + 1

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
    # Now crop the image to correspond to the exact bounding box (as opposed to the tiled boundaries)
    x_f, y_f = deg2float(lat_min, lon_min, zoom = 18)
    offset_X_top = int((x_f - int(x_f)) * 256.0)
    offset_Y_top = int((y_f - int(y_f)) * 256.0)
    x_f, y_f = deg2float(lat_max, lon_max, zoom = 18)
    offset_X_bottom = int((1 - (x_f - int(x_f))) * 256.0)
    offset_Y_bottom = int((1 - (y_f - int(y_f))) * 256.0)
    completeImage = completeImage.crop((offset_X_top, offset_Y_top, \
                                        completeImage.size[0] - offset_X_bottom, completeImage.size[1] - offset_Y_bottom))
    # Save the image
    try:
        completeImage.save(filename)
    except:
        logging.error('Saving the composite image failed: {0} \n\n image filename: {1}'.format(sys.exc_info()[0], completeFileName))
        return False
    else:
        logging.info('Downloaded task map to ' + filename)
        return True

def getTaskImage(projectID, taskID, TMSurl, zoom=18):
    '''
    Downloads all tiles belonging to an OSM task and joins them into one image.
    :param projectID:
    :param taskID:
    :param TMSurl: The base-url for the slippy map server, like so: http://domain.net/hot/1.0.0/caracol-flipped/{z}/{x}/{y}.png
    :param zoom:
    :return: True if success, False otherwise
    '''
    (lat_min, lon_min, lat_max, lon_max), (x_min, y_min, x_max, y_max) = \
        getTaskBoundaries(projectID, taskID, zoom)
    taskWidth  = x_max - x_min + 1
    taskHeight = y_max - y_min + 1
    logging.info('Found bounding box {0},{1} - {2},{3}, comprising {4} TMS/slippy map tiles'.format(lat_min, lon_min, lat_max, lon_max, taskWidth * taskHeight))

    folder = 'osm-hot-images'
    if not os.path.exists(folder): os.makedirs(folder)
    completeFileName = folder + '/project{0}task{1}_complete.png'.format(str(projectID), str(taskID))
    return getBboxImage(lat_min, lon_min, lat_max, lon_max, TMS_url, zoom, completeFileName)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, encoding='UTF-8')

    HELPTEXT = 'getTaskData.py -p <HOT OSM project ID> -u <affiliated TMS url> [-t <taskID>]'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:u:t:h",["project=","tmsurl=","task="])
    except getopt.GetoptError:
        print HELPTEXT
        sys.exit(2)

    project_id, TMS_url = None, None
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

    print "Project {0} metadata:".format(str(project_id))
    meta = getProjectMeta(project_id)
    print json.dumps(meta, indent=4, sort_keys=True)

    if task_ids is None:
        print "No task specified. Trying all tasks starting at 0 (until 10 failures, assuming incremental numbering)"
        numFails = 0
        t_id = 0
        while numFails < 10:
            print "### Task {0} status:".format(str(t_id))
            print getTaskStatus(project_id, t_id)

            print "### getting task image...", t_id
            success = getTaskImage(project_id, t_id, TMS_url)
            print ' Success' if success else ' FAILED.'
            numFails = numFails + 1 if not success else 0
            t_id += 1
    else:
        for t_id in task_ids:
            print "### Task {0} status:".format(str(t_id))
            print getTaskStatus(project_id, t_id)

            print "### getting task...", t_id,
            success = getTaskImage(project_id, t_id, TMS_url)
            print ' Success' if success else ' FAILED.'
