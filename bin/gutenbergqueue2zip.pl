#!/usr/bin/env perl

# gutenbergqueue2zip.pl - given a carrel name and a Solr query, create a zip file of documents

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# November 27, 2020 - building for Reader Classic; during Thanksgiving vacation in Lancaster during a pandemic

# configure
use constant READERCLASSIC_HOME => $ENV{ 'READERCLASSIC_HOME' };
use constant SOLR               => 'http://10.0.1.11:8983/solr/reader-gutenberg';
use constant TEXTS              => '/data-disk/reader-compute/reader-gutenberg/texts';
use constant ROWS               => 999;
use constant DIRECTORY          => 'input-file';
use constant ROOT               => 'http://distantreader.org/gutenberg/texts';
use constant HEADER             => ( 'gid', 'author', 'title', 'file', 'local url', 'remote url' );
use constant METADATA           => 'metadata.csv';

# require
use Archive::Zip;
use File::Copy;
use File::Path;
use strict;
use WebService::Solr;

# get input; sanity check
my $carrel = $ARGV[ 0 ];
my $query  = $ARGV[ 1 ];
if ( ! $carrel || ! $query ) { die "Usage: $0 <short name> <query>\n" }

# initialize
my $solr      = WebService::Solr->new( SOLR );
my $texts     = TEXTS;
my $carrels   = READERCLASSIC_HOME . "/carrels";
my $directory = DIRECTORY;
my $root      = ROOT;
my $metadata  = METADATA;

# make sure the named carrel already exists
if ( ! -d "$carrels/$carrel" ) { die "The carrel ($carrels/$carrel) does not exist. Create it.\n" }

# create the directory where the files and their metadata will be saved
mkdir "$carrels/$carrel/$directory" or die "Can't make $carrels/$carrel/$directory ($!). Call Eric.\n";

# build the search options
my %search_options = ();
$search_options{ 'rows' } = ROWS;

# search
my $response = $solr->search( $query, \%search_options );

# get the total number of hits
my $total = $response->content->{ 'response' }->{ 'numFound' };

# get number of hits returned
my @hits = $response->docs;

# start the output
warn "Your search found $total item(s) and " . scalar( @hits ) . " item(s) are displayed.\n\n";

# loop through each document
my @records = ();
for my $doc ( $response->docs ) {

	# parse
	my $author          = $doc->value_for(  'author' );
	my $title           = $doc->value_for(  'title' );
	my $gid             = $doc->value_for(  'gid' );
	my $remote          = $doc->value_for(  'file' );
	#my $rights          = $doc->value_for(  'rights' );
	#my $language        = $doc->value_for(  'language' );
	#my @subjects        = $doc->values_for( 'subject' );
	#my @classifications = $doc->values_for( 'classification' );

	# local file
	my $file = "$gid.txt";

	# build the url
	my $local = "$root/$gid.txt";

	# output
	warn "               title: $title\n";
	warn "              author: $author\n";
	#warn "          subject(s): " . join( '; ', @subjects ), "\n";
	#warn "  classifications(s): " . join( '; ', @classifications ), "\n";
	#warn "            language: $language\n";
	#warn "              rights: $rights\n";
	warn "                file: $file\n";
	warn "          remote URL: $remote\n";
	warn "          local file: $local\n";
	warn "                 gid: $gid\n";
	warn "\n";

	# escape
	$author =~ s/"/""/g;
	$title  =~ s/"/""/g;

	# create a record and then update the "database"; quote marks are obtuse!
	my @record = ( qq("$gid), $author, $title, $file, $local, qq($remote") );
	push( @records, join( '","', @record ) );
	
	# copy the file to the directory
	copy( "$texts/$gid.txt", "$carrels/$carrel/$directory/$gid.txt" ) or die "Can't copy file to directory ($!). Call Eric.\n";

}

# build a CSV stream from the TSV; quote marks are still obtuse!
my $csv  = '"'. join( '","', HEADER ) . '"' . "\n";
$csv    .= join( "\n", @records );

# create the metadata file
my $metadata = "$carrels/$carrel/$directory/$metadata";
open FILE, " > $metadata" or die "Can't create $metadata ($!). Call Eric.\n";
print FILE $csv;
close FILE;

# compress the result
my $zip = Archive::Zip->new();
$zip->addTree( "$carrels/$carrel/$directory", $directory );
$zip->writeToFileNamed( "$carrels/$carrel/$directory.zip" );

# clean up and done
rmtree "$carrels/$carrel/$directory" or die "Can't remove $carrels/$carrel/$directory ($!). Call Eric.\n";
exit;
