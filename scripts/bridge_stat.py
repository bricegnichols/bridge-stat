# main script to house some functions

# Original author: yanofsky
# https://gist.github.com/yanofsky/5436496

# Export limited tweet history for SDOT bridges account

#!/usr/bin/env python
# encoding: utf-8

import tweepy 
import csv
from datetime import datetime, timedelta
from config import *
import pandas as pd

def get_tweets(screen_name, export_all=True):
	"""
	Retrieve tweet history for a user, for defined number of recent pages
	"""

	# authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token_key, access_token_secret)
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
	tweets = get_tweets('SDOTBridges',export_all=False)
	df = bridge_status(tweets).sort_values('local_date')

	# All closed bridges should have an open even followed by a later closed event

	# Check all the close events
	close_events = df[df['event'] == 'closed'].drop_duplicates(subset='bridge', keep='last')
	open_events = df[df['event'] == 'open'].drop_duplicates(subset='bridge', keep='last')

	# get only the most recent open and close events
	df = pd.merge(close_events,open_events,on='bridge',suffixes=['_close','_open'])

	current_closures = df[df['local_date_open'] < df['local_date_close']]

	return current_closures