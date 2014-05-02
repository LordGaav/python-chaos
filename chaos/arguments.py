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

def get_config_argparse(suppress=None):
	"""
	Create an ArgumentParser which listens for the following common options:
	- --config
	- --help
	- --quiet
	- --verbose
	- --version

	Arguments
	---------
	suppress_help: list of strings
		Defines what options to suppress from being added to the ArgumentParser. Provide
		the name of the options to suppress, without "--". Of note in particular is the help option.

		If help is suppressed, help information is suppressed in the returned ArgumentParser
		If help is not suppressed, help information is automatically output by ArgumentParser 
			when -h/--help is passed, and the program is exited upon parsing the arguments.
		In both cases, -h/--help is not actually suppressed, only the behaviour of the ArgumentParser
		when encountering the option.
	"""

	if suppress is None:
		suppress = []

	config_parser = ArgumentParser(description="Looking for config", add_help=(not "help" in suppress))
	if not "config" in suppress:
		config_parser.add_argument("--config",	metavar="CFG",		 type=str,		help="Config file to load")
	if "help" in suppress:
		config_parser.add_argument("--help",	action="store_true", default=False, help="Display usage information and exit")
	if not "quiet" in suppress:
		config_parser.add_argument("--quiet",	action="store_true", default=False, help="Don't print messages to stdout")
	if not "verbose" in suppress:
		config_parser.add_argument("--verbose", action="store_true", default=False, help="Output debug messages")
	if not "version" in suppress:
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

	return get_config_argparse(suppress=["help"]).parse_known_args()

def get_default_config_file(argparser, suppress=None, default_override=None):
	"""
	Turn an ArgumentParser into a ConfigObj compatible configuration file.

	This method will take the given argparser, and loop over all options contained. The configuration file is formatted
	as follows:

	# <option help info>
	<option destination variable>=<option default value>

	Arguments
	---------
	argparser: ArgumentParser
	suppress: list of strings
		All options specified will be suppressed from the config file. Useful to avoid adding stuff like version or help.
	default_override: dict
		This method will use the defaults from the given ArgumentParser, unless the option is specified here. If specified,
		the default from this dict will be used instead. The format is { "option": <new default value>, ... } .
	"""
	if not suppress:
		suppress = []
	if not default_override:
		default_override = {}

	lines = []
	seen_arguments = []
	for arg in argparser._actions:
		if arg.dest in suppress:
			continue
		if arg.dest in seen_arguments:
			continue
		default = arg.default
		if arg.dest in default_override.keys():
			default = default_override[arg.dest]
		lines.append("# {0}\n{1}={2}\n".format(arg.help, arg.dest, default))
		seen_arguments.append(arg.dest)

	return "".join(lines)
