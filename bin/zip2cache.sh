#!/usr/bin/env bash

# zip2cache.sh - given the name of a study carrel, fill the cache with the contents of a .zip file

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame and distributed under a GNU Public License

# May      22, 2019 - first cut
# September 6, 2019 - quoted a basename file; escaped values in id


# configure
CARRELS="$READERCLASSIC_HOME/carrels"
METADATA2SQL='metadata2sql.py'
DB='./etc/reader.db'

# sanity check
if [[ -z "$1" ]]; then
	echo "Usage: $0 <name>" >&2
	exit
fi

# get input and make sane
NAME=$1
cd "$CARRELS/$NAME"

# initialize temporary file system and unzip
rm -rf ./tmp/input
mkdir ./tmp/input
unzip input-file.zip -d ./tmp/input -x '*MACOSX*' 1>&2 

# copy known file types to the cache; normalize file names here
find tmp/input -name "*.pdf"  | parallel --will-cite mv {} cache
find tmp/input -name "*.PDF"  | parallel --will-cite mv {} cache
find tmp/input -name "*.xml"  | parallel --will-cite mv {} cache
find tmp/input -name "*.htm"  | parallel --will-cite mv {} cache
find tmp/input -name "*.html" | parallel --will-cite mv {} cache
find tmp/input -name "*.txt"  | parallel --will-cite mv {} cache
find tmp/input -name "*.doc"  | parallel --will-cite mv {} cache
find tmp/input -name "*.docx" | parallel --will-cite mv {} cache
find tmp/input -name "*.pptx" | parallel --will-cite mv {} cache
find tmp/input -name "*.xlsx" | parallel --will-cite mv {} cache

# configure possible metadata file
DIRECTORIES=( $(find ./tmp/input -type d) )
DIRECTORY=${DIRECTORIES[1]}
METADATA="$DIRECTORY/metadata.csv"

# re-initialize bibliographics sql
rm -rf ./tmp/bibliographics.sql

# check for optional metadata file
if [[ -f $METADATA ]]; then

	# process metadata
    $METADATA2SQL $METADATA > ./tmp/bibliographics.sql

# initialize bib table
else
	
	# process each file in the cache
	for FILE in cache/* ; do
    
    	# parse
    	FILE=$( basename "$FILE" )
    	ID=$( echo ${FILE%.*} )
    	
    	# escape
    	ID=$( echo "$ID" | sed "s/'/''/g" )
    	
		# output
		echo "INSERT INTO bib ( 'id' ) VALUES ( '$ID' );" >> ./tmp/bibliographics.sql
    	
	done

fi

# update the bibliographic table
echo "=== updating bibliographic database" >&2
echo "BEGIN TRANSACTION;"     > ./tmp/update-bibliographics.sql
cat ./tmp/bibliographics.sql >> ./tmp/update-bibliographics.sql
echo "END TRANSACTION;"      >> ./tmp/update-bibliographics.sql
cat ./tmp/update-bibliographics.sql | sqlite3 $DB

# done
exit
