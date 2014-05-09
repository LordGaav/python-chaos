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

import shlex
from subprocess import Popen, PIPE

def call_simple_cli(command, cwd=None, universal_newlines=False):
	""" Simple wrapper around SimpleCliTool. Simple. """
	return SimpleCliTool._call_cli(command, cwd, universal_newlines)

class SimpleCliTool(object):
	def _call_cli(self, command, cwd=None, universal_newlines=False):
		"""
		Executes the given command, internally using Popen. The output of
		stdout and stderr are returned as a tuple. The returned tuple looks
		like: (stdout, stderr, returncode)

		Parameters
		----------
		command: string
			The command to execute.
		cwd: string
			Change the working directory of the program to the specified path.
		universal_newlines: boolean
			Enable the universal_newlines feature of Popen.
		"""
		command = str(command.encode("utf-8").decode("ascii", "ignore"))
		proc = Popen(shlex.split(command), stdout=PIPE, stderr=PIPE, cwd=cwd, universal_newlines=universal_newlines)
		stdout, stderr = proc.communicate()

		return (stdout, stderr, proc.returncode)
