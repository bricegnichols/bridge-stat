# bridge-stat
Find out if Seattle bridges are closed. Supply your travel window and receive text/email alerts.

## Script
Currently, the project comprises only one script ("bridge.py"). This script monitors an automated [Seattle DOT Twitter account] (https://twitter.com/sdotbridges). If the account tweets a bridge closure for a defined bridge name, within a certain time frame, an email/text alert is sent. This script works for a single bridge, time window, and user. Next step is to build a simple web framework that allows other users to sign up for alerts, passing in their list of bridges and time windows. Thinking Django for this. 
