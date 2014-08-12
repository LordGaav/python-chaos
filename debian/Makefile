KEY=CD9C0E84
DIST=trusty
PROJECT=python-chaos
PYTHON_PROJECT=$(shell head -n1 debian/changelog | cut -d" " -f1)
GIT_REV=$(shell git rev-parse --short --verify HEAD)
MAJOR_VERSION=$(shell head -n1 debian/changelog | egrep -o '[0-9]+\.' | sed 's/\.//' | head -n1)
MINOR_VERSION=$(shell head -n1 debian/changelog | egrep -o '\.[0-9]+' | sed 's/\.//' | head -n1)
DEV_VERSION=1

ifndef VERSION
TMP_VERSION=$(shell expr $(MINOR_VERSION) + 1)
VERSION=$(MAJOR_VERSION).$(TMP_VERSION)
endif

clean:
	rm -vfR build
	rm -vfR debian/control
	rm -vfR debian/$(PROJECT)*

changelog:
	git dch --ignore-branch --snapshot --auto --git-author

release:
	git dch --ignore-branch --release --auto -N $(VERSION) --git-author

bump_version:
	sed -i 's/VERSION = ".*"/VERSION = "$(VERSION)"/;s/BUILD = ".*"/BUILD = "$(GIT_REV)"/' $(PYTHON_PROJECT)/version.py
	tail -n3 $(PYTHON_PROJECT)/version.py

generate_all: generate_control

generate_control:
	cat debian/control.source debian/control.$(DIST) > debian/control

package: clean generate_all
	make -f debian/Makefile bump_version VERSION=$(VERSION)~dev$(DEV_VERSION)
	sed -i "0,/RELEASE/s/(.*)/($(VERSION)~dev$(DEV_VERSION))/" debian/changelog
	dpkg-buildpackage -A -us -uc
	git checkout $(PYTHON_PROJECT)/version.py
	git checkout debian/changelog

source: clean generate_all
	dpkg-buildpackage -S -k$(KEY)

source_no_sign: clean generate_all
	dpkg-buildpackage -S -us

upload_to_ppa:
	dput ppa:lordgaav/$(PROJECT) "$(CHANGES)"

pbuild_create:
	pbuilder-dist "$(DIST)" create

pbuild_update:
	pbuilder-dist "$(DIST)" update

pbuild:
	pbuilder-dist "$(DIST)" "$(CHANGES)"

version:
	echo $(VERSION)
