#!/usr/bin/env python
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

from os.path import join, dirname
from setuptools import setup
from chaos.version import NAME, VERSION

DESCRIPTION = "chaos Python modules: Assorted libraries and subroutines"
LONG_DESCRIPTION = "A set of libraries and subroutines I commonly use in my python projects."

setup(
	name=NAME,
	version=VERSION,
	description=DESCRIPTION,
	long_description=LONG_DESCRIPTION,
	license="GNU LGPLv3+",
	author="Nick Douma",
	author_email="n.douma@nekoconeko.nl",
	url="https://github.com/LordGaav/python-chaos",
	platforms=["any"],
	classifiers=[
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
		"Operating System :: Unix",
		"Programming Language :: Python :: 2 :: Only",
		"Programming Language :: Python :: 2.7",
		"Topic :: Software Development :: Libraries :: Python Modules"
	],
	packages=[
		"chaos",
		"chaos.amqp",
		"chaos.multiprocessing",
		"chaos.threading"
	],
	install_requires=[
		"configobj",
		"pika>=0.9.5"
	]
)
