import sqlite3
from math import radians, cos, sin, asin, sqrt
import googlemaps
from datetime import datetime
import requests

def haversine(lat1, lon1, lat2, lon2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m


def find_address_coords(address, gmaps):
	coords = gmaps.geocode(address)[0]["geometry"]["bounds"]
	lat = (coords["northeast"]["lat"] + coords["southwest"]["lat"]) / 2
	lon = (coords["northeast"]["lng"] + coords["southwest"]["lng"]) / 2
	return (lat, lon)


def format_data_query(lat_range, lon_range, address, address_coords, gmaps, query_type):
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
		walk_times[routes[i]] = route["duration"]["value"]
	return walk_times

#Still need to manually categorize downtown vs. hyde park stops

def go(address, transit_inputs):
	api_key="AIzaSyB6jVa5oN8mBp8kna3l8obDYsqrb1ja6EE"
	gmaps = googlemaps.Client(key=api_key)
	address_coords = find_address_coords(address, gmaps)
	#Hyde Park + Kenwood area
	lat_range = (41.765605, 41.812444)
	lon_range = (-87.625826, -87.583701)
	if address_coords[0] < lat_range[0] or address_coords[0] > lat_range[1] or address_coords[1] < lon_range[0] or address_coords[1] > lon_range[1]:
		return ("Error: Invalid Address")

	output = {}
	transit_types = []
	if transit_inputs["bicycling"] != "none":
		transit_types.append("divvy")
	if transit_inputs["transit"] != "none":
		transit_types.extend(["shuttles", "cta"]) 
	for query_type in transit_types:
		output[query_type] = format_data_query(lat_range, lon_range, address, address_coords, gmaps, query_type)
	return output
