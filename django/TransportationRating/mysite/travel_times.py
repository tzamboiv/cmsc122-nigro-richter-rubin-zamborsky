import sqlite3
from math import radians, cos, sin, asin, sqrt
import googlemaps
from datetime import datetime
import requests


def haversine(lat1, lon1, lat2, lon2):
    '''
    Computes haversine distance between two points
    '''
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    a = sin((lat2 - lat1) / 2)**2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2)**2
    circ = 2 * asin(sqrt(a))
    return 6367 * circ * 1000


def find_address_coords(address, gmaps):
	'''
	Converts address to latitude and longitute
	'''
	coords = gmaps.geocode(address)[0]["geometry"]["location"]
	return (coords['lat'], coords['lng'])



def get_travel_times(lat_range, lon_range, address, address_coords, gmaps, query_type):
	'''
	Computes walking time from address to nearby transit of type query_type
	'''
	db = sqlite3.connect("transit.db")
	c = db.cursor()
	if query_type == "divvy":
		identifier = "station_name"
	elif query_type == "shuttles" or query_type == "cta":
		identifier = "route"
	r = c.execute("SELECT {}, lat, lon FROM {} WHERE (lat BETWEEN {} AND {}) AND (lon BETWEEN {} AND {});".format(identifier, query_type, lat_range[0], lat_range[1], lon_range[0], lon_range[1]))
	stop_coords = r.fetchall()
	db.close()
	route_dict = {}
	dist_dict = {}
	for row in stop_coords[0:]:
		dist = haversine(address_coords[0], address_coords[1], row[1], row[2])
		if row[0] in route_dict.keys():
			if dist < dist_dict[row[0]]:
				route_dict[row[0]] = (row[1], row[2])
				dist_dict[row[0]] = dist
		else:
			route_dict[row[0]] = (row[1], row[2])
			dist_dict[row[0]] = dist
	routes = []
	dest_coords = []
	for route, coord in route_dict.items():
		routes.append(route)
		dest_coords.append(coord)
	query_return = gmaps.distance_matrix(origins=address, destinations=dest_coords, mode="walking")
	walk_times = {}
	for i, route in enumerate(query_return["rows"][0]["elements"]):
		walk_times[routes[i]] = {}
		walk_times[routes[i]]["time"] = route["duration"]["value"]
		walk_times[routes[i]]["coords"] = dest_coords[i]
	return walk_times


def check_if_in_range(address_coords):
	'''
	Checks if address in Hyde Park/Kenwood
	'''
	#Hyde Park + Kenwood area
	lat_range = (41.765605, 41.812444)
	lon_range = (-87.625826, -87.583701)
	if address_coords[0] < lat_range[0] or address_coords[0] > lat_range[1] or address_coords[1] < lon_range[0] or address_coords[1] > lon_range[1]:
		return False
	return lat_range, lon_range


def go(address, transit_inputs):
	'''
	Computes walking times to all transit types from transit_inputs
	'''
	api_key="AIzaSyB6jVa5oN8mBp8kna3l8obDYsqrb1ja6EE"
	gmaps = googlemaps.Client(key=api_key)
	address_coords = find_address_coords(address, gmaps)
	hp_range = check_if_in_range(address_coords)
	if not hp_range:
		return ("Error: address not in Hyde Park")
	lat_range = hp_range[0]
	lon_range = hp_range[1]
	output = {}
	transit_types = []
	for mode in ["divvy", "shuttles", "cta"]: 
		if transit_inputs[mode] != "none":
			transit_types.append(mode) 
	for query_type in transit_types:
		output[query_type] = get_travel_times(lat_range, lon_range, address, address_coords, gmaps, query_type)
		for stop, info in output[query_type].items():
			output[query_type][stop]["ranking"] = transit_inputs[query_type]
	return output
