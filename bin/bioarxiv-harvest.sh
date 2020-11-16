#!/usr/bin/env bash

# harvest.sh - given a TSV file of a specific shape, cache PDF files from BioArxiv

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# September 5, 2020 - first cut


# configure
RESOLVER='https://biorxiv.org/lookup/doi/'
BIOARXIV='https://biorxiv.org'
CACHE='./cache'
PARAMETERS='./tmp/todo.tsv'

# sanity check
if [[ -z $1 ]]; then
	echo "Usage: $0 <tsv>" >&2
	exit
fi

# get input
METADATA="$1"

# initialize
rm -rf "$PARAMETERS"
touch "$PARAMETERS"

# process each record in the metadata file; create parameters for wget
tail -n+2 "$METADATA" | while read RECORD; do

	IFS=$"\t"
	DOI=$( echo $RECORD | cut -f5 )
	FILE=$( echo $RECORD | cut -f6 )
	echo $DOI  >&2
	echo $FILE >&2
	echo       >&2
	
	BASE=$( curl --silent -L "$RESOLVER$DOI" | grep 'application/pdf' | cut -d'=' -f5 | cut -d'"' -f2 )
	printf "$BIOARXIV$BASE\t$CACHE/$FILE\n" >> "$PARAMETERS"
	
# fini
done

# parallel-ize wget to actually cache the files
cat "$PARAMETERS" | parallel --will-cite --colsep="\t" wget --no-verbose -O {2} {1}

# clean up and done
rm -rf "$PARAMETERS"
exit
