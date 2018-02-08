import json
import csv

routes = None
with open("shuttle_routes.json") as f:
	routes = json.load(f)

routes = routes["data"]["100"]
route_dict = {}
for r in routes:
	route_dict[r["route_id"]] = r["long_name"]

stops = None
with open("shuttle_stops.json") as f:
	stops = json.load(f)

stops = stops["data"]
stops_info = {}
for s in stops:
	stops_info[s["name"]] = {"lat" : s["location"]["lat"], "lng" : s["location"]["lng"], "routes" : [route_dict[r_id] for r_id in s["routes"]]}

with open("shuttle_data.csv", "w") as f:
	writer = csv.DictWriter(f, fieldnames = ["stop_name", "latitude", "longitude", "routes"])
	writer.writeheader()

	for stop in stops_info.keys():
		row = {}
		row["stop_name"] = stop
		row["latitude"] = stops_info[stop]["lat"]
		row["longitude"] = stops_info[stop]["lng"]
		row["routes"] = ", ".join(stops_info[stop]["routes"])
		writer.writerow(row)
