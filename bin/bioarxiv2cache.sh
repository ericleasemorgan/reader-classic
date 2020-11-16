#!/usr/bin/env bash

# bioarxiv2cache.sh - given an XML file of specific shape, cache PDF files from Bioarxiv and update bibliographics

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# September 5, 2020 - first cut
# November 16, 2020 - moving to Azure; first real day of vacation


# configure
XML2TSV='bioarxiv2tsv.sh'
HARVEST='bioarxiv-harvest.sh'
METADATA2SQL='metadata2sql.py'
TSV='./metadata.tsv'
CSV='./metadata.csv'
DB='./etc/reader.db'

# sanity check
if [[ -z $1 ]]; then
	echo "Usage: $0 <xml>" >&2
	exit
fi

# get input
XML="$1"

# transform XML to TSV and harvest
$XML2TSV $XML > "$TSV"
$HARVEST "$TSV"

# convert TSV to CSV and then create SQL
perl -lpe 's/"/""/g; s/^|$/"/g; s/\t/","/g' < $TSV > $CSV
$METADATA2SQL $CSV > ./tmp/bibliographics.sql

# update the bibliographic table
echo "=== updating bibliographic database" >&2
echo "BEGIN TRANSACTION;"     > ./tmp/update-bibliographics.sql
cat ./tmp/bibliographics.sql >> ./tmp/update-bibliographics.sql
echo "END TRANSACTION;"      >> ./tmp/update-bibliographics.sql
cat ./tmp/update-bibliographics.sql | sqlite3 $DB

# done
exit
