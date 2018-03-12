import urllib3
import json
import csv

def get_divvy_stops():
	URL = "https://feeds.divvybikes.com/stations/stations.json"
	pm = urllib3.PoolManager()
	html = pm.urlopen(url = URL, method = "GET")
	dic = json.loads(html.data.decode('utf-8'))
	return dic

def make_divvy_csv():
	fieldnames = ["id", "landmark", "lat", "lon", "station_name"]
	with open("divvy.csv","w") as f:
		writer = csv.DictWriter(f, fieldnames = fieldnames)
		writer.writeheader()
		stops = get_divvy_stops()["stationBeanList"]
		for i in stops:
			temp = {}
			temp["id"] = i["id"]
			temp["landmark"] = i["landMark"]
			temp["lat"] = i["latitude"]
			temp["lon"] = i["longitude"]
			temp["station_name"] = i["stationName"]
			writer.writerow(temp)