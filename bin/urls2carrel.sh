#!/usr/bin/env bash

# urls2carrel.sh - given a list of URLs in a plain text file, create a Distant Reader Study Carrel

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame and distributed under a GNU Public License

# July      8, 2018 - first cut
# July     14, 2018 - more investigation
# July     16, 2018 - made things more module
# November 17, 2019 - hacked to accepte command line input and rename input file
# November 15, 2020 - migrating to Azure


# sanity check
if [[ -z $1 ]]; then
	echo "Usage: $0 <file>" >&2
	exit
fi	

# rename input to a "standard" name; a hack
mv "$1" input-file.txt

# configure input
FILE=./input-file.txt

# get the name of newly created directory
NAME=$( pwd )
NAME=$( basename $NAME )

# configure some more
CARRELS="$READERCLASSIC_HOME/carrels"
TMP="$CARRELS/$NAME/tmp"
CACHE='cache';
MAKE='make.sh'
CARREL2ZIP='carrel2zip.pl'
DB='./etc/reader.db'
URL2CACHE='urls2cache.pl'
INITIALIZECARREL='initialize-carrel.sh'
CARREL2PATRONS='carrel2patrons.sh'


# create a study carrel
echo "Creating study carrel named $NAME" >&2
$INITIALIZECARREL $NAME

# process each line from cache and... cache again
echo "Processing each URL in $TMP/$NAME.txt" >&2
cat "./$FILE" | parallel --will-cite $URL2CACHE {} $CACHE

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

# move the carrel to patron's cache
$CARREL2PATRONS $NAME

# done
exit
