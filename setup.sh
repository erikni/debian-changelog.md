#!/bin/bash

echo "start ... "
echo

# redhat
if [ -f "/etc/redhat-release" ]; then
	DISTNAME="redhat";
	DISTFILE="/etc/redhat-release";

# centos
elif [ -f "/etc/centos-release" ]; then
	DISTNAME="centos";
	DISTFILE="/etc/redhat-release";

# fedora
elif [ -f "/etc/fedora-release" ]; then
	DISTNAME="fedora";
	DISTFILE="/etc/redhat-release";

# debian
elif [ -f "/etc/debian_version" ]; then
	DISTNAME="debian";
	DISTFILE="/etc/debian_version";

# other
elif [ -f "/etc/os-release" ]; then
	DISTNAME=`cat /etc/os-release  | grep -v "_ID=" | grep "ID=" | cut -d"=" -f2`;
	DISTFILE="/etc/os-release";
	
else
	echo "unsupported linux distribution. exit";
	exit;
fi

echo "distribution ... "
echo "* name: $DISTNAME ";
echo -n "* version: "
cat $DISTFILE 

# install apt for rhel os
if [ "$DISTNAME" = "redhat" ] || [ "$DISTNAME" = "centos" ] || [ "$DISTNAME" = "fedora" ]; then
	echo "* $DISTNAME install apt"
	yum install apt;
fi;

# test if sudo install
if [ ! -f "/usr/bin/sudo" ]; then
	echo "* sudo install"
	apt install sudo
fi;

# test if git install
if [ ! -f "/usr/bin/git" ]; then
	echo "* sudo git"
	sudo apt install git
fi;

echo
cd /tmp/

echo "changelog-md ... "

echo -n "* clean ... "
sudo rm -rf /tmp/debian-changelog.md
echo " done"

echo -n "* git clone ... "
git clone https://github.com/erikni/debian-changelog.md.git

echo -n "* create config dir ... "
sudo mkdir -p /etc/changelog-md
echo " done"

echo -n "* script install  ... "
sudo cp -v /tmp/debian-changelog.md/changelog_md.py  /usr/bin/
sudo chmod 755 /usr/bin/changelog_md.py
echo " done"

echo -n "* config install  ... "
sudo cp -v /tmp/debian-changelog.md/changelog_md.yml /etc/changelog-md
echo " done"

echo
echo "end."
