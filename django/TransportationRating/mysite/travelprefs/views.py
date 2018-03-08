from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views import View
import sqlite3
import googlemaps
import ratings
import travel_times

from .forms import HomeForm
#from .models import All

# Create your views here.
class HomeView(TemplateView):
	template_name = 'travelprefs/home.html'

	def get(self, request):
		form = HomeForm()
		return render(request, self.template_name, {'form': form})

	def post(self, request):
		form = HomeForm(request.POST)
		if form.is_valid():
			form.save()
			form = HomeForm()
		return HttpResponseRedirect('/results')

class ResultsView(View):

	def get(self, request):
		
		inputs = get_dict()
		is_in_hp = True
		api_key="AIzaSyB6jVa5oN8mBp8kna3l8obDYsqrb1ja6EE"
		gmaps = googlemaps.Client(key=api_key)
		for i in inputs[0]:
			address_coords = travel_times.find_address_coords(i, gmaps)
			hp_range = travel_times.check_if_in_range(address_coords)
			if not hp_range:
				is_in_hp = False
				break
		if is_in_hp:
			res = ratings.compute_rankings(inputs)
			tups = sorted([(val, key) for key, val in res.items()])
			rv = []
			for i, x in enumerate(tups):
				rv.append((str(i + 1) + ".", x[1] ))
		else:
			rv = [("Error: ", "Address not in Hyde Park")]


		return render(request, 'travelprefs/results.html', {'content':rv})

DB_NAME = "db.sqlite3"

def get_dict():
	order = " streetad, poi, divvy, cta, shuttles, driving, bicycling, walking, downtown, southside "
	db = sqlite3.connect(DB_NAME)
	cursor = db.cursor()
	res = cursor.execute("select" + order+ "from travelprefs_all").fetchall()
	N = len(res) - 1
	info = res[N]
	adds = info[0].split(";")
	poi = info[1].split(";")
	pref = {"divvy" : info[2],
			"cta" : info[3],
			"shuttles" : info[4],
			"driving" : info[5],
			"bicycling": info[6],
			"walking" : info[7]
			}

	
	return (adds, poi, pref, info[8], info[9])




