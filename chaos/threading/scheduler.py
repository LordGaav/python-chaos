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

""" Helper functions for making Threads execute periodically. """

from __future__ import absolute_import
import threading, datetime, time, logging

class Scheduler(threading.Thread):
	"""
	A single thread that is automatically called with a specific interval.

	To stop a thread that is in its main loop, set stop to True.
	"""
	def __init__(self, delay, action, name, startNow=False, *args, **kwargs):
		"""
		Initialize a new Scheduler thread.

		Parameters
		----------
		delay: int
			The delay between consequtive runs of this thread, in seconds.
		action: function pointer
			The function to call.
		name: string
			Descriptive name of this thread.
		startNow: boolean
			When True, this thread will start immediately when run() is called.
			When False, this thread will start now+interval seconds when run() is called.
		*args
			Positional arguments to pass to action.
		**kwargs:
			Keyword arguments to pass to action.
		"""

		self.logger = logging.getLogger(name)
		super(Scheduler, self).__init__(None, None, name, None, None)

		self.delay = delay
		self.main_action = action
		self.name = name
		self.main_args = args
		self.main_kwargs = kwargs

		self.stop = False
		now = datetime.datetime.now()
		if startNow is True:
			self.lastRun = datetime.datetime.min
			self.logger.debug("Thread {0} will start immediately".format(name))
		else:
			self.lastRun = now
			if isinstance(startNow, (int, long)):
				self.lastRun += datetime.timedelta(seconds=startNow)
			wait = (self.lastRun - now).seconds + delay
			self.logger.debug("Thread {0} will start in {1} seconds".format(name, wait))
	
	def setStartAction(self, action, *args, **kwargs):
		"""
		Set a function to call when run() is called, before the main action is called.

		Parameters
		----------
		action: function pointer
			The function to call.
		*args
			Positional arguments to pass to action.
		**kwargs:
			Keyword arguments to pass to action.
		"""

		self.init_action = action
		self.init_args = args
		self.init_kwargs = kwargs
	
	def setStopAction(self, action, *args, **kwargs):
		"""
		Set a function to call when run() is stopping, after the main action is called.

		Parameters
		----------
		action: function pointer
			The function to call.
		*args
			Positional arguments to pass to action.
		**kwargs:
			Keyword arguments to pass to action.
		"""
		self.stop_action = action
		self.stop_args = args
		self.stop_kwargs = kwargs

	def run(self):
		"""
		Calls the defined action every $interval seconds. Optionally calls an action before
		the main loop, and an action when stopping, if these are defined.

		Exceptions in the main loop will NOT cause the thread to die.
		"""
		self.logger.debug("Thread {0} is entering main loop".format(self.name))

		if hasattr(self, "init_action"):
			self.logger.debug("Thread {0} is calling its init action")
			self.init_action(*self.init_args, **self.init_kwargs)

		while not self.stop:
			self.logger.debug("Delay is {0}".format(self.delay))
			if (datetime.datetime.now() - self.lastRun).total_seconds() > self.delay:
				self.logger.debug("Thread {0} is running".format(self.name))
				try:
					self.main_action(*self.main_args, **self.main_kwargs)
				except Exception:
					self.logger.exception("Thread {0} generated an exception!".format(self.name))

				self.lastRun = datetime.datetime.now()
				self.logger.debug("Thread {0} is done".format(self.name))
			time.sleep(1)

		if hasattr(self, "stop_action"):
			self.logger.debug("Thread {0} is calling its stop action")
			self.stop_action(*self.stop_args, **self.stop_kwargs)

		self.logger.debug("Thread {0} is exiting main loop".format(self.name))
