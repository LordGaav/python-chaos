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

""" Helper functions for file and directory globbing. """

from __future__ import absolute_import
import os, fnmatch

class Globber(object):
	"""
	Traverses a directory and returns all absolute filenames.
	"""

	def __init__(self, path, include=None, recursive=True):
		"""
		Initialize Globber parameters. Filter may be a list of globbing patterns.

		Parameters
		----------
		path: string
			Absolute path to the directory to glob
		include: list of strings
			List of globbing pattern strings. By default, ALL files in the given path
			are globbed.
		recursive: boolean
			When True: will traverse subdirectories found in $path. Defaults to True.
		"""
		if include is None:
			include = ['*']
		self.path = path
		self.include = include
		self.recursive = recursive
	
	def glob(self):
		"""
		Traverse directory, and return all absolute filenames of files that
		match the globbing patterns.
		"""
		matches = []
		for root, dirnames, filenames in os.walk(self.path):
			if not self.recursive:
				while len(dirnames) > 0:
					dirnames.pop()
			for include in self.include:
				for filename in fnmatch.filter(filenames, include):
					matches.append(os.path.join(root, filename))
		return matches
