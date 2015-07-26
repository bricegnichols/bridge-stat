# get Seattle bridge open/close status from Twitter 
import twitter
import datetime
from config import *
import smtplib
import email
from email.mime.text import MIMEText

api = twitter.Api(consumer_key=consumer_key,
	consumer_secret=consumer_secret,
	access_token_key=access_token_key,
	access_token_secret=access_token_secret)

# Check recent statuses and store any for Spokane St.

def getClosures(bridgeName, statuses):
	closures = []
	for status in statuses:
		if bridgeName in status.text and "closed" in status.text:
		    closures.append(status.created_at.split(' ')[1:4] + [status.text])

	return closures

def filterClosures(bridgeName, startTime, endTime, handle):
	statuses = api.GetUserTimeline(screen_name=handle,count=50)
	closures = getClosures(bridgeName, statuses)
	currentDate = datetime.datetime.now()
	for closure in closures:
		# Get closures from today's date
		# print closure
		if closure[1] == str(currentDate.day):
			# Extract time from tweet text, created_at time is inaccurate
			text = closure[-1]
			time = text.split('- ')[-1]

			# compare to start and end times
			# Start and End times should be spec'ed as [hr, min, am/pm]
			# Split input start and end times
			startHour = startTime[0]
			startMin = startTime[1]
			startSun = startTime[-1]

			endHour = endTime[0]
			endMin = endTime[1]
			endSun = endTime[-1]

			# # Split tweet times
			tweetHour = int(time.split(':')[0])
			tweetMin = int(time.split(':')[1])
			tweetSun = time.split(' ')[-1]

			if startHour < tweetHour < endHour:
				# also need to account for minute differences...
				return closures

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
	closures = filterClosures('Spokane', startTime=[1,12,"PM"], endTime=[3,00,"PM"], handle=handle)
	#sendAlert(closures, email)

if __name__ == '__main__':
	main()