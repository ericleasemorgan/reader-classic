#!/usr/bin/env bash

# make-pages.sh - given a study carrel, create sets of HTML pages (a narrative report)

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# November 15, 2020 - create a long long time ago, but first notes; in Lancaster


# configure
CARREL2ABOUT='carrel2about.py'
CARREL2JSON='carrel2json.py'
CARREL2SEARCH='carrel2search.pl'
CARRELS="$READERCLASSIC_HOME/carrels"
CORPUS2FILE='corpus2file.sh'
LISTQUESTIONS='list-questions.sh'
TSV2COMPLEX='tsv2htm-complex.py'
TSV2ENTITIES='tsv2htm-entities.py'
TSV2HTM='tsv2htm.py'
TSV2QUESTIONS='tsv2htm-questions.py'
DB2BIBLIOGRAPHICS='db2tsv-bibliographics.py'
TSV2BIBLIOGRAPHICS='tsv2htm-bibliographics.py'
TXT='txt/*.txt'

# sanity check
if [[ -z "$1" ]]; then
	echo "Usage: $0 <carrel>" >&2
	exit
fi

# get input
CARREL=$1

# make sane
cd "$CARRELS/$CARREL"

# begin the work; index page
$CARREL2ABOUT > index.htm

# htm files
echo "==== make-pages.sh htm files" >&2
$TSV2HTM adjective   ./tsv/adjectives.tsv   > ./htm/adjectives.htm   &
$TSV2HTM adverb      ./tsv/adverbs.tsv      > ./htm/adverbs.htm      &
$TSV2HTM bigram      ./tsv/bigrams.tsv      > ./htm/bigrams.htm      &
$TSV2HTM keyword     ./tsv/keywords.tsv     > ./htm/keywords.htm     &
$TSV2HTM noun        ./tsv/nouns.tsv        > ./htm/nouns.htm        &
$TSV2HTM pronoun     ./tsv/pronouns.tsv     > ./htm/pronouns.htm     &
$TSV2HTM proper      ./tsv/proper-nouns.tsv > ./htm/proper-nouns.htm &
$TSV2HTM quadgram    ./tsv/quadgrams.tsv    > ./htm/quadgrams.htm    &
$TSV2HTM trigram     ./tsv/trigrams.tsv     > ./htm/trigrams.htm     &
$TSV2HTM unigram     ./tsv/unigrams.tsv     > ./htm/unigrams.htm     &
$TSV2HTM verb        ./tsv/verbs.tsv        > ./htm/verbs.htm        &

# more complex tsv files
echo "==== make-pages.sh complex files" >&2
$TSV2COMPLEX noun      verb ./tsv/noun-verb.tsv       > ./htm/noun-verb.htm      &
$TSV2COMPLEX adjective noun ./tsv/adjective-noun.tsv  > ./htm/adjective-noun.htm &

# named entities
echo "==== make-pages.sh named enities" >&2
$TSV2ENTITIES ./tsv/entities.tsv  > ./htm/entities.htm &

# bibliographics
echo "==== making bibliographics" >&2
$DB2BIBLIOGRAPHICS > ./tsv/bibliographics.tsv
$TSV2BIBLIOGRAPHICS ./tsv/bibliographics.tsv > ./htm/bibliographics.htm

# list questions
echo "==== make-pages.sh questions" >&2
echo -e "identifier\tquestion"      > ./tsv/questions.tsv
$LISTQUESTIONS $CARREL             >> ./tsv/questions.tsv
$TSV2QUESTIONS ./tsv/questions.tsv  > ./htm/questions.htm

# create search page
echo "==== make-pages.sh search" >&2
$CARREL2SEARCH $CARREL > ./htm/search.htm

# create data and page for topic modeling
echo "==== make-pages.sh topic modeling corpus" >&2
find txt/*.txt | parallel --will-cite $CORPUS2FILE {} > ./etc/model-data.txt
cp $READERCLASSIC_HOME/etc/template-model.htm ./htm/topic-model.htm

# done
wait
exit
