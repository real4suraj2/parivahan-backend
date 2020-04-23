from django.db import models

# Create your models here.

class Vehicle(models.Model): 
	vehicle_no = models.CharField(max_length=10, blank = True, default = '') 
	vehicle_img = models.ImageField(upload_to='vehicles/', blank = True) 