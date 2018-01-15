#!/usr/bin/python
# -*- coding: utf-8 -*-

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


import commands, time, sys, os.path, yaml, os


# params DEBIAN_CHANGELOG_YML
if os.environ[ 'DEBIAN_CHANGELOG_YML' ]:
        CHANGELOGYML = os.environ[ 'DEBIAN_CHANGELOG_YML' ]
else:
        CHANGELOGYML = '/etc/debian-changelog.md/changelog-md.yml'

# --

# test: if exist
if not os.path.isfile( CHANGELOGYML ):
        print '[debug] yaml config="%s" not found' % CHANGELOGYML
        sys.exit(1)

# yaml config
f = open( CHANGELOGYML, 'r' )
yamlData = yaml.safe_load( f.read() )
f.close()


# Changes not exist
if 'Changes' not in yamlData:
        print '[debug] "Changes" not in yaml config'
        sys.exit(1)

if 'Config' not in yamlData:
        print '[debug] "Config" not in yaml config'
        sys.exit(1)

params = {
        'control'       : 'debian/control'      ,
        'changelog'     : 'debian/changelog'    ,
        'outputMD'      : 'CHANGELOG.md'        ,
        'debug'         : 1                     ,
}
for configName in ( 'control', 'changelog', 'outputMD', 'debug' ):
        params[ configName ] = yamlData[ 'Config' ][ configName ]

DEBUG = params['debug']

# test if exist
if not os.path.isfile( params['changelog'] ):
        print '[debug] file "%s" not found' % params['changelog']
        sys.exit(1)

if not os.path.isfile( params['control'] ):
        print '[debug] file "%s" not found' % params['control']
        sys.exit(1)


# Types of changes
categorys = yamlData.get( 'Changes', [] ).keys() 
categorys.append( 'Unknown' )

categorysLower = []
for categoryName in categorys:
        categorysLower.append( categoryName.lower() )


# Changes keys
categoryComments = {}
for keyType in yamlData[ 'Changes' ].keys():
        for keyVal in yamlData[ 'Changes' ][ keyType ]:
                categoryComments[ keyVal ] = keyType


# Package 
packageName = 'debian-unknown'
names = open( params['changelog'], 'r' ).readline().split()
if len(names) > 1:
        packageName = names[0].strip()
del names


packageTitle= packageName
for lines in open( params['control'], 'r' ).read().split('\n'):
        if not lines:
                continue

        if not lines.startswith( 'Description:' ):
                continue

        line = lines.split(':')
        if len(line) != 2:
                continue

        packageTitle = line[1].strip()


# changelog.md
fw = open( params['outputMD'], 'wb' )

fw.write( '# Changelog for %s (%s)\n' % (packageTitle, packageName) )
fw.write( 'All notable changes to this project will be documented in this file.\n\n' )

fw.write( 'The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)\n' )
fw.write( 'and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).\n\n' )

fw.write( 'This is an automatically generated [changelog](%s), please do not edit\n\n' % params['changelog'] )


# debian changelog
data = f = open( 'debian/changelog' ).read().split( '%s (' % packageName)
__prevDate = ''
for versionLine in data:

        lines   = []
        for line in versionLine.split('\n'):
                if not line:
                        continue

                line = line.strip()
                if not line:
                        continue

                lines.append( line )

        lineCnt = len(lines)
        lineNo  = 0

        versionNo       = ''
        versionDate     = ''
        versionHistorys = {}

        if DEBUG:
                print '[debug]  info lineNo=%s, line="%s"' % (lineCnt, lines)
        for line in lines:
                lineNo = lineNo + 1

                if lineNo == 1:
                        if DEBUG:
                                print '[debug] first lineNo=%s, line="%s"' % (lineNo,line)
                        versionNo = line.split(')')[0].strip()

                elif lineNo == lineCnt:
                        if DEBUG:
                                print '[debug]  last lineNo=%s, line="%s"' % (lineNo,line)
                        versionDate = ''

                        if DEBUG:
                                print '[debug]  date lineNo=%s, line="%s"' % (lineNo, line.split(',')[-1].split('+')[0].strip() )
                        timep = time.strptime( line.split(',')[-1].split('+')[0].strip(), '%d %b %Y %H:%M:%S' )
                        versionDate = time.strftime( '%Y-%m-%d', timep )

                else:
                        if DEBUG:
                                print '[debug]  info lineNo=%s, line="%s"' % (lineNo, line)
                        if line[0] == '*':
                                line = line[1:].strip()
 
                        categoryName = line.lower().split(':')[0].strip()
                        if categoryName in categorysLower:
                                categoryName = '%s%s' % ( categoryName[0].upper(), categoryName[1:].lower() )
                                comment = line.split(':',1)[1].strip()
                        else:
                                categoryName = 'Unknown'
                                comment = line.strip()

                                findLine = ' %s ' % line.lower().replace('.',' ').replace(',',' ').replace('#',' ').replace(':',' ').replace('-',' ').replace(';',' ')
                                for findKey in categoryComments.keys():
                                        findStr = ' %s ' % findKey.lower()
                                        if findLine.find( findStr ) > -1:
                                                categoryName = categoryComments[ findKey ]
                                del findLine

                        if categoryName not in versionHistorys:
                                versionHistorys[ categoryName ] = []

                        versionHistorys[ categoryName ].append( comment )
                        if DEBUG:
                                print '[debug] write category="%s", message="%s"' % (categoryName, comment)

        if not versionNo or not versionDate or not versionHistorys:
                continue

        if versionDate != __prevDate:
                if DEBUG:
                        print  '[debug]  diff version=%s, date=%s, prev=%s' % (versionNo, versionDate, __prevDate)
                fw.write( '## [%s] - %s\n' % (versionNo, versionDate) )
        else:
                if DEBUG:
                        print  '[debug]  same version=%s, date=%s, prev=%s' % (versionNo, versionDate, __prevDate)
                fw.write( '## [%s]\n' % (versionNo,) )
        for categoryName in categorys:
                if categoryName in versionHistorys:
                        fw.write( '### %s\n' % categoryName )
                        for history in versionHistorys[categoryName]:
                                fw.write( '- %s\n' % history )
                        fw.write( '\n' )
        fw.write( '\n' )
        __prevDate = versionDate

fw.close()
