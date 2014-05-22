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

import gdbm, json, collections

def dump_simple_db(path):
	"""
	Dumps a SimpleDb as string in the following format:
	<key>: <json-encoded string>
	"""
	output = []
	simpledb = SimpleDb(path, mode="r", sync=False)
	with simpledb as db:
		for key in db:
			output.append("{0}: {1}".format(key, db.dumpvalue(key)))
	return "\n".join(output)

class SimpleDb(collections.MutableMapping):
	"""
	Implements a simple key/value store based on GDBM. Values are stored as JSON strings,
	to allow for more complex values than GDBM itself can provide.

	This class implements the full MutableMapping ABC, which means that after using open(),
	or using with, this class behaves as a dict. All changes will be saved to disk after
	using close() or ending the with statement.
	"""

	def __init__(self, path, mode = "c", sync=True):
		"""
		Store the given parameters internally and prepare for opening the database later.

		Arguments
		---------
		path: string
			Path where to create or open the database
		mode: string
			What mode to use when opening the database:
			- "r" (read-only)
			- "w" (read-write)
			- "c" (read-write, create when not exists)
			- "n" (read-write, always create new file)
		sync: boolean
			If set to True, data will be flushed to disk after every change.
		"""
		self.path = path
		self.mode = mode + ("s" if sync else "")
		self.db = None

	def _checkopen(self):
		if self.db == None:
			raise RuntimeError("SimpleDb was not opened")

	def open(self):
		"""
		Open the GDBM database internally.
		"""
		return self.__enter__()

	def close(self):
		"""
		Close the internal GDBM database.
		"""
		self.__exit__(None, None, None)

	def dumpvalue(self, key):
		"""
		Retrieves the given key, and returns the raw JSON encoded string.
		"""
		self._checkopen()
		return self.db[key]

	def __enter__(self):
		self.db = gdbm.open(self.path, self.mode)
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self._checkopen()
		self.db.sync()
		self.db.close()
		self.db = None

	def __getitem__(self, key):
		self._checkopen()
		return json.loads(self.db[key])

	def __setitem__(self, key, value):
		self._checkopen()
		self.db[key] = json.dumps(value)

	def __delitem__(self, key):
		self._checkopen()
		del(self.db[key])

	def __iter__(self):
		self._checkopen()
		key = self.db.firstkey()

		while key != None:
			yield key
			key = self.db.nextkey(key)

		if key == None:
			raise StopIteration()

	def __len__(self):
		self._checkopen()
		return len(self.db)
