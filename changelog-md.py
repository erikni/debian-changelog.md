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
import yaml


class ChangelogMD(object):
	""" Changelog object """

	def __init__(self, debug_mode=0):
		""" init """

		# config
		self.changelog_yml = os.environ.get('DEB_CHANGELOG_YML', '/etc/changelog-md/changelog-md.yml')

		# debug mod
		self.debug_mode = debug_mode

		self.params = {\
			'control' : 'debian/control',\
			'changelog' : 'debian/changelog',\
			'debug' : 1,\
		}


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
				if type(self.params[config_name]) != type('aaa'):
					continue
				self.params[config_name] = self.params[config_name].replace('{{%s}}' % env_name, envs[env_name])

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

		return package_name, package_title


	def changelog(self, yaml_data):
		""" generate changelog """

		# package name + title
		(package_name, package_title) = self.__package()

		# categories
		(categories, categories_lower, category_comments) = self.__categories(yaml_data)

		# ---

		# changelog.md
		self.debug('write file="%s"' % self.params['outputMD'])
		fwr = open(self.params['outputMD'], 'w')

		fwr.write('# Changelog for %s (%s)\n' % (package_title, package_name))
		fwr.write('All notable changes to this project will be documented in this file.\n\n')

		fwr.write('The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)\n')
		fwr.write('and this project adheres to [Semantic Versioning]')
		fwr.write('(http://semver.org/spec/v2.0.0.html).\n\n')

		fwr.write('This is an automatically generated [changelog](%s), ' % self.params['changelog'])
		fwr.write('please do not edit\n\n')


		# debian changelog
		data = open('debian/changelog').read().split('%s (' % package_name)
		__prev_date = ''
		for version_line in data:

			lines = []
			for line in version_line.split('\n'):
				if not line:
					continue

				line = line.strip()
				if not line:
					continue

				lines.append(line)

			line_cnt = len(lines)
			line_no = 0

			version_no = ''
			version_date = ''
			version_historys = {}

			self.debug('info line_no=%s, line="%s"' % (line_cnt, lines))
			for line in lines:
				line_no = line_no + 1

				if line_no == 1:
					self.debug('first line_no=%s, line="%s"' % (line_no, line))
					version_no = line.split(')')[0].split('-')[0].strip()

				elif line_no == line_cnt:
					self.debug('last line_no=%s, line="%s"' % (line_no, line))
					version_date = ''

					self.debug('date line_no=%s, line="%s"' %\
							(line_no, line.split(',')[-1].split('+')[0].strip()))
					timep = time.strptime(line.split(',')[-1].split('+')[0].strip(), '%d %b %Y %H:%M:%S')
					version_date = time.strftime('%Y-%m-%d', timep)

				else:
					self.debug('info line_no=%s, line="%s"' % (line_no, line))
					if line[0] == '*':
						line = line[1:].strip()

					category_name = line.lower().split(':')[0].strip()
					if category_name in categories_lower:
						category_name = '%s%s' % (category_name[0].upper(), category_name[1:].lower())
						comment = line.split(':', 1)[1].strip()
					else:
						category_name = 'Unknown'
						comment = line.strip()

						find_line = ' %s ' % line.lower().replace('.', ' ')
						find_line = find_line.replace(',', ' ').replace('#', ' ')
						find_line = find_line.replace(':', ' ').replace('-', ' ')
						find_line = find_line.replace(';', ' ')

						for find_key in category_comments.keys():
							find_str = ' %s ' % find_key.lower()
							if find_line.find(find_str) > -1:
								category_name = category_comments[find_key]

						del find_line

					if category_name not in version_historys:
						version_historys[category_name] = []

					version_historys[category_name].append(comment)
					self.debug('write category="%s", message="%s"' %\
						(category_name, comment))

			if not version_no or not version_date or not version_historys:
				continue

			if version_date != __prev_date:
				self.debug('diff version=%s, date=%s, prev=%s' %\
					(version_no, version_date, __prev_date))
				fwr.write('## [%s] - %s\n' % (version_no, version_date))
			else:
				self.debug('same version=%s, date=%s, prev=%s' %\
					(version_no, version_date, __prev_date))
				fwr.write('## [%s]\n' % (version_no,))

			for category_name in categories:
				if category_name in version_historys:
					fwr.write('### %s\n' % category_name)
					for history in version_historys[category_name]:
						fwr.write('- %s\n' % history)
					fwr.write('\n')

			fwr.write('\n')
			__prev_date = version_date

		fwr.close()

		return True


if __name__ == '__main__':

	CHANGELOG = ChangelogMD(1)
	DATA = CHANGELOG.read()
	CHANGELOG.changelog(DATA)
