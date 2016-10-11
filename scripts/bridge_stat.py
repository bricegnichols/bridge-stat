# main script to house some functions

# Original author: yanofsky
# https://gist.github.com/yanofsky/5436496

# Export limited tweet history for SDOT bridges account

#!/usr/bin/env python
# encoding: utf-8
import os
import tweepy 
import csv
from datetime import datetime, timedelta
import math
# from config import *
import pandas as pd

def get_tweets(screen_name, export_all=True):
	"""
	Retrieve tweet history for a user, for defined number of recent pages
	"""

	# authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(os.environ['consumer_key'], os.environ['consumer_secret'])
	auth.set_access_token(os.environ['access_token_key'], os.environ['access_token_secret'])
	api = tweepy.API(auth)

	# initialize a list to hold all the tweepy Tweets
	alltweets = []

	# Retrieve the most recent 200 tweets (max per request) & save to array
	new_tweets = api.user_timeline(screen_name=screen_name, count=200)
	alltweets.extend(new_tweets)

	# save the id of the oldest tweet less in case we want to export remaining history
	oldest = alltweets[-1].id - 1

	# export entire history page by page if required
	if export_all=='all':
		while len(new_tweets) > 0:
			print "getting tweets before %s" % (oldest)
			
			#all subsiquent requests use the max_id param to prevent duplicates
			new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
			
			#save most recent tweets
			alltweets.extend(new_tweets)
			
			#update the id of the oldest tweet less one
			oldest = alltweets[-1].id - 1
			
			print "...%s tweets downloaded so far" % (len(alltweets))

	#transform the tweepy tweets into a 2D array that will populate the csv	
	outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in alltweets]
	
	df = pd.DataFrame(outtweets, columns=['id','created_at', 'text'])

	return df

def days_hours_minutes(td):
    """
    convert a timedate object into a dictionary with days, hours, and minutes elements
    """
    mydict = {}
    mydict['days'] = td.days
    mydict['hours'] = td.seconds//3600
    mydict['minutes'] = (td.seconds//60)%60
    return mydict

def set_local_time(obj, offset_hours=-7):

	#account for offset from UTC using timedelta                                
	local_timestamp = obj + timedelta(hours=offset_hours)

	return local_timestamp  

def bridge_status(df):

	# Extract data from CSV by splitting text columns
	# set time field based on value in text, not from "created_at"
	df['bridge'] = df['text'].map(lambda x: x.split('The ')[-1].split(' Bridge')[0])
	# df['time'] = df['text'].map(lambda x: x.split('- ')[-1])
	df['local_date'] = df['created_at'].apply(lambda x: set_local_time(x))
	df['event'] = df['text'].apply(lambda x: 'closed' if ('closed' in x) else 'open')
	df = df[['bridge','event', 'text','created_at', 'local_date']]

	bridge_list = ['Ballard', 'Fremont', '1st Ave S', 'Montlake', 'Lower Spokane St', 'South Park', 'University']

	# Select only rows with a bridge name in the bridge list
	df = df[df['bridge'].isin(bridge_list)]

	# There are still some records with bad data
	# Get rid of date rows without dates

	# first remove extra space in the date string
	# newdf['newtime'] = newdf['time'].str.lstrip()

	# Only include date rows with PM or AM text
	# newdf = newdf[newdf['newtime'].str.contains('PM|AM')]

	# Convert the time text to a datetime object in pandas
	# newdf['timeobj'] = pd.to_datetime(newdf['newtime'], format="%I:%M:%S %p", errors='coerce')

	# Drop some nats (not a time)
	# newdf = newdf.dropna()

	return df

def current_closures():
	'''
	Return dataframe of bridges currently opened to traffic at time of query.
	'''
	tweets = get_tweets('SDOTBridges',export_all=False)
	df = bridge_status(tweets).sort_values('local_date')
	# All closed bridges should have an open even followed by a later closed event

	# Check all the close events
	close_events = df[df['event'] == 'closed'].drop_duplicates(subset='bridge', keep='last')
	open_events = df[df['event'] == 'open'].drop_duplicates(subset='bridge', keep='last')

	# get only the most recent open and close events
	df = pd.merge(close_events,open_events,on='bridge',suffixes=['_close','_open'])
	
	current_closures = df[pd.to_datetime(df['local_date_open']) < pd.to_datetime(df['local_date_close'])]
	

	return current_closures

def average_closures(events):
	'''
	Return dataframe of average closures per day for each bridge
	Input is collected bridge event data from twitter history (../data/bridge/bridge_status.csv)
	'''
	closures = events[events['event'] == 'closed']
	closures_group = closures.groupby(['date','bridge']).count()

	closures_group['date'] = closures_group.index.get_level_values(0)
	closures_group['bridge'] = closures_group.index.get_level_values(1)

	avg_closure_per_day = {}
	for bridge in closures_group.groupby('bridge').count().index:
		avg_closure_per_day[bridge] = closures_group[closures_group['bridge'] == bridge].mean()['event']

	df = pd.DataFrame(avg_closure_per_day, index=avg_closure_per_day.keys()).T
	df = pd.DataFrame(df['Ballard'])
	df.columns = ['avg_closures']
	df['bridge'] = df.index
	df.to_csv('../data/bridge/avg_closures.csv')

	return df

def closures_per_day(average_closures):
	'''
	Return dataframe of closures on today's date, and anticipated openings left,
	based on the average from average_closures
	'''

	tweets = get_tweets('SDOTBridges',export_all=False)
	recent_df = bridge_status(tweets).sort_values('local_date')

	# Write these out for testing
	# recent_df.to_csv('../data/bridge/recent_tweets.csv')

	recent_df['local_date'] = pd.to_datetime(recent_df['local_date'])

	today = datetime.today()

	tweets_today = recent_df[recent_df['local_date'].apply(lambda row:
                       (row.day == today.day) &
                       (row.month == today.month) &
                       (row.year == today.year))
    ]

    # Get a count of tweets by bridge 
	tweets_today
	closures_today = tweets_today[tweets_today['event'] == 'closed']
	closures_by_bridge = closures_today.groupby('bridge').count()
	closures_by_bridge['bridge'] = closures_by_bridge.index
	closures_by_bridge = closures_by_bridge[['bridge','event']]
	closures_by_bridge.columns = ['bridge','closures_so_far']

	# Compare to average to get anticipated remained on average
	remaining_closures_df = pd.merge(closures_by_bridge, average_closures, left_on='bridge', right_on='bridge')

	# Round up for average closures
	remaining_closures_df['avg_closures'] = remaining_closures_df['avg_closures'].apply(lambda row: math.ceil(row))
	remaining_closures_df['closures_remaining'] = remaining_closures_df['avg_closures'] - remaining_closures_df['closures_so_far']
	remaining_closures_df['%_closures_remaining'] = remaining_closures_df['closures_remaining']/remaining_closures_df['avg_closures']

	# Leave the negatives in: indicates odds less likely 
	# remaining_closures_df.to_csv('../data/bridge/closure_estimate.csv')

	return remaining_closures_df