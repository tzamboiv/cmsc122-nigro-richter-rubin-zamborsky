from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views import View

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
		return render(request, 'travelprefs/results.html', {'content':[('Did','this'),('this','work')]})


