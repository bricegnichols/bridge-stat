# Retrieve latest bridge opening and ship data

import subprocess

def main():

	print 'importing bridge data'
	print '---------------------'
	subprocess.call("python fetch_bridge.py", shell=True)

	print 'importing ship data'
	print '---------------------'
	subprocess.call("python fetch_ship.py", shell=True)

if __name__ == '__main__':
	main()