from django import forms
from .models import Address, Preferences

class HomeForm(forms.ModelForm):
	streetad = forms.CharField()
	zipcode = forms.IntegerField()

	class Meta:
		model = Address
		fields = ('streetad','zipcode')
