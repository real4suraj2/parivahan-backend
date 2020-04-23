from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from .forms import VehicleForm
from main.brain.brain import brain
# Create your views here.

def homepage(request):
	error = ''
	if request.method == 'POST': 
		form = VehicleForm(request.POST, request.FILES) 
		if form.is_valid(): 
			vehicle_no = form.cleaned_data.get('vehicle_no')
			try: 
				vehicle_img = request.FILES['vehicle_img']
			except:
				vehicle_img = None
			if vehicle_no or vehicle_img : 
				form.save()
				if vehicle_no:
					res = brain(number = vehicle_no)
				if vehicle_img:
					res = brain(img_name = vehicle_img.name)
					#print(vehicle_img.name)
				if res == 'operation_success':
					return redirect('main:result')
			if res == 'operation_failed':
				error = 'Please try with other clear input images'
			else :
				error = "Please provide at least one of the inputs"
	else: 
		form = VehicleForm() 
	return render(request = request, template_name = 'main/home.html', context = {'form' : form, 'error' : error}) 
	
def result(request):
	return render(request = request, template_name = 'main/reg_details.html', context = {})

def test(request):
	return HttpResponse("<h1>Test Passed</h1>")
