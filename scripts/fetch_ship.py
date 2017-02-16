# Get upcoming ship arrival and departure data, and vessel data

import os
from lxml import html
import requests
from BeautifulSoup import BeautifulSoup
import json
import pandas as pd
from datetime import datetime


def get_schedule(schedule_data_dir):
	""" Save arrival and departure data to file.
		Return db of arrival/departure events.
	"""

	# Pull existing data
	page = requests.get('https://www.nwseaportalliance.com/operations/vessels')
	soup = BeautifulSoup(page.text)

	# Fetch the schedule data from the main page
	schedule_db = {}

	# Get the vessel list and href for vessel details
	vessels = soup.findAll('td', {'class':'views-field views-field-title-1'})

	# ETA, ETD, and and Terminal Data
	eta = soup.findAll('div',{'class':'field field-name-field-vessel-eta field-type-datestamp field-label-hidden'})
	etd = soup.findAll('div', {'class':'field field-name-field-vessel-etd field-type-datestamp field-label-hidden'})
	terminal = soup.findAll('div', {'class':'field field-name-field-vessel-terminal field-type-text field-label-hidden'})
	harbor = soup.findAll('td', {'class': 'views-field views-field-field-vessel-harbor'}) 

	vessel_list = []
	href_list = []
	for i in xrange(len(vessels)):
	    vessel = vessels[i]
	    schedule_db[i] = {'vessel': vessel.findAll('a',href=True)[0].contents[0].strip(),
	                     'href': vessel.findAll('a',href=True)[0]['href'],
	                     'eta': eta[i].findAll('span')[0].contents[0].strip(),
	                     'etd': etd[i].findAll('span')[0].contents[0].strip(),
	                     'terminal': terminal[i].contents[0].split('\n')[-1].strip(),
	                     'harbor': harbor[i].contents[0].strip()}

	# Save the schedule db to file
	with open(schedule_data_dir+"/"+str(datetime.now())+".json", 'w') as fp:
	    json.dump(schedule_db, fp)

	return schedule_db

def get_vessel(vessel_data_file, schedule_db):
	"""Save vessel details, inlcuding name, size, draught"""

	# Try to load an existing vessel dict
	if os.path.isfile(vessel_data_file):
		try:
		    with open(vessel_data_file, 'r') as fp:
		        vessel_dict = json.load(fp)
		except:
		    vessel_dict = {}
	else:
		vessel_dict = {}

	# If ship doesn't already exist in our database, collect it
	for entry_id, entry in schedule_db.iteritems():
		vessel = schedule_db[entry_id]['vessel'] 

	if vessel not in vessel_dict.keys():
	    print 'adding: ' + vessel
	    vessel_dict[vessel] = {}
	    page = requests.get('https://www.nwseaportalliance.com' + schedule_db[entry_id]['href'])
	    soup = BeautifulSoup(page.text)

	    # # Get the list of class names to search
	    vessel_class_names = []
	    for field in [i['class'] for i in soup.findAll('div')[1:]]:
	        if 'field' in str(field):
	            vessel_class_names.append(field)

	    for class_name in vessel_class_names:
	        field_name = class_name.split(' ')[1].split('-')[-1]
	        field_val = soup.findAll('div', {'class':class_name})[0].contents[0].split('\n')[-1].strip()
	        vessel_dict[vessel][field_name] = field_val
	        
	with open(vessel_data_file, 'w') as fp:
		json.dump(vessel_dict, fp)

def main():

	print "retrieving schedule data"
	schedule_db = get_schedule(schedule_data_dir='../data/ship')

	print "retrieving vessel data"
	get_vessel(vessel_data_file='../data/ship/vessel_data.json', schedule_db=schedule_db)

if __name__ == '__main__':
	main()