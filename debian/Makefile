KEY=CD9C0E84
DIST=trusty
PROJECT=$(shell head -n1 debian/changelog | cut -d" " -f1)
PYTHON_PROJECT=$(shell head -n1 debian/changelog | cut -d" " -f1 | sed 's/-//')
MAJOR_VERSION=$(shell head -n1 debian/changelog | egrep -o '[0-9]+\.' | sed 's/\.//' | head -n1)
MINOR_VERSION=$(shell head -n1 debian/changelog | egrep -o '\.[0-9]+' | sed 's/\.//' | head -n1)

GIT_REV=$(shell git rev-parse --short --verify HEAD)
LAST_CHANGELOG_REV=$(shell git log -n 1 --pretty=format:%h -- debian/changelog)
COMMITS_SINCE_LAST_CHANGELOG=$(shell git rev-list $(LAST_CHANGELOG_REV)..HEAD | wc -l)

ifndef VERSION
TMP_VERSION=$(shell expr $(MINOR_VERSION) + 1)
VERSION=$(MAJOR_VERSION).$(TMP_VERSION)
endif

CURRENT_DEV=$(shell git config user.email)

SNAPSHOT_VERSION=$(VERSION)~$(COMMITS_SINCE_LAST_CHANGELOG).g$(GIT_REV)

clean:
	rm -vfR build
	rm -vfR debian/control
	rm -vfR debian/$(PROJECT)*
	rm -vfR debian/python-$(PROJECT)*
	rm -vfR dist
	rm -vfR *.egg-info

changelog:
	git dch --ignore-branch --snapshot --auto --git-author --new-version "$(VERSION)" --snapshot-number "$(COMMITS_SINCE_LAST_CHANGELOG)"

release:
	git dch --ignore-branch --release --auto -N $(VERSION) --git-author

bump_version:
	sed -i 's/VERSION = ".*"/VERSION = "$(VERSION)"/;s/BUILD = ".*"/BUILD = "$(GIT_REV)"/' $(PYTHON_PROJECT)/version.py
	tail -n3 $(PYTHON_PROJECT)/version.py

generate_all: generate_control

generate_control:
	cat debian/control.source debian/control.$(DIST) > debian/control

package: clean generate_all changelog
	make -f debian/Makefile bump_version VERSION=$(SNAPSHOT_VERSION)
	dpkg-buildpackage -us -uc -rfakeroot
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
	echo $(SNAPSHOT_VERSION)
