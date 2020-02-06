#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Python setup
"""

import setuptools

def control():
	""" debian/control """

	data = open('debian/control', 'r').read()
	author = ''
	email = ''
	desc = ''

	for line in data.split('\n'):
		lines = line.split(':', 1)

		if len(lines) != 2:
			continue

		if line[0].startswith('Maintainer'):
			author = line[1].strip()

	return author, email, desc

DESC_LONG = open('README.md', 'r').read()
VERSION = open('debian/changelog', 'r').read().split('\n')[0].split('(')[1].split(')')[0].strip()
AUTHOR_NAME, AUTHOR_EMAIL, DESC_SHORT = control()


# setup
setuptools.setup(\
	name='deb-changelog-md',\
	version=VERSION,\
	author=AUTHOR_NAME,\
	author_email=AUTHOR_EMAIL,\
	description=DESC_SHORT,\
	long_description=DESC_LONG,\
	#long_description_content_type="text/markdown",\
	url="https://github.com/erikni/debian-changelog.md",\
	packages=setuptools.find_packages(),\
	classifiers=[\
		"Programming Language :: Python :: 3.5",\
		"Programming Language :: Python :: 3.6",\
		"Programming Language :: Python :: 3.7",\
		"Programming Language :: Python :: 3.8",\
		"License :: OSI Approved :: MIT License",\
		"Operating System :: OS Independent",\
    ],\
)
