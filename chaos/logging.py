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
import logging, logging.handlers, os

def get_logger(name, level=logging.INFO, handlers=[]):
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
