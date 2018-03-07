from django import forms
from .models import Address, Preferences, All

class HomeForm(forms.ModelForm):
	streetad = forms.CharField(label = "Addresses", required = True, initial = "Separate by semicolons")
	poi = forms.CharField(label = "Points of Interest", required = False, initial = "Separate by semicolons")
	divvy = forms.ChoiceField(label = "Divvy", choices = [("high", "High") ,("medium", "Medium"),("low", "Low"), ("none", "None")])
	cta = forms.ChoiceField(label = "CTA Buses", choices = [("high", "High") ,("medium", "Medium"),("low", "Low"), ("none", "None")])
	shuttles = forms.ChoiceField(label = "UChicago Shuttles", choices = [("high", "High") ,("medium", "Medium"),("low", "Low"), ("none", "None")])
	driving = forms.ChoiceField(label = "Driving", choices = [("high", "High") ,("medium", "Medium"),("low", "Low"), ("none", "None")])
	bicycling = forms.ChoiceField(label = "Biking", choices = [("high", "High") ,("medium", "Medium"),("low", "Low"), ("none", "None")])
	walking = forms.ChoiceField(label = "Walking", choices = [("high", "High") ,("medium", "Medium"),("low", "Low"), ("none", "None")] )

	class Meta:
		model = All
		fields = ("streetad", "poi", "divvy", "cta", "shuttles", "driving", "bicycling", "walking")
	"""	class Meta:
		model = Address
		fields = ('streetad','zipcode')"""

