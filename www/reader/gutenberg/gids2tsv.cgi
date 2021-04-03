#!/data-disk/bin/perl

# id2tsv.cgi - given one more more identifiers, generate a TSV file of metatdata

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# March 9, 2017 - first cut; I'm doing great!
# April 9, 2018 - migrating to Project English
# May   9, 2019 - migrating to Project Gutenberg


# configure
use constant DATABASE => '/data-disk/reader-compute/reader-gutenberg/etc/gutenberg.db';
use constant DRIVER   => 'SQLite';
use constant HEADER   => ( 'gid', 'author', 'title', 'remote url', 'local url' );
#use constant QUERY    => qq(SELECT t.*, f.file FROM titles AS t, files AS f WHERE t.language IS 'en' AND f.file LIKE '%.txt.utf-8' AND t.gid = f.gid ORDER BY gid;);

use constant QUERY    => qq(SELECT t.*, f.file FROM titles as t, files as f WHERE (##CLAUSE##) AND t.language IS 'en' AND f.file LIKE '%.txt.utf-8' AND t.gid = f.gid ORDER BY t.gid;);
use constant ROOT     => 'http://distantreader.org/gutenberg/texts';

# require
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use DBI;
use strict;

# initialize
my $cgi  = CGI->new;
my $gids = $cgi->param( 'gids' );

# no input; display home page
if ( ! $gids ) {

	print $cgi->header;
	print &form;
	
}

# process input
else {

	# get input and sanitize it
	my @gids =  ();
	$gids    =~ s/[[:punct:]]/ /g;
	$gids    =~ s/ +/ /g;
	@gids    =  split( ' ', $gids );

	# initialize
	my $root = ROOT;

	# VALIDATE INPUT HERE; we don't need to leave an opportunity for sql injection!

	# debug
	#print STDERR join( '; ', @ids ), "\n\n";

	# create the sql where clause and then build the whole sql query
	my @queries =  ();
	for my $gid ( @gids ) { push( @queries, "t.gid='$gid'" ) }
	my $sql     =  QUERY;
	$sql        =~ s/##CLAUSE##/join( ' OR ', @queries )/e;

	warn "$sql\n";
	
	# execute the query
	my $driver    = DRIVER; 
	my $database  = DATABASE;
	my $dbh       = DBI->connect( "DBI:$driver:dbname=$database", '', '', { RaiseError => 1 } ) or die $DBI::errstr;
	my $handle = $dbh->prepare( $sql );
	$handle->execute() or die $DBI::errstr;

	# process each title in the found set
	my @records = ();
	while( my $titles = $handle->fetchrow_hashref ) {
	
		# parse the title data
		my $author = $$titles{ 'author' };
		my $file   = $$titles{ 'file' };
		my $gid    = $$titles{ 'gid' };
		my $title  = $$titles{ 'title' };
		
		# build the url
		my $url = "$root/$gid.txt";

		# create a record and then update the "database"
		my @record = ( $gid, $author, $title, $file, $url );
		push( @records, join( "\t", @record ) );
	
	}

	# dump the database and done
	print $cgi->header( -type => 'text/tab-separated-values', -charset => 'utf-8');
	print join( "\t", HEADER ),   "\n";
	print join( "\n", @records ), "\n";
	
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
	 </ul>
	</div>

<div class="col-9 col-m-9">

	<p>Given a set of one or more identifiers, this program will return a tab-separated value list of search results suitable for reading with your favorite spreadsheet or database program. Use the output of this program to sort, refine, and save your search results.</p>
	<form method='POST' action='/gutenberg/gids2tsv.cgi'>
	<input type='text' name='gids' size='50' value='21711 36000 13500'/>
	<input type='submit' value='Get TSV' />
	</form>

	<div class="footer">
		<p style='text-align: right'>
		Eric Lease Morgan<br />
		May 9, 2019
		</p>
	</div>

</div>

</body>
</html>
EOF
	
}
