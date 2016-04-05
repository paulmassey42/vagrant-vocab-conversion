#!/usr/bin/env bash
#################################################################
echo "************* Bootstrapping started **********************"
apt-get update -y
apt-get install -y ntp xinit xterm iceweasel gnome gnome-terminal gnome-shell
apt-get install -y gawk dos2unix emacs curl gdm3 make autoconf
dpkg-reconfigure gdm3
# Python stuff which will be needed
apt-get install -y python-software-properties software-properties-common
apt-get install -y python python3 
# Python 3 tools and some libraries which will be needed
apt-get install -y python3-setuptools python-setuptools
easy_install3 rdflib
easy_install3 xlrd
easy_install SPARQLWrapper

# Make sure it's all installed.
apt-get -y update --force-yes
apt-get autoclean
echo "*********** done with bootstrap of dev machine ***********"
#################################################################

