#!/usr/bin/python
# -*- coding: utf-8 -*-

import setuptools, commands

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name	= "deb-changelog-md",
    version	= commands.getoutput( 'head -1 debian/changelog | cut -d"(" -f2 | cut -d ")" -f1' ).strip()		,
    author	= commands.getoutput( 'cat debian/control | grep Maintainer | cut -d":" -f2 | cut -d"<" -f1' ).strip()	,
    author_email= commands.getoutput( 'cat debian/control | grep Maintainer | cut -d":" -f2 | cut -d"<" -f2 | cut -d">" -f1' ).strip()	,
    description	= commands.getoutput( 'cat debian/control | grep Description | cut -d":" -f2' ),
    long_description=long_description,
    #long_description_content_type="text/markdown",
    url		= "https://github.com/erikni/debian-changelog.md",
    packages	= setuptools.find_packages(),
    classifiers	= [
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

