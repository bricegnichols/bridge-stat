from flask import render_template
from flask import Flask, request, send_from_directory
from app import app
import folium
import vincent
import json
import pandas as pd
import os
from scripts import bridge_stat

bridges = {'Lower Spokane St': [47.570950, -122.348324],
          'South Park': [47.529252, -122.314316],
          'Fremont': [47.647857, -122.349867],
          'Ballard': [47.659280, -122.376163],
          'Montlake': [47.647296, -122.304577],
          'University': [47.652995, -122.320194],
          '1st Ave S': [47.542049, -122.334541]}

# systematic pop up for all bridges, based on status
# current_closures = pd.read_csv(r'notebooks/scratch_closures.csv')
# map_osm = folium.Map(location=[47.5836, -122.3750], zoom_start=11, tiles='Stamen Toner')
# map_osm.save('osm.html')
current_closures = bridge_stat.current_closures()

@app.route('/')
@app.route('/index')
def map():
# 	tweets = bridge_stat.get_tweets(screen_name='SDOTBridges', export_all=False)
# 	df = bridge_stat.bridge_status(tweets)
# 	df = df.sort('local_date')
# 	close_events = df[df['event'] == 'closed'].drop_duplicates(subset='bridge', keep='last')
# 	open_events = df[df['event'] == 'open'].drop_duplicates(subset='bridge', keep='last')
# 	df = pd.merge(close_events,open_events,on='bridge',suffixes=['_close','_open
# 	current_closures = df[df['local_date_open'] < df['local_date_close']]
	
	# current_closures = bridge_stat.bridge_status(latest_tweets) 
	# latest_tweets.to_csv('test.csv')
	print 'here'

	map_osm = folium.Map(location=[47.5836, -122.3750], zoom_start=11, tiles='Stamen Toner')

	for bridge, coord in bridges.iteritems():
	    color='green'
	    print bridge
	    if bridge in current_closures['bridge'].values:
	        color='red'
	    icon = folium.Icon(color=color, icon="ok")
	    marker = folium.Marker(location=coord,icon=icon, popup=bridge)

	    map_osm.add_children(marker);

	map_osm.save('osm.html')
	
	return send_from_directory(os.getcwd(),'osm.html')
	# return map_osm