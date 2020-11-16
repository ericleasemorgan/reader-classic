#!/usr/bin/env bash

# xml2tsv.sh - given an XML file of specific shape, output a TSV file

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# September 5, 2020 - first cut


# configure
XML2TSV="$READERCLASSIC_HOME/etc/bioarxiv2tsv.xsl"

# sanity check
if [[ -z $1 ]]; then
	echo "Usage: $0 <xml>" >&2
	exit
fi

# get input
XML="$1"

xsltproc $XML2TSV $XML