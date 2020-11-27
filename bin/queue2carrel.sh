#!/usr/bin/env bash

# queue2carrel.sh - submit queued work

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame and distributed under a GNU Public License

# August    1, 2018 - first investigations and in Lake Geneva after HathiTrust workshop in Milwaukee; "Happy birthday, Barb!"
# August    2, 2018 - back at home and getting closer; works, but only one at a time
# November 27, 2020 - refining to use TSV input; during Thanksgiving holiday in Lancaster and during a pandemic; go figure


# configure
CARRELS="$READERCLASSIC_HOME/carrels"
FILE2CARREL='file2carrel.sh'
URL2CARREL='url2carrel.sh'
URLS2CARREL='urls2carrel.sh'
ZOTERO2CARREL='zotero2carrel.sh'
SEARCH='search.pl'
GUTENBERGQUEUE2ZIP='gutenbergqueue2zip.pl'
ZIP2CARREL='zip2carrel.sh'

# get the input
if [[ -z $1 ]]; then
	echo "Usage: $0 <file>" >&2
	exit
fi
TSV=$1

# initialize and process the input
IFS=$'\t'
cat $TSV | while read TYPE SHORTNAME DATE TIME EMAIL CONTENT; do

	# debug
	echo "       to do: $TSV"       >&2
	echo "        type: $TYPE"      >&2
	echo "  short name: $SHORTNAME" >&2
	echo "        date: $DATE"      >&2
	echo "        time: $TIME"      >&2
	echo "       email: $EMAIL"     >&2
	echo "     content: $CONTENT"   >&2
	echo                            >&2
		
	# conditionally, create the carrel's directory
	if [[ -d "$CARRELS/$SHORTNAME" ]]; then
		echo "Carrel ($SHORTNAME) exists. Exiting." >&2
		exit
	else
		mkdir  "$CARRELS/$SHORTNAME"
	fi

	# for reasons of provenance, copy the queue file to the carrel
	cp $TSV "$CARRELS/$SHORTNAME/provenance.tsv"

	# check for valid/known processes
	if [[ $TYPE = "gutenberg" ]]; then
		
		# create the zip file and its metadata
		echo "Creating zip file" >&2
		$GUTENBERGQUEUE2ZIP $SHORTNAME $CONTENT

		# make sane and do the work
		echo "Making sane and doing the work ($ZIP2CARREL)" >&2
		cd "$CARRELS/$SHORTNAME"
		$ZIP2CARREL ./input-file.zip 1>standard-output.txt 2>standard-error.txt &

	# unknown process; update database
	else 

		echo "Error: Unknown type ($TYPE). Call Eric.\n" >&2
	
	fi

# fini
done
exit



