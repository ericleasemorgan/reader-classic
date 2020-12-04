#!/usr/bin/env bash

# monitor-queue.sh - look for carrels to create, and if found, create them

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# June      2, 2020 - first cut
# June      7, 2020 - created in-process... processing
# November 27, 2020 - started implementing for Reader Classic

# configure
TODO="$READERCLASSIC_HOME/queue/todo"
INPROCESS="$READERCLASSIC_HOME/queue/in-process"
SUBMITTTED="$READERCLASSIC_HOME/queue/submitted.tsv"
QUEUE2CARREL='queue2carrel.sh'

# process each to-do item
find $TODO -name '*.tsv' | while read FILE; do
	
	# debug
	echo "===================" >&2
	cat $FILE                  >&2
	echo ''                    >&2

	# move to-do item to in-process
	cat $FILE >> $SUBMITTTED	
	BASENAME=$( basename $FILE .tsv )
	mv $FILE $INPROCESS/$BASENAME.tsv
	
	# do the work and clean up
	$QUEUE2CARREL $INPROCESS/$BASENAME.tsv 2>> ~/log/queue2carrel.log
	rm -rf $INPROCESS/$BASENAME.tsv
	
# fini
done
exit