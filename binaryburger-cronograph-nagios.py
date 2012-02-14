#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
binaryburger-cronograph-nagios.py: Nagios plugin to monitor servers executing tasks managed by the BinaryBurger Cron-o-graph

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


class cronograph_check:
	uri = "http://www.binaryburger.com/cronograph/api/"
	message = False

	def _set_message(self, message):
		self.message = message

	def _exit(self, status):
		if self.message:
			print self.message
		sys.exit(status)

	def check(self):
		"""Parse command line arguments and get status
		"""

		parser = argparse.ArgumentParser(
			description="BinaryBurger Cron-o-graph Nagios plugin"
		)
		parser.add_argument(
			"--server",
			dest="Server",
			help="The server name as shown on the Cron-o-graph web interface",
			required=True
		)
		parser.add_argument(
			"--secret",
			dest="Secret",
			help="The server secret as shown on the Cron-o-graph web interface",
			required=True
		)
		parser.add_argument(
			"--api",
			dest="API",
			help="Set different API URI",
			required=False,
			default="http://www.binaryburger.com/cronograph/api/"
		)
		args = parser.parse_args()

		if args.API:
			self.uri = args.API

		request = urllib2.Request(self.uri + "status")
		request.add_header("Authorization", "Basic %s" % base64.encodestring("%s:%s" % (args.Server, args.Secret))[:-1])

		try:
			response_handle = urllib2.urlopen(request)
			response_json = json.loads(response_handle.read())

			# check response
			if not response_json["status"] or response_json["status"] not in [EXIT_OK, EXIT_WARN, EXIT_CRIT]:
				self._set_message("API response did not contain a status code")
				self._exit(EXIT_UNKNOWN)

			# set status message
			if response_json["message"]:
				self._set_message(response_json["message"])

			self._exit(response_json["status"])
		except IOError, e:
			message = "API request failed"
			if hasattr(e, "code") and e.code != 0:
				message += " (error code " + str(e.code) + ")"

			self._set_message(message)
			self._exit(EXIT_UNKNOWN)
		except ValueError, e:
			message = "Failed to decode API response"
			if hasattr(e, "message") and e.message.strip():
				message += "( " + e.message.strip() + ")"

			self._set_message(message)
			self._exit(EXIT_UNKNOWN)
		except Exception, e:
			self._set_message("An unexpected error happened (" + str(type(e)) + ")")
			self._exit(EXIT_UNKNOWN)


# run the check
if __name__ == "__main__":
	check = cronograph_check()
	check.check()
