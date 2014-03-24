# Copyright (c) 2014 Nick Douma < n.douma [at] nekoconeko . nl >
#
# This file is part of chaos, a.k.a. python-chaos .
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see 
# <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
import threading, logging, os

class Threads(object):
	thread_list = {}

	def __init__(self):
		self.logger = logging.getLogger(__name__)

	def registerThread(self, name, thread):
		if not isinstance(thread, threading.Thread):
			self.logger.error("Thread {0} is not actually a Thread!".format(name))
			raise Exception("Thread {0} is not actually a Thread!".format(name))

		if name in self.thread_list:
			self.logger.error("Thread {0} already registered!".format(name))
			raise Exception("Thread {0} already registered!".format(name))

		self.thread_list[name] = thread
		self.logger.debug("Registered thread {0}".format(name))

		return thread

	def getThreads(self):
		return self.thread_list.keys()

	def getThread(self, name):
		if not name in self.thread_list:
			self.logger.error("Thread {0} is not registered!".format(name))
			raise Exception("Thread {0} is not registered!".format(name))

		return self.thread_list[name]

	def unregisterThread(self, name):
		if not name in self.thread_list:
			self.logger.error("Thread {0} is not registered!".format(name))
			raise Exception("Thread {0} is not registered!".format(name))

		del self.thread_list[name]
		self.logger.debug("Unregistered thread {0}".format(name))

	def startAll(self):
		self.logger.info("Starting all threads...")

		for thread in self.getThreads():
			t = self.getThread(thread)
			self.logger.debug("Starting {0}".format(t.name))
			t.start()

		self.logger.info("Started all threads")

	def stopAll(self, exit=False):
		self.logger.info("Stopping all threads...")

		for thread in self.getThreads():
			t = self.getThread(thread)
			self.logger.info("Stopping {0}".format(t.name))
			t.stop = True
			t.join()
			self.unregisterThread(thread)

		self.logger.info("Stopped all threads")

		if exit:
			self.logger.fatal("Comitting suicide")
			os._exit(0)
