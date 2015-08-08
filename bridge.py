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

api = twitter.Api(consumer_key=consumer_key,
	consumer_secret=consumer_secret,
	access_token_key=access_token_key,
	access_token_secret=access_token_secret)

# Check recent statuses and store any for Spokane St.

def getClosures(bridgeName, statuses):
	closures = []
	for status in statuses:
		if bridgeName in status.text and "closed" in status.text:
		    closures.append([status.created_at, status.text])

	return closures

def to_local_time(tweet_time_string):
    """Convert rfc 5322 -like time string into a local time
       string in rfc 3339 -like format.

    """
    timestamp = email.utils.mktime_tz(email.utils.parsedate_tz(tweet_time_string))
    
    return datetime.fromtimestamp(timestamp, pytz.timezone(local_tz)).strftime('%a %b %d %H:%M:%S %Y')

def days_hours_minutes(td):
    mydict = {}
    mydict['days'] = td.days
    mydict['hours'] = td.seconds//3600
    mydict['minutes'] = (td.seconds//60)%60
    
    return mydict

def filterClosures(bridgeName, handle):
	statuses = api.GetUserTimeline(screen_name=handle,count=50)
	closures = getClosures(bridgeName, statuses)
	currentDate = datetime.now()

	for status in statuses:
		#print status
		print status.created_at
		# tweet_time = status.created_at
		# local_time = to_local_time(tweet_time)
		# print time_string

	for closure in closures:
		#Get closures from today's date

		print closure
		# # need to convert tweet time/date from UTC to Pacific time
		twt_time = closure[0]    # First item from response is timestamp
		twt_text = closure[-1]   # Last item is tweet text

		# Convert tweet time stamp from UTC to local time
		twt_local_time = to_local_time(twt_time)

		# Convert tweet string to datetime object
		twt_datetime = datetime.strptime(twt_local_time, '%a %b %d %H:%M:%S %Y')

		# Compare to start and end times
		# consider only tweets that are within past 30 minutes for now
		# get current time and date
		present = datetime.now()

		dt = present - twt_datetime
		newdt = days_hours_minutes(dt)

		timestamp_min = 30

		# only report if difference is in past 30 minutes
		if newdt['days'] == 0 and newdt['hours'] == 0 and newdt['minutes'] < timestamp_min:
		    print 'bridge opening within past 30 minutes'
		    
		    return closure

def sendAlert(closures, email):
	# Import the email modules we'll need
	from email.mime.text import MIMEText

	# Open a plain text file for reading.  For this example, assume that
	# the text file contains only ASCII characters.
	# fp = open(textfile, 'rb')
	# Create a text/plain message
	msg = MIMEText('some contents')
	# fp.close()

	# me == the sender's email address
	# you == the recipient's email address
	msg['Subject'] = 'Test Email'
	msg['From'] = 'you'
	msg['To'] = 'person'

	# Send the message via our own SMTP server, but don't include the
	# envelope header.
	s = smtplib.SMTP('localhost:8888')
	s.sendmail(me, [you], msg.as_string())
	s.quit()



def main():
	handle = '@SDOTbridges'
	
	# only run check during a specified time interval
	# should be arguments set by user
	closure = filterClosures('Spokane', handle=handle)
	
	if closure:


	# print closures
	#sendAlert(closures, email)

if __name__ == '__main__':
	main()