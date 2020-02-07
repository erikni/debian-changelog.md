#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Debian changelog
"""

# ########################## Copyrights and license ############################
#                                                                              #
# Copyright 2017 Erik Brozek <erik@brozek.name>                 	       #
#                                                                              #
# This file is part of CaptainCI.                                              #
# http://www.captainci.com                                                     #
#                                                                              #
# CaptainCI is free software: you can redistribute it and/or modify it under   #
# the terms of the GNU Lesser General Public License as published by the Free  #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# CaptainCI is distributed in the hope that it will be useful, but WITHOUT ANY #
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS    #
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more #
# details.                                                                     #
#                                                                              #
# You should have received a copy of the GNU Lesser General Public License     #
# along with CaptainCI. If not, see <http://www.gnu.org/licenses/>.            #
#                                                                              #
# ##############################################################################

import os
import time
import six
import yaml


class ChangelogMD(object):
	""" Changelog object """

	def __init__(self, debug_mode=0):
		""" init """

		# config
		self.changelog_yml = os.environ.get('DEB_CHANGELOG_YML', '/etc/changelog-md/changelog_md.yml')

		# debug mod
		self.debug_mode = debug_mode

		self.params = {\
			'control' : 'debian/control',\
			'changelog' : 'debian/changelog',\
			'debug' : 1,\
		}

		self.category = {'categories':[], 'lower':[], 'comments':{}}
		self.package = {'name':'debian-unknown', 'title':'debian-unknown'}

		self.__prev_date = ''


	def debug(self, msg=''):
		""" debug mesg """

		if self.debug_mode:
			print('[debug] %s' % msg)
			return True

		return False


	def read(self):
		""" read """

		# test: if exist
		if not os.path.isfile(self.changelog_yml):
			self.debug('yaml config="%s" not found' % self.changelog_yml)
			return False

		# yaml config
		yaml_file = open(self.changelog_yml, 'r')
		yaml_data = yaml.safe_load(yaml_file.read())
		yaml_file.close()

		# Changes not exist
		if 'Changes' not in yaml_data:
			self.debug('"Changes" not in yaml config')
			return False

		if 'Config' not in yaml_data:
			self.debug('"Config" not in yaml config')
			return False

		envs = {}
		envs['GIT_BRANCH'] = 'master'
		if os.path.isfile('.captainci-env-GIT_BRANCH'):
			envs['GIT_BRANCH'] = open('.captainci-env-GIT_BRANCH', 'r').read()

		self.params['outputMD'] = 'CHANGELOG.%s.md' % envs['GIT_BRANCH']

		for config_name in ('control', 'changelog', 'outputMD', 'debug'):
			self.params[config_name] = yaml_data['Config'][config_name]

			for env_name in envs:
				if isinstance(self.params[config_name], six.string_types):
					self.params[config_name] = self.params[config_name].replace(\
						'{{%s}}' % env_name, envs[env_name])

		self.debug_mode = int(self.params['debug'])
		self.debug('debug mode=%s' % self.debug_mode)

		# test if exist
		if not os.path.isfile(self.params['changelog']):
			self.debug('file "%s" not found' % self.params['changelog'])
			return False

		if not os.path.isfile(self.params['control']):
			self.debug('file "%s" not found' % self.params['control'])
			return False

		return yaml_data


	def __categories(self, yaml_data):
		""" categories """

		# Types of changes
		categories = []
		for category_name in yaml_data.get('Changes', []).keys():
			categories.append(category_name)
		categories.append('Unknown')

		categories_lower = []
		for category_name in categories:
			categories_lower.append(category_name.lower())


		# Changes keys
		category_comments = {}
		for key_type in yaml_data['Changes'].keys():
			for key_val in yaml_data['Changes'][key_type]:
				category_comments[key_val] = key_type

		self.category['categories'] = categories
		self.category['lower'] = categories_lower
		self.category['comments'] = category_comments

		return categories, categories_lower, category_comments


	def __package(self):
		""" package """

		# Package
		package_name = 'debian-unknown'
		names = open(self.params['changelog'], 'r').readline().split()
		if len(names) > 1:
			package_name = names[0].strip()
		del names

		package_title = package_name
		for lines in open(self.params['control'], 'r').read().split('\n'):
			if not lines:
				continue

			if not lines.startswith('Description:'):
				continue

			line = lines.split(':', 1)
			if len(line) != 2:
				continue

			package_title = line[1].strip()

		self.package['name'] = package_name
		self.package['title'] = package_title

		return package_name, package_title


	def __write_init(self):
		""" file write """

		# changelog.md
		self.debug('write file="%s"' % self.params['outputMD'])
		fwr = open(self.params['outputMD'], 'w')

		fwr.write('# Changelog for %s (%s)\n' % (self.package['title'], self.package['name']))
		fwr.write('All notable changes to this project will be documented in this file.\n\n')

		fwr.write('The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)\n')
		fwr.write('and this project adheres to [Semantic Versioning]')
		fwr.write('(http://semver.org/spec/v2.0.0.html).\n\n')

		fwr.write('This is an automatically generated [changelog](%s), ' % self.params['changelog'])
		fwr.write('please do not edit\n\n')

		return fwr


	def changelog(self, yaml_data):
		""" generate changelog """

		# package name + title
		self.__package()

		# categories
		self.__categories(yaml_data)

		# ---

		# file write
		fwr = self.__write_init()

		# debian changelog
		self.__prev_date = ''
		data = open('debian/changelog').read().split('%s (' % self.package['name'])
		for version_line in data:

			lines = []
			for line in version_line.split('\n'):
				if not line:
					continue

				line = line.strip()
				if not line:
					continue

				lines.append(line)

			self.__changelog_lines(lines, fwr)

		fwr.close()

		return True


	def __changelog_lines(self, lines, fwr):
		""" changelog lines """

		row = {'cnt':len(lines), 'no':0}
		version = {'no':'', 'date':'', 'historys':{}}

		self.debug('info line_no=%s, line="%s"' % (row['cnt'], lines))
		for line in lines:
			row['no'] = row['no'] + 1

			if row['no'] == 1:
				self.debug('first line_no=%s, line="%s"' % (row['no'], line))
				version['no'] = line.split(')')[0].split('-')[0].strip()
				continue

			if row['no'] == row['cnt']:
				self.debug('last line_no=%s, line="%s"' % (row['no'], line))
				version['date'] = ''

				self.debug('date line_no=%s, line="%s"' %\
						(row['no'], line.split(',')[-1].split('+')[0].strip()))
				timep = time.strptime(line.split(',')[-1].split('+')[0].strip(), '%d %b %Y %H:%M:%S')
				version['date'] = time.strftime('%Y-%m-%d', timep)
				continue

			self.debug('info line_no=%s, line="%s"' % (row['no'], line))
			if line[0] == '*':
				line = line[1:].strip()

			category_name = line.lower().split(':')[0].strip()
			if category_name in self.category['lower']:
				category_name = '%s%s' % (category_name[0].upper(), category_name[1:].lower())
				comment = line.split(':', 1)[1].strip()
			else:
				category_name = 'Unknown'
				comment = line.strip()

				find_line = ' %s ' % line.lower().replace('.', ' ')
				find_line = find_line.replace(',', ' ').replace('#', ' ')
				find_line = find_line.replace(':', ' ').replace('-', ' ')
				find_line = find_line.replace(';', ' ')

				for find_key in self.category['comments']:
					find_str = ' %s ' % find_key.lower()
					if find_line.find(find_str) > -1:
						category_name = self.category['comments'][find_key]

				del find_line

			if category_name not in version['historys']:
				version['historys'][category_name] = []

			version['historys'][category_name].append(comment)
			self.debug('write category="%s", message="%s"' %\
				(category_name, comment))


		return self.__changelog_endlines(fwr, version)


	def __changelog_endlines(self, fwr, version):
		""" changelog endlines """

		if not version['no'] or not version['date'] or not version['historys']:
			return fwr

		if version['date'] != self.__prev_date:
			self.debug('diff version=%s, date=%s, prev=%s' %\
				(version['no'], version['date'], self.__prev_date))
			fwr.write('## [%s] - %s\n' % (version['no'], version['date']))
		else:
			self.debug('same version=%s, date=%s, prev=%s' %\
				(version['no'], version['date'], self.__prev_date))
			fwr.write('## [%s]\n' % (version['no'],))

		for category_name in self.category['categories']:
			if category_name in version['historys']:
				fwr.write('### %s\n' % category_name)
				for history in version['historys'][category_name]:
					fwr.write('- %s\n' % history)
				fwr.write('\n')

		fwr.write('\n')
		self.__prev_date = version['date']

		return fwr


if __name__ == '__main__':

	CHANGELOG = ChangelogMD(1)
	DATA = CHANGELOG.read()
	CHANGELOG.changelog(DATA)
