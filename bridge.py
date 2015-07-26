# get Seattle bridge open/close status from Twitter 
import twitter
from config import *

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

	print closures
	return closures


def main():
	handle = '@SDOTbridges'
	statuses = api.GetUserTimeline(screen_name=handle,count=200)

	getClosures('Spokane', statuses)

if __name__ == '__main__':
	main()