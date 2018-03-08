from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

from .forms import HomeForm

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
		return HttpResponseRedirect(request.path_info)


