#!/usr/bin/env bash

# make.sh - one script to rule them all

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame and distributed under a GNU Public License

# July 10, 2018 - first cut


# configure
CACHE2TXT='cache2txt.sh'
CARRELS="$READERCLASSIC_HOME/carrels"
CORPUS="./etc/reader.txt"
DB2REPORT='db2report.sh'
MAKEPAGES='make-pages.sh'
MAP='map.sh'
REDUCE='reduce.sh'
REPORT='etc/report.txt'
CARREL2ZIP='carrel2zip.pl'
EMAILPATRON='email-patron.sh'

# sanity check
if [[ -z "$1" ]]; then
	echo "Usage: $0 <name>" >&2
	exit
fi

# get input
NAME=$1

# start tika
#java -jar /data-disk/lib/tika-server.jar &
#PID=$!
#sleep 10

# transform cache to plain text files
$CACHE2TXT $NAME

# extract parts-of-speech, named entities, etc
$MAP $NAME
#kill $PID

# build the database
$REDUCE $NAME

# build ./etc/reader.txt; a plain text version of the whole thing
echo "Building ./etc/reader.txt" >&2
rm -rf $CORPUS >&2
find "./txt" -name '*.txt' -exec cat {} >> "$CORPUS" \;
#sed -e "s/[[:punct:]]\+//g" $CORPUS > ./tmp/corpus.001
tr '[:upper:]' '[:lower:]' < "$CORPUS" > ./tmp/corpus.001
tr '[:digit:]' ' ' < ./tmp/corpus.001 > ./tmp/corpus.002
tr '\n' ' ' < ./tmp/corpus.002 > ./tmp/corpus.003
tr -s ' ' < ./tmp/corpus.003 > "$CORPUS"

# output a report against the database
$DB2REPORT $NAME > "$CARRELS/$NAME/$REPORT"
cat "$CARRELS/$NAME/$REPORT"

# send a status message
$EMAILPATRON $NAME processing

# create about file
$MAKEPAGES $NAME

# zip it up
echo "Zipping study carrel" >&2
rm -rf ./tmp
echo "" >&2
$CARREL2ZIP $NAME

# make zip file accessible
cp "./etc/reader.zip" "./study-carrel.zip"

# done
exit
