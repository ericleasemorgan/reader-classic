#!/usr/bin/env bash

# map.sh - given an directory (of .txt files), map various types of information

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame and distributed under a GNU Public License

# June     27, 2018 - first cut
# July     10, 2018 - started using parallel, and removed files2txt processing
# July     12, 2018 - migrating to the cluster
# February  3, 2020 - tweaked a lot to accomodate large files
# November 15, 2020 - migrating to Azure; in Lancaster


export OMP_NUM_THREADS=1

# configure
TXT='txt';
CACHE='cache'

# sanity check
if [[ -z "$1" ]]; then
	echo "Usage: $0 <name>" >&2
	exit
fi

# initialize
NAME=$1
INPUT="$TXT"

# extract addresses, urls, and keywords
find "$INPUT" -name '*.txt' | parallel --will-cite txt2adr.sh {} 
find "$INPUT" -name '*.txt' | parallel --will-cite txt2urls.sh {}

# extract bibliographics
find "$CACHE" -type f | parallel --will-cite file2bib.sh {}

# extract parts-of-speech and named-entities
find "$INPUT" -name '*.txt' | parallel --will-cite txt2ent.sh {}
find "$INPUT" -name '*.txt' | parallel --will-cite txt2pos.sh {}

# extract keywords
find "$INPUT" -name '*.txt' | parallel --will-cite txt2keywords.sh {}

# wait and done
wait
echo "Done mapping." >&2
exit
