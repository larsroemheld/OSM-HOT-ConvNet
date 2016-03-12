'''
Gets data for a specified Open Street Map (OSM) Task Manager (OTM) task, esp. for HOT (Humanitarian OSM Team) and mapgive.
Gets OSM map data for a specified task area.

Lars Roemheld, roemheld@stanford.edu
'''
__author__ = 'Lars Roemheld'

import requests
import logging
import json
import getTaskData
from collections import Counter

def getOsmMapData_bbox(lat_min, lon_min, lat_max, lon_max):
    '''
    Pull relevant OSM map data for the given bounding box. Nodes and ways are downloaded and returned as a python object (from json).
    The object contains an 'elements' list of nodes and ways.
    Note: The query used here ignores ways (everything that is not a point! Not only roads) which do not have nodes
    within the bounding box. This could potentially be problematic, but the alternative (including all ways) may blow
    up the map size (since potentially long ways may have to be downloaded)
    :param lat_min:
    :param lon_min:
    :param lat_max:
    :param lon_max:
    :return: Python object, or None if failed
    '''
    if lat_min > lat_max: lat_min, lat_max = lat_max, lat_min #swap.
    if lon_min > lon_max: lon_min, lon_max = lon_max, lon_min #swap.
    OVERPASS_URL = 'http://overpass-api.de/api/interpreter'
    #Bounding box clauses always start with the lower latitude followed by lower longitude, then upper latitude then upper longitude. Note that this is different from the ordering in the XAPI syntax.
    #http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide
    overpassQuery =  '[out:json];'
    overpassQuery +=  '(node('
    overpassQuery += ','.join([str(lat_min), str(lon_min), str(lat_max), str(lon_max)])
    overpassQuery += ');<;);out;'
    try:
        r = requests.get(OVERPASS_URL, params={'data': overpassQuery})
    except:
        logging.error('Could not reach the overpass api at '+OVERPASS_URL + ". query: " + overpassQuery)
        return None
    try:
        map_data = json.loads(r.text)
    except:
        logging.error('Could not read the overpass api result (query error?): '+r.text)
        return None

    map_data['bbox_latlong'] = {'lat_min': lat_min, 'lon_min': lon_min, 'lat_max': lat_max, 'lon_max': lon_max}
    return map_data

def getOsmMapData(projectID, taskID):
    '''
    A small helper to get OSM map data for a specific OTM task (see comments in getTaskBoundaries and getOsmMapData_bbox)
    '''
    (lat_min, lon_min, lat_max, lon_max), _ = \
        getTaskData.getTaskBoundaries(projectID, taskID)
    return getOsmMapData_bbox(lat_min, lon_min, lat_max, lon_max)

def osmMapHasTag(mapData, tagKey, tagValue=None):
    for e in mapData['elements']:
        tags = e.get('tags')
        if tags is not None:
            if tagKey in tags.keys():
                if tagValue is None or tags[tagKey] == tagValue:
                    return True
    return False


def osmTaskHasTag(projectID, taskID, tagKey, tagValue=None):
    '''
    Boolean whether the current OSM map data for a task contains specific tags. If tagValue is None, only existence of
    the tagKey is checked. Note that key:value is case-sensitive!
    '''
    map_obj = getOsmMapData(projectID, taskID)
    if map_obj is None: raise # no good way to recover: true/false/none will all bias the data
    osmMapHasTag(map_obj, tagKey, tagValue)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    project = 1080
    task = 51
    print getTaskData.getTaskBoundaries(project, task)
    map_obj = getOsmMapData(project, task)
    # x, y = 78633, 116459
    # nw_lat, nw_lon = getTaskData.num2deg(x, y, 18)
    # se_lat, se_lon = getTaskData.num2deg(x+1, y+1, 18)
    # print se_lat, nw_lon, nw_lat, se_lon
    # map_obj = getOsmMapData_bbox(nw_lat, nw_lon, se_lat, se_lon)
    print json.dumps(map_obj, indent=4, sort_keys=True)

    map_nodes     = [e for e in map_obj['elements'] if e['type'] == 'node']
    map_ways      = [e for e in map_obj['elements'] if e['type'] == 'way']
    map_relations = [e for e in map_obj['elements'] if e['type'] == 'relation']

    map_nodes_tags     = [e for e in map_nodes if e.get('tags') is not None]
    map_ways_tags      = [e for e in map_ways if e.get('tags') is not None]
    map_relations_tags = [e for e in map_relations if e.get('tags') is not None]

    print "{0} elements in total".format(len(map_obj['elements']))
    print "- Thereof {0} nodes, {1} of which have tags".format(len(map_nodes), len(map_nodes_tags))
    print "- Thereof {0} ways, {1} of which have tags".format(len(map_ways), len(map_ways_tags))
    print "- Thereof {0} relations, {1} of which have tags".format(len(map_relations), len(map_relations_tags))

    map_tags = [e for e in map_obj['elements'] if e.get('tags') is not None]
    tag_counts = Counter()
    for o in map_tags:
        for t in o['tags'].keys():
            tag_counts[t] += 1

    print 'Included tags:'
    print tag_counts

    print "'building's included?': ", osmMapHasTag(project, task, 'building')