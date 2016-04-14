#!/usr/bin/env bash
#################################################################
echo "************* Bootstrapping started **********************"
apt-get update -y
apt-get install -y ntp xinit xterm iceweasel gnome gnome-terminal gnome-shell
apt-get install -y gawk dos2unix emacs curl gdm3 make autoconf perl
dpkg-reconfigure gdm3
# Python stuff which will be needed
apt-get install -y python-software-properties software-properties-common
apt-get install -y python python3 
# Python 3 tools and some libraries which will be needed
apt-get install -y python3-setuptools python-setuptools
easy_install3 rdflib
easy_install3 xlrd
easy_install SPARQLWrapper
# JYTHON, ETC
easy_install3 Django
easy_install3 django-jython

#################################################################
# python 2.7 tool needed
easy_install xlwt
easy_install csv2xls

# install bunch of perl libraries (for csv2xls perl script)
apt-get -y install libtext-csv-xs-perl
apt-get -y install libdate-calc-perl
apt-get -y install libspreadsheet-writeexcel-perl

# install libiconv
wget http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.11.tar.gz
tar -xvzf libiconv-1.11.tar.gz
cd libiconv-1.11
./configure --prefix=/usr/local/libiconv
make
make install

# Make sure it's all installed.
apt-get -y update --force-yes
apt-get autoclean
echo "*********** done with bootstrap of dev machine ***********"
#################################################################
