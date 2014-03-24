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
import logging, logging.handlers, os

def get_logger(name=None, level=logging.INFO, handlers=[]):
	"""
	Create a Python logging Logger for the given name. A special case is
	when the name is None, as this will represent the root Logger object.

	Parameters
	----------
	name: string
		Name of the Logger to create. Specify None to designate the root Logger.
	level: string
		One of: CRITICAL, ERROR, WARNING, INFO or DEBUG.
	handlers: dict
		Keys specifies the handler, value may optionally contain configuration,
		or be specified as None.

		Supported handlers are:
		- console: logging to stdout
		- file: logging to a specific file. Specify the file as 'logfile'.
		- syslog: logging to syslog
	"""
	logger = logging.getLogger(name)

	if name is None:
		name = "root"

	if len(handlers) != 0:
		logger.setLevel(level)

	if "console" in handlers:
		strm = logging.StreamHandler()
		fmt = logging.Formatter('%(message)s')
		strm.setLevel(level)
		strm.setFormatter(fmt)
		logger.addHandler(strm)

	if "file" in handlers:
		conf = handlers['file']
		fl = logging.handlers.WatchedFileHandler(conf['logfile'])
		fl.setLevel(level)

		fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		fl.setFormatter(fmt)
		logger.addHandler(fl)

	if "syslog" in handlers:
		sysl = logging.handlers.SysLogHandler(address='/dev/log', facility=logging.handlers.SysLogHandler.LOG_SYSLOG)
		sysl.setLevel(level)

		formatter = logging.Formatter('%(name)s[' + str(os.getpid()) + '] %(levelname)-8s: %(message)s')
		sysl.setFormatter(formatter)
		logger.addHandler(sysl)

	return logger
