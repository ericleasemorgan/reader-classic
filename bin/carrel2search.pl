#!/usr/bin/env perl

# configure
use constant READERCLASSIC_HOME => $ENV{ 'READERCLASSIC_HOME' };
use constant CARRELS            => READERCLASSIC_HOME . '/carrels';
use constant DATABASE           => 'etc/reader.db';
use constant DRIVER             => 'SQLite';
use constant QUERY              => 'SELECT id, title, summary FROM bib;';
use constant TEMPLATE           => READERCLASSIC_HOME . '/etc/template-search.htm';

# require
use DBI;
use strict;
use JSON;

my $carrel = $ARGV[ 0 ];
if ( ! $carrel ) { die "Usage: $0 <short-name>\n" }

# initialize
my $driver   = DRIVER;
my $database = CARRELS . "/$carrel/" . DATABASE;
my $template = TEMPLATE;
my @data     = ();

# open the database and search
my $dbh = DBI->connect( "DBI:$driver:dbname=$database", '', '', { RaiseError => 1 } ) or die $DBI::errstr;
my $handle = $dbh->prepare( QUERY );
$handle->execute() or die $DBI::errstr;

# initialize the data and update it
while( my $bibliographics = $handle->fetchrow_hashref ) {

	# parse
	my $id       = $$bibliographics{ 'id' };
	my $title    = $$bibliographics{ 'title' };
	my $summary  = $$bibliographics{ 'summary' };

	# update
	push( @data, { 'id' => $id, 'title' => $title, 'summary' => $summary } );

}

# transform the data into json
my $json = JSON->new->encode( [ @data ] );

# read the template, do the substitution, output, and done
my $html =  &slurp( $template );
$html    =~ s/##JSON##/$json/e;
print $html;
exit;

sub slurp {
	my $f = shift;
	open ( F, $f ) or die "Can't open $f: $!\n";
	my $r = do { local $/; <F> };
	close F;
	return $r;
}