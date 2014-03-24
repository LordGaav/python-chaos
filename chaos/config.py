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
import threading, logging, os, inspect
from configobj import ConfigObj

def get_config(config_base, custom_file=None, debug_log=False, console=True):
	logger = logging.getLogger(__name__)

	logger.debug("Expanding variables")
	home = os.path.expanduser("~")
	loc = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

	logger.debug("Create empty config")
	config = ConfigObj()

	# Merge in config file in program dir
	if os.path.isfile(os.path.join(loc, "%s.config" % config_base)):
		logger.debug("Loading config from workingdir")
		cfg = ConfigObj(os.path.join(loc, "%s.config" % config_base))
		config.merge(cfg)

	# Merge in system-wide config (Unix specific)
	if os.path.isfile("/etc/%s.config" % config_base):
		logger.debug("Loading config from /etc")
		cfg = ConfigObj("/etc/%s.config" % config_base)
		config.merge(cfg)

	# Merge in user specific config
	if os.path.isfile(os.path.join(home, ".%s.config" % config_base)):
		logger.debug("Loading config from homedir")
		cfg = ConfigObj(os.path.join(home, ".%s.config" % config_base))
		config.merge(cfg)

	# Config file provided on command line has preference
	if custom_file:
		logger.debug("Loading custom config file")
		cfg = ConfigObj(custom_file)
		config.merge(cfg)

	return config