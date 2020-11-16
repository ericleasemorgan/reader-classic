#!/usr/bin/env bash

# zip2carrel.sh - given a pre-configured zip file, create a Distant Reader Study Carrel

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame and distributed under a GNU Public License

# May      22, 2019 - first cut
# November 17, 2019 - hacked to accepte command line input and rename input file
# November 15, 2020 - making working on a big compute; in Lancaster during a pandemic


# configure
FILE='./input-file.zip'

# sanity check
if [[ -z $1 ]]; then
	echo "Usage: $0 <zip file>" >&2
	exit
fi	

# rename input to a "standard" name; a hack
mv "$1" $FILE

# get the name of newly created directory
NAME=$( pwd )
NAME=$( basename $NAME )

# configure some more
INITIALIZECARREL='initialize-carrel.sh'
CARRELS="$READERCLASSIC_HOME/carrels"
TMP="$CARRELS/$NAME/tmp"
CACHE='cache';
ZIP2CACHE='zip2cache.sh'
MAKE='make.sh'

# create a study carrel
echo "Creating study carrel named $NAME" >&2
echo "" >&2
$INITIALIZECARREL $NAME

# unzip the zip file and put the result in the cache
echo "Unzipping $ZIP" >&2
$ZIP2CACHE $NAME

# build the carrel; the magic happens here
echo "Building study carrel named $NAME" >&2
$MAKE $NAME
echo "" >&2

# done
exit