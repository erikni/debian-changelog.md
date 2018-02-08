all: build clean

/usr/bin/dpkg-buildpackage:
	@echo package dpkg-dev not found (apt-get install dpkg-dev)
	@exit 1

build: /usr/bin/dpkg-buildpackage
	@dpkg-buildpackage -uc -us

clean:
	@rm -rf debian/deb-changelog-md/ debian/python-module-stampdir/
	@mv -v ../deb-changelog-md_*.deb /tmp/

