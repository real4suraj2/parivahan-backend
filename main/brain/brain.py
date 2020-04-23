import pytesseract
import argparse
import os
import sys
import requests
import shutil
import cv2
import imutils
import numpy as np
import json
from bs4 import BeautifulSoup, SoupStrainer
import pdfkit
from django.conf import settings

uri = 'http://mis.mptransport.org/MPLogin/eSewa/VehicleSearch.aspx'
def brain(img_name = None, number = None):
	if number == None:
		img = cv2.imread(os.path.join(settings.VEHICLE_DIR, img_name))
		img = imutils.resize(img, width = 500)
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		gray = cv2.bilateralFilter(gray, 11, 17, 17)
		edged = cv2.Canny(gray, 170, 200)
		
		contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		contours = sorted(contours, key = cv2.contourArea, reverse = True)[:30]
		
		possible_contours = []

		for c in contours:
			peri = cv2.arcLength(c, True)
			approx = cv2.approxPolyDP(c, 0.02 * peri, True)
			if len(approx) == 4: 
				possible_contours.append(approx)
		
		for idx in range(len(possible_contours)):		
			mask = np.zeros_like(gray) 
			cv2.drawContours(mask, possible_contours, idx, 255, -1) 
			out = np.zeros_like(gray)
			out[mask == 255] = gray[mask == 255]
			cv2.imwrite(os.path.join(settings.OUTPUT_DIR,'output' + str(idx) + '.jpeg'), out)
		
		for idx in range(len(possible_contours)):
			img = cv2.imread(os.path.join(settings.OUTPUT_DIR,'output' + str(idx) + '.jpeg'))
			kernel = np.ones((2,2), np.uint8)
			img_erosion = cv2.erode(img, kernel, iterations=1)
			img_dilation = cv2.dilate(img_erosion, kernel, iterations=1)
			erosion_again = cv2.erode(img_dilation, kernel, iterations=1)
			img = cv2.GaussianBlur(erosion_again, (1, 1), 0)
			img = (255 - img)
			cv2.imwrite(os.path.join(settings.PREPROCESSED_DIR,'preprocessed.jpeg'), img)
			number = pytesseract.image_to_string(img).replace(" ",'').replace("\n", '').replace(".",'')
			if len(number) == 10 :
				break
		
		if(len(number) != 10):
			print("Operation Failed !!")
			return "operation_failed";

	print(number)

	s = requests.Session()
	r = s.get(url = uri)
	soup = BeautifulSoup(r.text, 'html.parser')

	vs1 = soup.select('input[id="__VIEWSTATE"]')[0]['value']
	ev1 = soup.select('input[id="__EVENTVALIDATION"]')[0]['value']

	data1 = {
		'ctl00$ScriptManager1':"ctl00$ContentPlaceHolder1$updatePanel|ctl00$ContentPlaceHolder1$btnShow",
		'__EVENTTARGET': "",
		'__EVENTARGUMENT':"",
		'__VIEWSTATE': vs1,
		'__VIEWSTATEENCRYPTED':"",
		'__EVENTVALIDATION':ev1,
		'ctl00$ContentPlaceHolder1$txtRegNo':number,
		'ctl00$ContentPlaceHolder1$txtEngineNo':"",
		'ctl00$ContentPlaceHolder1$txtchassis':"", 
		'ctl00$ContentPlaceHolder1$RadioButtonList1': "EXT",
		'ctl00$ContentPlaceHolder1$ddlNavigationPage':"GenericDetails",
		'ctl00$ContentPlaceHolder1$hdSortBy':"",
		'ctl00$ContentPlaceHolder1$hdSortOrd':"",
		'__ASYNCPOST': "false",
		'ctl00$ContentPlaceHolder1$btnShow':"Submit",
	}

	res = s.post(url = uri, data = data1)
	rsoup = BeautifulSoup(res.text, 'html.parser')

	vs2 = rsoup.select('input[id="__VIEWSTATE"]')[0]['value']
	ev2 = rsoup.select('input[id="__EVENTVALIDATION"]')[0]['value']

	data2 = {
		'ctl00$ScriptManager1': 'ctl00$ContentPlaceHolder1$updatePanel|',
		'ctl00$ContentPlaceHolder1$txtRegNo': number,
		'ctl00$ContentPlaceHolder1$txtEngineNo': '',
		'ctl00$ContentPlaceHolder1$txtchassis': '',
		'ctl00$ContentPlaceHolder1$RadioButtonList1': 'EXT',
		'ctl00$ContentPlaceHolder1$ddlNavigationPage': 'GenericDetails',
		'ctl00$ContentPlaceHolder1$hdSortBy': 'VEH_REGN_NO',
		'ctl00$ContentPlaceHolder1$hdSortOrd': 'Asc',
		'__EVENTTARGET': 'ctl00$ContentPlaceHolder1$grvSearchSummary',
		'__EVENTARGUMENT': 'Select$0',
		'__VIEWSTATE': vs2,
		'__VIEWSTATEENCRYPTED': '',
		'__EVENTVALIDATION': ev2,
		'__ASYNCPOST': 'false',
	}

	res = s.post(url = uri, data = data2)
	rsoup = BeautifulSoup(res.text, 'html.parser')

	for link in rsoup.find_all('a'):
		link.attrs['hidden'] = 'true'

	for btn in rsoup.find_all('input'):
		btn.attrs['hidden'] = 'true'

	#As html
	with open(os.path.join(settings.RESULT_DIR,"reg_details.html"), "w") as f:
		f.write(rsoup.prettify())
	
	try:	
		shutil.rmtree(settings.OUTPUT_DIR)
		shutil.rmtree(settings.PREPROCESSED_DIR)
	except:
		os.mkdir(settings.OUTPUT_DIR)
		os.mkdir(settings.PREPROCESSED_DIR)
	
	try:
		os.mkdir(settings.OUTPUT_DIR)
		os.mkdir(settings.PREPROCESSED_DIR)
	except:
		pass
	
	return "operation_success"
	#As pdf from html
	#pdfkit.from_file('reg_details.html', 'reg_details.pdf')