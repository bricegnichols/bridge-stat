# from flask import render_template
# from flask import Flask, request, send_from_directory, jsonify
# from app import app
# import folium
# import vincent
# import json
# import pandas as pd
# import os
# from scripts import bridge_stat

# bridges = {'Lower Spokane St': [47.570950, -122.348324],
#           'South Park': [47.529252, -122.314316],
#           'Fremont': [47.647857, -122.349867],
#           'Ballard': [47.659280, -122.376163],
#           'Montlake': [47.647296, -122.304577],
#           'University': [47.652995, -122.320194],
#           '1st Ave S': [47.542049, -122.334541]}

# # use fake one for testing below
# # current_closures = pd.read_csv(r'notebooks/scratch_closures.csv')

# # Uncomment below to get live updates!
# current_closures = pd.read_csv('data/bridge/current_closures.csv')



# @app.route('/dashboard', methods=['GET','POST'])
# def dashboard():

# 	status_color = {}
	
# 	for bridge, coord in bridges.iteritems():
# 		status_color[bridge]='green'
# 		if bridge in current_closures['bridge'].values:
# 			status_color[bridge]='red'

# 	if request.method == 'POST':
# 		# print json.dumps(request.data)
# 		# print request.data[0]
# 		return 'test'
# 	else:
# 		print 'get'
# 		return render_template('dashboard.html', status_color=status_color,
# 			bridges=bridges)

# @app.route('/stats')
# def stats():

# 	# Get average closures
# 	# Use a static check for now, but want to get the latest at some point
# 	events = pd.read_csv(r'data/bridge/bridge_status.csv')
# 	average_closures = bridge_stat.average_closures(events)

# 	# Closures today; how many more might we expect?
# 	closures_per_day = bridge_stat.closures_per_day(average_closures)
	
# 	resp = closures_per_day.to_json()

# 	return resp

# @app.route('/results/<bridge_name>', methods=['POST','GET'])
# def get_results(bridge_name):

# 	average_closures = pd.read_csv('data/bridge/avg_closures.csv')

# 	df = bridge_stat.closures_per_day(average_closures)
# 	df.to_csv('data/bridge/closures_per_day.csv',index=False)

# 	df = df[df['bridge'] == bridge_name]
# 	# df.index = df['bridge']
# 	resp = df.to_dict()
# 	# return resp

# 	# resp = df.to_json()
# 	return render_template('bridge.html', resp=resp)