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
        logging.error('Could not reach the overpass api at '+OVERPASS_URL)
        return None
    try:
        map_data = json.loads(r.text)
    except:
        logging.error('Could not read the overpass api result (query error?): '+r.text)
        return None

    return map_data

def getOsmMapData(projectID, taskID, zoom=18):
    '''
    A small helper to get OSM map data for a specific OTM task (see comments in getTaskBoundaries and getOsmMapData_bbox)
    '''
    (lat_min, lon_min, lat_max, lon_max), _ = \
        getTaskData.getTaskBoundaries(projectID, taskID, zoom)
    return getOsmMapData_bbox(lat_min, lon_min, lat_max, lon_max)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    project = 1080
    task = 51

    map_obj = getOsmMapData(project, task)
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
