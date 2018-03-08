from django.db import models

# Create your models here.
class Address(models.Model):
	streetad = models.TextField()
	zipcode = models.IntegerField()

class Preferences(models.Model):
	transitpref = models.CharField(max_length=500)
	destpref = models.CharField(max_length=500)
	interests = models.TextField()

class POI(models.Model):
	poi_ad = models.TextField()

class All(models.Model):
	streetad = models.TextField(default = "none")
	poi = models.TextField(default = "none")
	divvy = models.TextField(default = "none")
	cta = models.TextField(default = "none")
	shuttles = models.TextField(default = "none")
	driving = models.TextField(default = "none")
	bicycling = models.TextField(default = "none")
	walking = models.TextField(default = "none")
	downtown = models.TextField(default = "netiher")

