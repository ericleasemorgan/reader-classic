#!/data-disk/bin/perl

# gids2tsv.cgi - given one more more identifiers, create a zip file conducive for the Distant Reader

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# March     9, 2017 - first cut; I'm doing great!
# April     9, 2018 - migrating to Project English
# May       9, 2019 - migrating to Project Gutenberg
# November 26, 2020 - migrating to Reader Gutenberg; Thanksgiving Day in Lancaster during a pandemic


# configure
use constant DATABASE => '/data-disk/reader-compute/reader-gutenberg/etc/gutenberg.db';
use constant DRIVER   => 'SQLite';
use constant HEADER   => ( 'gid', 'author', 'title', 'file', 'local url', 'remote url' );
use constant QUERY    => qq(SELECT t.*, f.file FROM titles as t, files as f WHERE (##CLAUSE##) AND t.language IS 'en' AND f.file LIKE '%.txt.utf-8' AND t.gid = f.gid ORDER BY t.gid;);
use constant ROOT     => 'http://distantreader.org/gutenberg/texts';
use constant CARRELS  => './carrels';
use constant METADATA => 'metadata.csv';
use constant TEXTS    => './texts';


# require
use Archive::Zip;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use DBI;
use File::Copy;
use File::Path;
use strict;

# initialize
my $cgi    = CGI->new;
my $carrel = $cgi->param( 'carrel' );
my $gids   = $cgi->param( 'gids' );

# no input; display home page
if ( ! $gids || ! $carrel ) {

	# get input and sanitize it
	my @gids =  ();
	$gids    =~ s/[[:punct:]]/ /g;
	$gids    =~ s/ +/ /g;
	@gids    =  split( ' ', $gids );

	# build the html
	my $html =  &form;
	$html    =~ s/##GIDS##/join( ' ', @gids )/e;

	print $cgi->header;
	print $html;
	
}

# process input
else {

	# get input and sanitize it
	my @gids =  ();
	$gids    =~ s/[[:punct:]]/ /g;
	$gids    =~ s/ +/ /g;
	@gids    =  split( ' ', $gids );

	# initialize
	my $root     = ROOT;
	my $carrels  = CARRELS;
	my $texts    = TEXTS;
	my $metadata = METADATA;

	# VALIDATE INPUT HERE; we don't need to leave an opportunity for sql injection!

	# create the sql where clause and then build the whole sql query
	my @queries =  ();
	for my $gid ( @gids ) { push( @queries, "t.gid='$gid'" ) }
	my $sql     =  QUERY;
	$sql        =~ s/##CLAUSE##/join( ' OR ', @queries )/e;
	
	# execute the query
	my $driver    = DRIVER; 
	my $database  = DATABASE;
	my $dbh       = DBI->connect( "DBI:$driver:dbname=$database", '', '', { RaiseError => 1 } ) or die $DBI::errstr;
	my $handle    = $dbh->prepare( $sql );
	$handle->execute() or die $DBI::errstr;

	# create the directory where the data and metadata will be saved
	my $directory = "$carrels/$carrel";
	mkdir $directory or die "Can't make $directory ($!). Call Eric.\n";
	
	# process each title in the found set
	my @records = ();
	while( my $titles = $handle->fetchrow_hashref ) {
	
		# parse the title data
		my $author = $$titles{ 'author' };
		my $remote = $$titles{ 'file' };
		my $gid    = $$titles{ 'gid' };
		my $title  = $$titles{ 'title' };
		
		# local file
		my $file = "$gid.txt";
		
		# build the url
		my $local = "$root/$gid.txt";

		# escape
		$author =~ s/"/""/g;
		$title  =~ s/"/""/g;

		# create a record and then update the "database"; quote marks are obtuse!
		my @record = ( qq("$gid), $author, $title, $file, $local, qq($remote") );
		push( @records, join( '","', @record ) );
		
		# copy the file to the directory
		copy( "$texts/$gid.txt", "$directory/$gid.txt" ) or die "Can't copy file to directory ($!). Call Eric.\n";
		
	}

	# build a CSV stream from the TSV; quote marks are still obtuse!
	my $csv  = '"'. join( '","', HEADER ) . '"' . "\n";
	$csv    .= join( "\n", @records );
	
	# create the metadata file
	my $metadata = "$directory/$metadata";
	open FILE, " > $metadata" or die "Can't create $metadata ($!). Call Eric.\n";
	print FILE $csv;
	close FILE;
	
	# compress the result
	my $zip = Archive::Zip->new();
	$zip->addTree( $directory, $carrel );
	$zip->writeToFileNamed( "$carrels/$carrel.zip" );
	
	# clean up
	rmtree $directory or die "Can't remove $directory ($!). Call Eric.\n";
	
}


# done
exit;


sub form {

	return <<EOF
<html>
<head>
	<title>Project Gutenberg - Identifiers to TSV</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" href="/etc/style.css">
	<style>
		.item { margin-bottom: 1em }
	</style>
</head>
<div class="header">
	<h1>Project Gutenberg - Identifiers to TSV</h1>
</div>

	<div class="col-3 col-m-3 menu">
	  <ul>
		<li><a href="/gutenberg/">Home</a></li>
		<li><a href="/gutenberg/gids2urls.cgi">Get URLs</a></li>
		<li><a href="/gutenberg/gids2tsv.cgi">IDs to TSV</a></li>
		<li><a href="/gutenberg/gids2zip.cgi">IDs to ZIP</a></li>
	 </ul>
	</div>

<div class="col-9 col-m-9">

	<p>Given a set of one or more identifiers, this program will return a tab-separated value list of search results suitable for reading with your favorite spreadsheet or database program. Use the output of this program to sort, refine, and save your search results.</p>
	<form method='POST' action='/gutenberg/gids2zip.cgi'>
	<input type='text' name='carrel' size='50' />
	<input type='hidden' name='gids' value='##GIDS##'/>
	<input type='submit' value='Get Zip' />
	</form>

	<div class="footer">
		<p style='text-align: right'>
		Eric Lease Morgan<br />
		November 26, 2020
		</p>
	</div>

</div>

</body>
</html>
EOF
	
}
