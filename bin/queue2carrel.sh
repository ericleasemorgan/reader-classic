#!/usr/bin/env bash

# queue2carrel.sh - submit queued work

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame and distributed under a GNU Public License

# August    1, 2018 - first investigations and in Lake Geneva after HathiTrust workshop in Milwaukee; "Happy birthday, Barb!"
# August    2, 2018 - back at home and getting closer; works, but only one at a time
# November 27, 2020 - refining to use TSV input; during Thanksgiving holiday in Lancaster and during a pandemic; go figure
# November 28, 2020 - added url2carrel and biorxiv2carrel


# configure
BACKLOG='/data-disk/reader-compute/reader-classic/queue/backlog'
BIOARXIV2CARREL='bioarxiv2carrel.sh'
CARRELS="$READERCLASSIC_HOME/carrels"
FILE2CARREL='file2carrel.sh'
GUTENBERGQUEUE2ZIP='gutenbergqueue2zip.pl'
SEARCH='search.pl'
URL2CARREL='url2carrel.sh'
URLS2CARREL='urls2carrel.sh'
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

	# check for valid/known processes; gutenberg
	if [[ $TYPE = "gutenberg" ]]; then
		
		# create the zip file and its metadata
		echo "Creating zip file" >&2
		$GUTENBERGQUEUE2ZIP $SHORTNAME $CONTENT

		# make sane and do the work
		echo "Making sane and doing the work ($ZIP2CARREL)" >&2
		cd "$CARRELS/$SHORTNAME"
		$ZIP2CARREL ./input-file.zip 1>standard-output.txt 2>standard-error.txt &

	# url2carrel
	elif [[ $TYPE = "url2carrel" ]]; then
	
		# make sane and do the work
		echo "Making sane and doing the work ($URL2CARREL)" >&2
		cd "$CARRELS/$SHORTNAME"
		$URL2CARREL "$CONTENT" 1>standard-output.txt 2>standard-error.txt &
	
	# urls2carrel
	elif [[ $TYPE = "urls2carrel" ]]; then
	
		# make sane and do the work
		echo "Making sane and doing the work ($URLS2CARREL)" >&2
		cd "$CARRELS/$SHORTNAME"
		mv $BACKLOG/$CONTENT ./input-urls.txt
		$URLS2CARREL ./input-urls.txt 1>standard-output.txt 2>standard-error.txt &
	
	# file2carrel
	elif [[ $TYPE = "file2carrel" ]]; then
	
		# make sane and do the work
		echo "Making sane and doing the work ($FILE2CARREL)" >&2
		cd "$CARRELS/$SHORTNAME"
		mv $BACKLOG/$CONTENT $CONTENT
		$FILE2CARREL $CONTENT 1>standard-output.txt 2>standard-error.txt &
	
	# zip2carrel
	elif [[ $TYPE = "zip2carrel" ]]; then
	
		# make sane and do the work
		echo "Making sane and doing the work ($ZIP2CARREL)" >&2
		cd "$CARRELS/$SHORTNAME"
		mv $BACKLOG/$CONTENT ./input-file.zip
		$ZIP2CARREL ./input-file.zip 1>standard-output.txt 2>standard-error.txt &
	
	# biorxiv
	elif [[ $TYPE = "biorxiv" ]]; then
	
		# make sane and do the work
		echo "Making sane and doing the work ($BIOARXIV2CARREL)" >&2
		cd "$CARRELS/$SHORTNAME"
		mv $BACKLOG/$CONTENT ./biorxiv.xml
		$BIOARXIV2CARREL ./biorxiv.xml 1>standard-output.txt 2>standard-error.txt &
	
	# unknown process
	else 

		echo "Error: Unknown type ($TYPE). Call Eric.\n" >&2
	
	fi

# fini
done
exit



