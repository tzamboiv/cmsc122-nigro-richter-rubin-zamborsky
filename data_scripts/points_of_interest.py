import sqlite3
from math import radians, cos, sin, asin, sqrt
import googlemaps
from datetime import datetime
import requests

#transit_inputs = dict of {transit type : ranking}
#transit type = "walking", "transit", "biking"
#ranking = "none", "low", "medium", "high"
def time_to_dest(address, dest_address, transit_inputs, gmaps):
	returns = {}
	for transit_type, ranking in transit_inputs.items():
		if ranking != "none":
			output = gmaps.distance_matrix(origins=address, destinations=dest_address, mode=transit_type)
			returns[transit_type] = output['rows'][0]['elements'][0]['duration']['value']
	return returns

def go(address, dest_address, inputs):
	api_key="AIzaSyB6jVa5oN8mBp8kna3l8obDYsqrb1ja6EE"
	gmaps = googlemaps.Client(key=api_key)
	return time_to_dest(address, dest_address, inputs, gmaps)