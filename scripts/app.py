# The MIT License (MIT)

# Copyright (c) [2015] [Brice Nichols]

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import json
import smtplib
from datetime import datetime
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import StreamListener
from tweepy import Stream

from config import *

# Seattle bridges twitter account
twitterID = '2768116808'
bridgeName = 'Spokane'    # Testing with the Spokane St. bridge

# Define a single timeframe for testing
startTime = "4:25PM"
endTime = "10:30PM"

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
   	    # if within the defined time frame, process tweet
   	    # otherwise do nothing
   	    if check_time(startTime, endTime):
   	    	process_tweet(data)
   	    return True

    def on_error(self, status):
        print(status)

def check_time(startTime, endTime):
  """
  Check if bridge opening time is within s=define parameters
  """

  now = datetime.now()
  startTimeObj = datetime.strptime(startTime, '%I:%M%p')
  endTimeObj = datetime.strptime(startTime, '%I:%M%p')

  if startTimeObj.hour <= now.hour <= endTimeObj.hour and \
         startTimeObj.minute <= now.minute <= endTimeObj.minute:
             return True

def process_tweet(data):
    """
    Send alert if bridge is opened
    """
    decoded = json.loads(data)

    twt_text = decoded['text']
    # Do some stuff with the json data if tweet is a closure for specific bridge
    if bridgeName in twt_text and "closed" in twt_text:
    	# Send and email or turn on a light or something
    	print "BRIDGE CLOSED!!! Eat another piece of toast, pet the cats"
    	sendAlert(data=decoded, email=to_emailAddress)

    	# temporarily limit the number of calls to one
    	sys.exit('had a bridge event, shutting down')
    return True

def sendAlert(data, email):
	# Import the email modules we'll need from config.py
	fromaddr = from_email_address
	toaddrs = email
	msg = 'The bridge just closed...'
	username = from_email_address
	password = from_email_password

	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()
	server.login(username,password)
	server.sendmail(fromaddr, toaddrs, msg)
	server.quit()

if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)

    stream = Stream(auth, l)
    # Stream tweets live

    # follow only the SDOTbridges twitter ID
    stream.filter(follow=[twitterID])

    # test with a general feed for now
    #stream.filter(track=['programming'])