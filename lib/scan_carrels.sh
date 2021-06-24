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

# Look at every carrel under the root path passed in.
# build a SQL file which is then run agains the database at the end.
carrel_count=0
sql_commands=$( mktemp )

# Using find in this way lets us stop searching nested directories once we
# find a provenance file.
# See https://www.gnu.org/software/findutils/manual/html_mono/find.html#Finding-the-Shallowest-Instance
#
# Piping the find command into the while loop causes the while loop to run in a
# subshell, which makes the value of carrel_count not available after the loop.
# Instead put output into a file and redirect the file into the while loop.
carrel_list=$( mktemp )
find "$START_DIRECTORY" -exec test -e {}/provenance.tsv \; -print -prune > $carrel_list
while read CARREL; do
    # we have to batch these up in groups of 490 because sqlite only lets us
    # have ~500 items in each "INSERT OR REPLACE" statement.
    if [ $carrel_count -ge 490 ]; then
        echo ";" >> $sql_commands
        sqlite3 $DATABASE_FILE < $sql_commands
        carrel_count=0
    fi
    if [ $carrel_count -eq 0 ]; then
        cat > $sql_commands <<EOF
INSERT OR REPLACE INTO carrels
(owner, shortname, fullpath, status, created, items, words, readability, bytes, keywords)
VALUES 
EOF
    fi
    CARREL=$(realpath $CARREL)
    SHORTNAME=$( basename $CARREL )
    DB="$CARREL/etc/reader.db"
    ITEMS=$( echo "SELECT COUNT( id ) FROM bib;" | sqlite3 $DB )
    WORDS=$( echo "SELECT SUM( words ) FROM bib;" | sqlite3 $DB )
    FLESCH=$( echo "SELECT CAST ( AVG( flesch ) AS INTEGER ) FROM bib;" | sqlite3 $DB )
    KEYWORDS=$( echo "SELECT keyword FROM wrd GROUP BY keyword ORDER BY COUNT( keyword ) DESC LIMIT 5;" | sqlite3 $DB )
    # convert into comma separated list and remove double quotes
    KEYWORDS=$( echo $KEYWORDS | sed 's/ /, /g' | sed 's/"/ /g' )
    SIZE=$( du -b "$CARREL/study-carrel.zip" | cut -f1 )
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

    if [ $carrel_count -ge 1 ]; then
        echo "," >> $sql_commands
    fi
    let carrel_count+=1
    cat >> $sql_commands <<EOF
    ("$OWNER",
        "$SHORTNAME",
        "$CARREL",
        "$CARREL_STATUS",
        "$DATE",
        $ITEMS,
        $WORDS,
        $FLESCH,
        $SIZE,
        "$KEYWORDS")
EOF

done < "$carrel_list"


if [ $carrel_count -gt 0 ]; then
    echo ";" >> $sql_commands
    sqlite3 $DATABASE_FILE < $sql_commands
fi
rm $sql_commands
rm $carrel_list
