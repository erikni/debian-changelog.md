#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Basic example
"""

import sys

#pylint: disable=wrong-import-position
sys.path.append('../../')
import changelog_md

print()
CHANGELOG = changelog_md.ChangelogMD(1)
DATA = CHANGELOG.read()
CHANGELOG.changelog(DATA)
