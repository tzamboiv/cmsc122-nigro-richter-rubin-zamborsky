import sqlite3
from math import radians, cos, sin, asin, sqrt
import googlemaps
from datetime import datetime
import requests
import travel_times
from travel_times import haversine
from travel_times import find_address_coords
from travel_times import check_if_in_range

#transit_inputs = dict of {transit type : ranking}
#transit type = "divvy", "cta", "shuttles", "driving", "bicycling", "walking"
#ranking = "none", "low", "medium", "high"

#this function: walking, driving, biking, cta
#to do manually: divvy, shuttles

#nested dictionary of transit type to time and ranking; if ranking = none, not included in dict
def time_to_dest(address, address_coords, poi, transit_inputs, gmaps):
	returns = {}
	for transit_type, ranking in transit_inputs.items():
		if ranking != "none" and transit_type != "divvy" and transit_type != "shuttles":
			if transit_type == "cta":
				mode = "transit"
			else:
				mode = transit_type
			output = gmaps.distance_matrix(origins=address, destinations=poi["formatted_address"], mode=mode)
			returns[transit_type] = {}
			returns[transit_type]["time"] = output['rows'][0]['elements'][0]['duration']['value']
			returns[transit_type]["ranking"] = ranking
			returns[transit_type]["notes"] = poi["name"]
	return returns


def get_divvy_travel_times(address, address_coords, transit_inputs, gmaps):
	db = sqlite3.connect("transit.db")
	c = db.cursor()
	r = c.execute("SELECT station_name, lat, lon FROM divvy;")
	divvy_stops = r.fetchall()
	db.close()
	nearest_stops = []
	for stop in divvy_stops[1:]:
		nearest_stops.append([haversine(stop[1], stop[2], address_coords[0], address_coords[1]), stop])
	stops_of_interest = sorted(nearest_stops)[0:10]
	stop_coords = [stop[1] for stop in stops_of_interest]
	routes = []
	dest_coords = []
	for stop in stop_coords:
		routes.append((stop[0], (stop[1], stop[2])))
		dest_coords.append((stop[1], stop[2]))
	query_return = gmaps.distance_matrix(origins=address, destinations=dest_coords, mode="walking")
	walk_times = {}
	for i, route in enumerate(query_return["rows"][0]["elements"]):
		walk_times[routes[i]] = {}
		walk_times[routes[i]]["time"] = route["duration"]["value"]
	return walk_times


def divvy_time_to_dest(address, poi, transit_inputs, gmaps):
	poi_nearest_divvy_stops = get_divvy_travel_times(poi["formatted_address"], (poi["geometry"]["location"]["lat"], poi["geometry"]["location"]["lng"]), transit_inputs, gmaps)
	closest_poi_stop = sorted([(poi_nearest_divvy_stops[p]['time'], p) for p in poi_nearest_divvy_stops])[0]
	divvy_input = {"divvy" : transit_inputs["divvy"], "shuttles" : "none", "cta" : "none"}
	address_nearest_divvy_stops = travel_times.go(address, divvy_input)['divvy']
	closest_address_stop = sorted([(address_nearest_divvy_stops[p]['time'], p) for p in address_nearest_divvy_stops])[0]
	output = gmaps.distance_matrix(origins=closest_address_stop[1][1], destinations=closest_poi_stop[1][1], mode="bicycling")
	divvy_dict = {}
	divvy_dict["time"] = output['rows'][0]['elements'][0]['duration']['value'] + closest_address_stop[0] + closest_poi_stop[0]
	divvy_dict["ranking"] = transit_inputs['divvy']
	divvy_dict["notes"] = (closest_address_stop[1][0], closest_poi_stop[1][0])
	return divvy_dict


def go(address, poi_query, transit_inputs):
	api_key="AIzaSyB6jVa5oN8mBp8kna3l8obDYsqrb1ja6EE"
	gmaps = googlemaps.Client(key=api_key)
	address_coords = find_address_coords(address, gmaps)
	if not check_if_in_range(address_coords):
		return "Error: address not in Hyde Park"
	poi = gmaps.places(poi_query, address_coords)["results"][0]
	output_dict = time_to_dest(address, address_coords, poi, transit_inputs, gmaps)
	output_dict["divvy"] = divvy_time_to_dest(address, poi, transit_inputs, gmaps)
	return output_dict