#!/usr/bin/env bash

# file2carrel.sh - given a file, create a study carrel

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame and distributed under a GNU Public License

# July     19, 2018 - first cut
# July     20, 2018 - started getting to work from a remote machine and sending email
# April    20, 2019 - building off of other work; at the Culver Coffee Shop
# November 17, 2019 - hacked to accepte command line input and rename input file
# November 15, 2019 - hacking on vacation during a pandemic


# configure
FILE='./input-file.ukn'

# sanity check
if [[ -z $1 ]]; then
	echo "Usage: $0 <file>" >&2
	exit
fi	

# rename input to a "standard" name; a hack
mv "$1" $FILE

# get the name of newly created directory
NAME=$( pwd )
NAME=$( basename $NAME )

# configure some more
CACHE='cache';
INITIALIZECARREL='initialize-carrel.sh'
MAKE='make.sh'
DB='./etc/reader.db'

# create a study carrel
echo "Creating study carrel named $NAME" >&2
$INITIALIZECARREL $NAME

# fill up the cache with the given files
echo "Building cache" >&2
echo "" >&2
cp  $FILE $CACHE

# process each file in the cache
for FILE in cache/* ; do

	# parse
	FILE=$( basename $FILE )
	ID=$( echo ${FILE%.*} )
	
	# output
	echo "INSERT INTO bib ( 'id' ) VALUES ( '$ID' );" >> ./tmp/bibliographics.sql
	
done
	
# update the bibliographic table
echo "BEGIN TRANSACTION;"     > ./tmp/update-bibliographics.sql
cat ./tmp/bibliographics.sql >> ./tmp/update-bibliographics.sql
echo "END TRANSACTION;"      >> ./tmp/update-bibliographics.sql
cat ./tmp/update-bibliographics.sql | sqlite3 $DB

# build the carrel; the magic happens here
echo "Building study carrel named $NAME" >&2
$MAKE $NAME

# done
exit
