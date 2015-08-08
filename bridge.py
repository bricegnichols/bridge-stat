# get Seattle bridge open/close status from Twitter 
# polling approach, not RESTful, which is ideal
import twitter
import pytz
import datetime
from config import *
import smtplib
import email
from email.mime.text import MIMEText
from datetime import datetime
from dateutil.tz import tzoffset
import sched, time
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import StreamListener
from tweepy import Stream
import json
import sys

api = twitter.Api(consumer_key=consumer_key,
	consumer_secret=consumer_secret,
	access_token_key=access_token_key,
	access_token_secret=access_token_secret)

twitterID = '2768116808'
bridgeName = 'Spokane'

# Define a single timeframe to work with
startTime = "4:25PM"
endTime = "10:30PM"

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
   	    # if within the defined time frame, process tweet
   	    # otherwise do nothing
   	    if check_time():
   	    	process_tweet(data)
   	    return True

    def on_error(self, status):
        print(status)

def check_time():
	now = datetime.now()
	startTimeObj = datetime.strptime(startTime, '%I:%M%p')
	endTimeObj = datetime.strptime(startTime, '%I:%M%p')

	if startTimeObj.hour <= now.hour <= endTimeObj.hour and \
       startTimeObj.minute <= now.minute <= endTimeObj.minute:
           return True

def process_tweet(data):
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
	# Import the email modules we'll need
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