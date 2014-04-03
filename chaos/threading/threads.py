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

""" Helper functions for working with python multithreading. """

from __future__ import absolute_import
import threading, logging, os

class Threads(object):
	"""
	Container to register and handle multiple Threads.
	"""
	thread_list = {}

	def __init__(self):
		self.logger = logging.getLogger(__name__)

	def registerThread(self, name, thread):
		"""
		Register a new Thread , under the given descriptive name.

		Trying to register multiple threads under the same name will raise an Exception.

		Parameters
		----------
		name: string
			Name to register the given thread under.
		thread: threading.Thread, or a subclass
			Thread object to register.
		"""
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
		"""
		Retrieve a list of names of all registered Threads.
		"""
		return self.thread_list.keys()

	def getThread(self, name):
		"""
		Retrieve the Thread registered under the given name.

		If the given name does not exists in the Thread list, an Exception is raised.

		Parameters
		----------
		name: string
			Name of the Thread to retrieve
		"""
		if not name in self.thread_list:
			self.logger.error("Thread {0} is not registered!".format(name))
			raise Exception("Thread {0} is not registered!".format(name))

		return self.thread_list[name]

	def unregisterThread(self, name):
		"""
		Unregister the Thread registered under the given name.

		Make sure that the given Thread is properly stopped, or that a reference is
		kept in another place. Once unregistered, this class will not keep any
		other references to the Thread.

		Parameters
		----------
		name: string
			Name of the Thread to unregister
		"""
		if not name in self.thread_list:
			self.logger.error("Thread {0} is not registered!".format(name))
			raise Exception("Thread {0} is not registered!".format(name))

		del self.thread_list[name]
		self.logger.debug("Unregistered thread {0}".format(name))

	def startAll(self):
		"""
		Start all registered Threads.
		"""
		self.logger.info("Starting all threads...")

		for thread in self.getThreads():
			thr = self.getThread(thread)
			self.logger.debug("Starting {0}".format(thr.name))
			thr.start()

		self.logger.info("Started all threads")

	def stopAll(self, stop=False):
		"""
		Stop all registered Threads. This is method assumes that the Thread is using
		and internal variable called stop to control its main loop. Stopping a Thread
		is achieved as follows:

		1. The Thread is retrieved.
		2. $thread.stop is set to False.
		3. The Thread is joined, and will wait until the Thread exits.
		4. The Thread is unregistered.
		5. If $exit = True, the main process is killed.

		Ensure that any registered Thread responds to having its stop property set to False,
		else calling stopAll() will result in a hung process.
		"""
		self.logger.info("Stopping all threads...")

		for thread in self.getThreads():
			thr = self.getThread(thread)
			self.logger.debug("Stopping {0}".format(thr.name))
			thr.stop = True
			thr.join()
			self.unregisterThread(thread)

		self.logger.info("Stopped all threads")

		if stop:
			self.logger.fatal("Comitting suicide")
			os._exit(0)
