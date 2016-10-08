#! flask/bin/python

import os
import json
from app import app
from threading import Timer
from flask import Flask, request, send_from_directory, jsonify, render_template
import pandas as pd
import folium
import vincent
from scripts import bridge_stat

# Grab info about current closures at start and update at intervals
update_interval = 150 # 2.5 minutes

bridges = {'Lower Spokane St': [47.570950, -122.348324],
          'South Park': [47.529252, -122.314316],
          'Fremont': [47.647857, -122.349867],
          'Ballard': [47.659280, -122.376163],
          'Montlake': [47.647296, -122.304577],
          'University': [47.652995, -122.320194],
          '1st Ave S': [47.542049, -122.334541]}

def update_bridge_status(interval):
	# update every minute

	Timer(interval,update_bridge_status,[interval]).start()
	# Results as df
	current_closures_df = bridge_stat.current_closures()

	print 'fetching bridge status now'
	# Check that the data looks okay. If so, save a copy locally
	current_closures_df.to_csv('data/bridge/current_closures.csv')

update_bridge_status(update_interval)
# And refresh the data being sent to 

@app.route('/')
def map():
	current_closures = pd.read_csv('data/bridge/current_closures.csv')
	map_osm = folium.Map(location=[47.5836, -122.3750], zoom_start=11, tiles='Stamen Toner')

	for bridge, coord in bridges.iteritems():
	    color='green'
	    if bridge in current_closures['bridge'].values:
	        color='red'
	    icon = folium.Icon(color=color, icon="ok")
	    marker = folium.Marker(location=coord,icon=icon, popup=bridge)

	    map_osm.add_children(marker);

	map_osm.save('osm.html')
	
	return send_from_directory(os.getcwd(),'osm.html')

if __name__ == '__main__':
	# app.run(debug=True)
	app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)