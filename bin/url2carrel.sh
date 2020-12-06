#!/usr/bin/env bash

# url2carrel.sh - give single url, create a study carrel

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame and distributed under a GNU Public License

# July     17, 2018 - first cut
# April    12, 2019 - got it working on the Science Gateway cluster
# November 15, 2020 - migrating to Azure; while in Lancaster for a holiday


# get the name of newly created directory
NAME=$( pwd )
NAME=$( basename $NAME )

# configure
CARRELS="$READERCLASSIC_HOME/carrels"
INITIALIZECARREL='initialize-carrel.sh'
TMP="$CARRELS/$NAME/tmp"
HTML2URLS='html2urls.pl'
URL2CACHE='urls2cache.pl'
CACHE='cache';
MAKE='make.sh'
SUFFIX='etc'
TIMEOUT=5
DB='./etc/reader.db'
CARREL2PATRONS='carrel2patrons.sh'
EMAILPATRON='email-patron.sh'

# validate input
if [[ -z $1 ]]; then

	echo "Usage: $0 <url> [<address>]" >&2
	exit

fi

# get the input
URL=$1

# send a status message
$EMAILPATRON $NAME started

# create a study carrel
echo "Creating study carrel named $NAME" >&2
$INITIALIZECARREL $NAME

# get the given url and cache the content locally
echo "Getting URL ($URL) and saving it ($TMP/$NAME)" >&2
wget -t $TIMEOUT -k -O "$TMP/$NAME" $URL  >&2

# extract the urls in the cache
echo "Extracting URLs ($TMP/$NAME) and saving ($TMP/$NAME.txt)" >&2
$HTML2URLS "$TMP/$NAME" > "$TMP/$NAME.txt"

# process each line from cache and... cache again
echo "Processing each URL in $TMP/$NAME.txt" >&2
cat "$TMP/$NAME.txt" | parallel --will-cite $URL2CACHE {} "$CARRELS/$NAME/$CACHE"

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
echo "" >&2

# send a status message
$EMAILPATRON $NAME finished

# move the carrel to patron's cache
$CARREL2PATRONS $NAME

# done
exit
