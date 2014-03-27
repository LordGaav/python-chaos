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
Helper functions for loading command line arguments using argparse.
"""

from __future__ import absolute_import
import logging
from argparse import ArgumentParser

def get_config_argparse(suppress_help=False):
	"""
	Create an ArgumentParser which listens for the following common options:
	- --config
	- --help
	- --quiet
	- --verbose
	- --version

	Arguments
	---------
	suppress_help: boolean
		If set to True, help information is suppressed in the returned ArgumentParser
		If set to False, help information is automatically output by ArgumentParser 
			when -h/--help is passed, and the program is exited upon parsing the arguments.
	"""

	config_parser = ArgumentParser(description="Looking for config", add_help=(not suppress_help))
	config_parser.add_argument("--config",	metavar="CFG",		 type=str,		help="Config file to load")
	if suppress_help:
		config_parser.add_argument("--help",	action="store_true", default=False, help="Display usage information and exit")
	config_parser.add_argument("--quiet",	action="store_true", default=False, help="Don't print messages to stdout")
	config_parser.add_argument("--verbose", action="store_true", default=False, help="Output debug messages")
	config_parser.add_argument("--version", action="store_true", default=False, help="Display version information and exit")

	return config_parser

def get_config_arguments():
	"""
	Parse command line arguments, and try to find common options. Internally
	this method uses the ArgumentParser returned by get_config_argparse().

	All variables are stored as True if set, --config will contain a string.

	Returns a tuple containing parsed variables and unknown variables,
	just like ArgumentParser.parse_known_args() would.
	"""

	logger = logging.getLogger(__name__)
	logger.debug("Parsing configuration arguments")

	return get_config_argparse(suppress_help=True).parse_known_args()
