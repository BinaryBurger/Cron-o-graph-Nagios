#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
binaryburger-cronmanager-nagios.py: Nagios plugin to monitor servers executing tasks managed by the BinaryBurger CronManager

Author: Jens Nistler <loci@binaryburger.com>
License: GPL
Version: 1.0
"""

import argparse, sys, urllib2, base64, json

# Constants
EXIT_OK = 0
EXIT_WARN = 1
EXIT_CRIT = 2
EXIT_UNKNOWN = 3


class cronmanager_check:
	uri = "http://www.binaryburger.com/cronmanager/api/status"
	message = False

	def addMessage(self, message):
		"""Add message
		"""

		if self.message:
			self.message += ", "
			self.message += message
		else:
			self.message = message

	def exit(self, status):
		if self.message:
			print self.message
		sys.exit(status)

	def check(self):
		"""Parse command line arguments and get status
		"""

		parser = argparse.ArgumentParser(
			description="BinaryBurger CronManager Nagios plugin"
		)
		parser.add_argument(
			"--server",
			dest="Server",
			help="The server name as shown on the CronManager web interface",
			required=True
		)
		parser.add_argument(
			"--secret",
			dest="Secret",
			help="The server secret as shown on the CronManager web interface",
			required=True
		)
		args = parser.parse_args()

		request = urllib2.Request(self.uri)
		request.add_header("Authorization", "Basic %s" % base64.encodestring("%s:%s" % (args.Server, args.Secret))[:-1])

		try:
			response_handle = urllib2.urlopen(request)
			response_json = json.loads(response_handle.read())

			# check response
			if not response_json["status"]:
				raise ValueError("Missing status in response")

			if response_json["message"]:
				self.addMessage(response_json["message"])
			if response_json["status"] == "OK":
				self.exit(EXIT_OK)
			elif response_json["status"] == "ERROR":
				self.exit(EXIT_CRIT)
			self.exit(EXIT_WARN)
		except IOError, e:
			self.addMessage("API request failed")
			if hasattr(e, "message") and e.message.strip():
				self.addMessage(e.message.strip())
			if hasattr(e, "code") and e.code != 0:
				self.addMessage("error code " + str(e.code))
			self.exit(EXIT_WARN)
		except ValueError, e:
			self.addMessage("Failed to decode API response")
			if hasattr(e, "message") and e.message.strip():
				self.addMessage(e.message.strip())
			self.exit(EXIT_WARN)

		self.addMessage("An unexpected error happened")
		self.exit(EXIT_UNKNOWN)

# run the check
if __name__ == "__main__":
	check = cronmanager_check()
	check.check()
