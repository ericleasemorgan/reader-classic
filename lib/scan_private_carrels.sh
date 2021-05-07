#!/bin/bash

#
# scan_private_carrels.sh <start directory>
#
# A study carrel is a directory that has a file named "provenance.tsv" in it.
# Any found study carrels are entered into the database (if they aren't there
# already).
#
# n.b. study carrels cannot be nested.

DATABASE_FILE="/data-disk/etc/reader-patrons.db"


find $1 -type f -name "provenance.tsv" | while read provenance; do
    CARREL=$(dirname $(realpath $provenance))
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
        "private",
        "$DATE",
        $ITEMS,
        $WORDS,
        $FLESCH,
        $SIZE);
EOF

done
