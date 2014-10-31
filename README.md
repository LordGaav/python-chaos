python-chaos
------------

A set of libraries and subroutines I commonly use in my python projects.

Dependencies
============

* python >= 2.7
* python-configobj
* python-gdbm >= 2.7.3 (only if using SimpleDb)
* python-pika >= 0.9.5 (only if using AMQP stuff)

Building
========

To build a Debian package, perform the following steps:

1. `apt-get install ubuntu-dev-tools debhelper dh-exec`

From here you can either build the package with pbuilder-dist:

2. `pbuilder-dist saucy create`
3. `make -f debian/Makefile source_no_sign`
4. `make -f debian/Makefile pbuild CHANGES=../python-chaos_xxxx_.dsc`
5. look for the resulting .deb in ~/pbuilder/saucy_result

Or directly using dpkg-buildpackage

2. `make -f debian/Makefile package`


Installing
==========

Either use the methods described above to build your own package, or install it from my PPA.

1. `add-apt-repository ppa:lordgaav/python-chaos`
2. `apt-get update && apt-get install python-chaos`

