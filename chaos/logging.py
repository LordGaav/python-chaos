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

"""
Helper functions for working with the Python built-in logging module.
"""

from __future__ import absolute_import
import collections
import logging
import logging.handlers
import os


def get_logger(name=None, level=logging.NOTSET, handlers=None):
	"""
	Create a Python logging Logger for the given name. A special case is
	when the name is None, as this will represent the root Logger object.

	When handlers are specified, the currently configured handlers for this name
	are removed, and the specified handlers are set.

	Parameters
	----------
	name: string
		Name of the Logger to create. Specify None to designate the root Logger.
	level: string
		One of: CRITICAL, ERROR, WARNING, INFO or DEBUG. Alternatively, use the `logging`
		constants: logging.CRITICAL, logging.ERROR, etc.
	handlers: dict
		Keys specifies the handler, value may optionally contain configuration,
		or be specified as None.

		Supported handlers are:
		- console: logging to stdout. Optionally specify a custom Handler using 'handler'.
		- file: logging to a specific file. Specify the file as 'logfile'.
		- syslog: logging to syslog.

		All handlers support custom output formats by specifying a 'format'.
	"""
	logger = logging.getLogger(name)

	if name is None:
		name = "root"
	if handlers is None:
		handlers = []

	logger.setLevel(level)

	if len(handlers) != 0:
		logger.handlers = []

	if "console" in handlers:
		if not isinstance(handlers['console'], collections.Iterable):
			handlers['console'] = {}

		if "handler" in handlers['console']:
			strm = handlers['console']['handler']
		else:
			strm = logging.StreamHandler()

		if "format" in handlers['console']:
			fmt = logging.Formatter(handlers['console']['format'])
		else:
			fmt = logging.Formatter('%(message)s')

		strm.setLevel(level)
		strm.setFormatter(fmt)
		logger.addHandler(strm)

	if "file" in handlers:
		if not isinstance(handlers['file'], collections.Iterable):
			raise TypeError("file handler config must be a dict")
		if "logfile" not in handlers['file']:
			raise ValueError("file handler config must contain logfile path name")

		fil = logging.handlers.WatchedFileHandler(handlers['file']['logfile'])

		if "format" in handlers['file']:
			fmt = logging.Formatter(handlers['file']['format'])
		else:
			fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

		fil.setLevel(level)
		fil.setFormatter(fmt)
		logger.addHandler(fil)

	if "syslog" in handlers:
		if not isinstance(handlers['syslog'], collections.Iterable):
			handlers['syslog'] = {}

		sysl = logging.handlers.SysLogHandler(address='/dev/log', facility=logging.handlers.SysLogHandler.LOG_SYSLOG)

		if "format" in handlers['syslog']:
			fmt = logging.Formatter(handlers['syslog']['format'])
		else:
			fmt = logging.Formatter('%(name)s[%(process)s] %(levelname)-8s: %(message)s')

		sysl.setLevel(level)
		sysl.setFormatter(fmt)
		logger.addHandler(sysl)

	return logger
