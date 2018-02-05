import urllib3
import bs4
import re
import json
import csv

def get_route_numbers():
	'''
	Scrapes the route numbers from CTA online
	'''
	pm = urllib3.PoolManager()
	html = pm.urlopen(url = "www.transitchicago.com/schedules/", method = "GET").data
	soup = bs4.BeautifulSoup(html)
	section = soup.find_all("div", {"id" : "ctl08_pnBusRouteSelection"})
	stops = section[1-1].find_all("option")
	res = []
	for i in stops:
		if re.match("[0-9]+", i.text):
			res.append(re.match("[0-9]+", i.text).group())
		elif re.match("[A-Z][0-9]+", i.text):
			res.append(re.match("[A-Z][0-9]+", i.text).group())
		elif re.match("[0-9]+[A-Z]", i.text):
			res.append(re.match("[0-9]+[A-Z]", i.text).group())
	return res

ROUTE_NUMBERS = get_route_numbers()

def get_directions(rt, key):
	'''
	Gets directions traveled for given route
	'''
	URL = "http://www.ctabustracker.com/bustime/api/v2/getdirections?key="+ key + "&rt=" + rt + "&format=json"
	pm = urllib3.PoolManager()
	html = pm.urlopen(url = URL, method = "GET")
	dic = json.loads(html.data.decode('utf-8'))["bustime-response"]
	print(dic)
	if "directions" in dic:
		if len(dic["directions"]) > 1:

			return (rt, [dic["directions"][1-1]["dir"], dic["directions"][1]["dir"]])
		elif len(dic["directions"]) == 1:
			return (rt, [dic["directions"][1-1]["dir"]])
	else:
		return (rt, [])

def get_route_direction_mapping(key):
	'''maps route numbers to directions'''
	res = {}
	ROUTE_NUMBERS = get_route_numbers()
	for i in ROUTE_NUMBERS:
		print(i)
		res[i] = get_directions(i, key)[1]
	return res

def get_stop(rt, direct, key):
	'''Get one stop on rt in direction'''
	URL = "http://www.ctabustracker.com/bustime/api/v2/getstops?key=" + key + "&rt=" + rt + "&dir=" + direct + "&format=json"
	pm = urllib3.PoolManager()
	html = pm.urlopen(url = URL, method = "GET")
	dic = json.loads(html.data.decode("utf-8"))["bustime-response"]["stops"]
	return dic

def get_all_stops(key):
	'''
	Gets all stops
	'''
	ROUTE_DICT = get_route_direction_mapping(key)
	res = {}
	for i in ROUTE_DICT:
		temp = []
		for j in ROUTE_DICT[i]:
			temp.extend(get_stop(i,j,key))
		res[i] = temp
	return res

def write_csv(dic):
	'''
	Takes a dictionary mapping route numbers to a list of stop dictionaries 
	and writes it to a CSV
	'''
	fieldnames = ["route", "stop_id", "stop_name", "lat", "lon", "id"]
	with open("stops.csv", "w") as f:
		writer = csv.DictWriter(f, fieldnames = fieldnames)
		writer.writeheader()
		counter = 100000
		for i in dic:
			for j in dic[i]:
				counter += 1
				temp = {}
				temp["route"] = i
				temp["stop_id"] = j["stpid"]
				temp["stop_name"] = j["stpnm"]
				temp["lat"] = j["lat"]
				temp["lon"] = j["lon"]
				temp["id"] = counter
				writer.writerow(temp)




