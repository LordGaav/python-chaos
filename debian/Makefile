KEY=CD9C0E84
DIST=saucy

clean:
	rm -vfR build
	rm -vfR debian/control
	rm -vfR debian/python-chaos*

changelog:
	git dch --ignore-branch --snapshot --auto --git-author

release:
	git dch --ignore-branch --release --auto -N $(VERSION) --git-author

package: clean generate_control
	dpkg-buildpackage -A -us -uc

generate_control:
	cat debian/control.source debian/control.precise > debian/control

source: clean generate_control
	dpkg-buildpackage -S -k$(KEY)

source_no_sign: clean generate_control
	dpkg-buildpackage -S -us

upload_to_ppa:
	dput ppa:lordgaav/python-chaos "$(CHANGES)"

pbuild:
	pbuilder-dist "$(DIST)" "$(CHANGES)"
