from django import forms
from .models import Address, Preferences, All

class HomeForm(forms.ModelForm):
	streetad = forms.CharField(label = "Addresses: Separate By Semicolons", required = True, initial = " ")
	poi = forms.CharField(label = "Points of Interest: Separate By Semicolons", required = False, initial = " ")
	divvy = forms.ChoiceField(label = "Divvy", choices = [("high", "High") ,("medium", "Medium"),("low", "Low"), ("none", "None")])
	cta = forms.ChoiceField(label = "CTA Buses", choices = [("high", "High") ,("medium", "Medium"),("low", "Low"), ("none", "None")])
	shuttles = forms.ChoiceField(label = "UChicago Shuttles", choices = [("high", "High") ,("medium", "Medium"),("low", "Low"), ("none", "None")])
	driving = forms.ChoiceField(label = "Driving", choices = [("high", "High") ,("medium", "Medium"),("low", "Low"), ("none", "None")])
	bicycling = forms.ChoiceField(label = "Biking", choices = [("high", "High") ,("medium", "Medium"),("low", "Low"), ("none", "None")])
	walking = forms.ChoiceField(label = "Walking", choices = [("high", "High") ,("medium", "Medium"),("low", "Low"), ("none", "None")] )
	downtown = forms.ChoiceField(label = "Downtown or Hyde Park", choices = [("hyde_park", "Hyde Park") ,("neither", "Neither") , ("downtown", "Downtown")])
	southside = forms.ChoiceField(label = "South of Hyde Park", choices = [("no", "No") , ("yes", "Yes")])

	class Meta:
		model = All
		fields = ("streetad", "poi", "divvy", "cta", "shuttles", "driving", "bicycling", "walking", "downtown", "southside")
	"""	class Meta:
		model = Address
		fields = ('streetad','zipcode')"""


