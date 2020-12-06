#!/usr/bin/env bash

# bioarxiv2carrel.sh - given a Bioarxiv citation (XML) file, create a study carrel

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame and distributed under a GNU Public License

# November 16, 2020 - first cut; first day of official vacation


# configure
FILE='./input-file.xml'

# sanity check
if [[ -z $1 ]]; then
	echo "Usage: $0 <xml file>" >&2
	exit
fi	

# rename input to a "standard" name; a hack
mv "$1" $FILE

# get the name of newly created directory
NAME=$( pwd )
NAME=$( basename $NAME )

# configure some more
INITIALIZECARREL='initialize-carrel.sh'
BIOARXIV2CACHE='bioarxiv2cache.sh'
MAKE='make.sh'
CARREL2PATRONS='carrel2patrons.sh'
EMAILPATRON='email-patron.sh'

# send a status message
$EMAILPATRON $NAME started

# create a study carrel
echo "Creating study carrel named $NAME" >&2
$INITIALIZECARREL $NAME

# unzip the zip file and put the result in the cache
echo "Creating cache from Bioarxiv xml file" >&2
$BIOARXIV2CACHE $FILE

# build the carrel; the magic happens here
echo "Building study carrel named $NAME" >&2
$MAKE $NAME

# send a status message
$EMAILPATRON $NAME finished

# move the carrel to patron's cache
$CARREL2PATRONS $NAME

# done
exit