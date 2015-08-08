# get Seattle bridge open/close status from Twitter 
import twitter
import pytz
import datetime
from config import *
import smtplib
import email
from email.mime.text import MIMEText
from datetime import datetime
from dateutil.tz import tzoffset

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
    return datetime.fromtimestamp(timestamp, pytz.timezone(local_tz)).strftime('%Y-%m-%d %H:%M:%S')

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

	# for status in statuses:
	# 	print status
	# 	print status.created_at
	# 	tweet_time = status.created_at
	# 	local_time = to_local_time(tweet_time)
	# 	print time_string

	for closure in closures:
		#Get closures from today's date

		# get UTC timestamp from seconds since epoch
	    #utc_dt = datetime.utcfromtimestamp(closure.created_at_in_seconds).replace(tzinfo=pytz.utc)
	    #print('utc: {}'.format(utc_dt))
	    # convert to local time in the user's timezone
	    #localtime_dt = utc_dt.astimezone(localtime_tz)
	    #print('localtime [{}]: {}'.format(localtime_dt.tzname(), localtime_dt))

		#print closure
		# # need to convert tweet time/date from UTC to Pacific time
		twt_text = closure[-1]
		twt_time = closure[0]

		twt_local_time = to_local_time(twt_time)
		# print twt_text
		# print twt_time
		# print twt_local_time

		# convert twt time to date object for compariosn
		timestring = ' '.join(twt_local_time.split(" ")[:-2])
		print timestring
		timestring = timestring + " " + timestring.split(" ")[-1]
		print timestring
		twt_datetime = datetime.strptime(timestring, '%a %b %d %H:%M:%S %Y')

		#	compare to start and end times
		# consider only tweets that are within past 30 minutes for now
		# get current time and date
		present = datetime.now()

		dt = present - twt_datetime
		#date_object = datetime.strptime(twt_local_time, '%d %M %Y %I:%M%p')
		newdt = days_hours_minutes(dt)

		timestamp_min = 30

		# only report if difference is in past 30 minutes
		if newdiff['days'] == 0 and newdiff['hours'] == 0 and newdiff['minutes'] < timestamp_min:
		    print 'opening within past 30 minutes'
		    return closure

		# 		return closure

# def sendAlert(closures, email):
# 	# Import the email modules we'll need
# 	from email.mime.text import MIMEText

# 	# Open a plain text file for reading.  For this example, assume that
# 	# the text file contains only ASCII characters.
# 	# fp = open(textfile, 'rb')
# 	# Create a text/plain message
# 	msg = MIMEText('some contents')
# 	# fp.close()

# 	# me == the sender's email address
# 	# you == the recipient's email address
# 	msg['Subject'] = 'Test Email'
# 	msg['From'] = 'you'
# 	msg['To'] = 'person'

# 	# Send the message via our own SMTP server, but don't include the
# 	# envelope header.
# 	s = smtplib.SMTP('localhost:8888')
# 	s.sendmail(me, [you], msg.as_string())
# 	s.quit()

def main():
	handle = '@SDOTbridges'
	closures = filterClosures('Spokane', handle=handle)
	
	# Get the members of tamtar's list "Things That Are Rad"
	# print api.lists.members(owner_screen_name=handle, slug="Spokane")


	# print closures
	#sendAlert(closures, email)

if __name__ == '__main__':
	main()