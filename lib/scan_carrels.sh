#!/bin/bash

#
# scan_carrels.sh <start directory> [public|private]
#
# A study carrel is a directory that has a file named "provenance.tsv" in it.
# Any found study carrels are entered into the database (if they aren't there
# already).
#
# The optional "public" or "private" word tells the script whether to record
# the carrel as being in the public carrel list or not. If not given it
# defaults to "private".
#
# note: study carrels cannot be nested.

DATABASE_FILE="/data-disk/etc/reader-patrons.db"

START_DIRECTORY="$1"
case $2 in
    public)
        CARREL_STATUS="public"
        ;;
    *)
        CARREL_STATUS="private"
        ;;
esac


# Using find in this way lets us stop searching nested directories once we
# find a provenance file.
# See https://www.gnu.org/software/findutils/manual/html_mono/find.html#Finding-the-Shallowest-Instance
find "$START_DIRECTORY" -exec test -e {}/provenance.tsv \; -print -prune | while read CARREL; do
    CARREL=$(realpath $CARREL)
    SHORTNAME=$( basename $CARREL )
    ITEMS=$( echo "SELECT COUNT( id ) FROM bib;" | sqlite3 "$CARREL/etc/reader.db" )
    WORDS=$( echo "SELECT SUM( words ) FROM bib;" | sqlite3 "$CARREL/etc/reader.db" )
    FLESCH=$( echo "SELECT RTRIM( ROUND( AVG( flesch ) ), '.0' ) FROM bib;" | sqlite3 "$CARREL/etc/reader.db" )
    SIZE=$( du "$CARREL/study-carrel.zip" | cut -f1 )
    DATE=$( awk '{print $3}' $CARREL/provenance.tsv )
    OWNER=$( awk '{print $5}' $CARREL/provenance.tsv )

    # Supply defaults since these are missing on a few carrels
    if [ -z $ITEMS ]; then
        ITEMS=0
    fi
    if [ -z $WORDS ]; then
        WORDS=0
    fi
    if [ -z $FLESCH ]; then
        FLESCH=0
    fi
    if [ -z $SIZE ]; then
        SIZE=0
    fi

    sqlite3 $DATABASE_FILE <<EOF
INSERT OR REPLACE INTO carrels
(owner, shortname, fullpath, status, created, items, words, readability, bytes)
VALUES ("$OWNER",
        "$SHORTNAME",
        "$CARREL",
        "$CARREL_STATUS",
        "$DATE",
        $ITEMS,
        $WORDS,
        $FLESCH,
        $SIZE);
EOF

done
