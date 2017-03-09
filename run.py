
#####################
# Turn off debug mode in production
debug = True

#! flask/bin/python

import os
import json
from datetime import datetime
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
	print len(current_closures_df)
	# Check that the data looks okay. If so, save a copy locally
	current_closures_df.to_csv('data/bridge/current_closures.csv')

@app.route('/')
def map():
	df = pd.read_csv('data/bridge/current_closures.csv')
	avg_times_df = pd.read_csv('data/bridge/mean_95th_percentile.csv')
	traffic_cams = pd.read_csv('data/bridge/traffic_cams.csv')

	# Flag closure periods longer than 95th percentile
	if len(df) > 0:
		df = pd.merge(df,avg_times_df,on='bridge')
		df['closure_time'] = pd.to_datetime(df['local_date_close'])-pd.to_datetime(df['local_date_open'])
		df['closure_time_min'] = df['closure_time'].apply(lambda row: float(row.seconds)/60)
		df.ix[:,'flag'] = 0
		df.ix[df['closure_time_min'] > df['95th_percentile'],'flag'] = 1

	map_osm = folium.Map(location=[47.5936, -122.3750], zoom_start=12, tiles='Stamen Toner')

	for bridge, coord in bridges.iteritems():
	    color='green'
	    icon='ok'
	    print bridge
	    cam_url = traffic_cams[traffic_cams['bridge'] == bridge]['url'].values[0]
	    html="""<base target="_blank" /><a href=http://www.google.com><img src=""" + cam_url + """ style="width:100%;height:90%;"></img></a>"""
	    iframe = folium.element.IFrame(html=html,width=400,height=300)
	    popup = folium.Popup(iframe,max_width=1000)

	    if bridge in df['bridge'].values:
	        color='red'
	        icon='exclamation'
	        # flag potential data issue
	        if df[df['bridge'] == bridge]['flag'].values[0] > 0:
	        	color = 'green'
	        	# possibly change the icon to an exclamation point or something
	        	# to warn that the twitter data is inaccurate
	    icon = folium.Icon(color=color, icon=icon)
	    marker = folium.Marker(location=coord,icon=icon, popup=popup)

	    map_osm.add_children(marker);

	map_osm.save('osm.html')
	
	return send_from_directory(os.getcwd(),'osm.html')

@app.route('/bridge')
def bridge():
	'''
	Return template that has bridge info in it
	'''
	bridge_name='test'
	return render_template('bridge.html', bridge_name=bridge_name)

if __name__ == '__main__':
	# app.run(debug=debug)
	if debug==False:
		update_bridge_status(update_interval)
	app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)