from django.db import models

# Create your models here.
class Address(models.Model):
	streetad = models.TextField()
	zipcode = models.IntegerField()

class Preferences(models.Model):
	transitpref = models.CharField(max_length=500)
	destpref = models.CharField(max_length=500)
	interests = models.TextField()