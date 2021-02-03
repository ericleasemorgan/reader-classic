#!/data-disk/bin/perl

# gid2urls.cgi - given one more more identifiers, generate a list of urls pointing to plain text files

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNU Public License

# July 12, 2018 - first cut, but based on other work
# May   3, 2019 - migrating to Project Gutenberg


# configure
use constant QUERY    => qq(SELECT file FROM files WHERE file LIKE "%.txt.utf-8" AND (##CLAUSE##) ORDER BY gid;);
use constant DATABASE => '/data-disk/reader-compute/reader-gutenberg/etc/gutenberg.db';
use constant DRIVER   => 'SQLite';
use constant ROOT     => 'http://distantreader.org/gutenberg/texts';

# require
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use DBI;
use strict;

# initialize
my $cgi = CGI->new;
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

	# create the sql where clause and then build the whole sql query
	my @queries =  ();
	for my $gid ( @gids ) { push( @queries, "gid='$gid'" ) }
	my $sql     =  QUERY;
	$sql        =~ s/##CLAUSE##/join( ' OR ', @queries )/e;

	# debug
	print STDERR "$sql\n\n";

	# execute the query
	my $driver    = DRIVER; 
	my $database  = DATABASE;
	my $dbh       = DBI->connect( "DBI:$driver:dbname=$database", '', '', { RaiseError => 1 } ) or die $DBI::errstr;
	my $handle = $dbh->prepare( $sql );
	$handle->execute() or die $DBI::errstr;

	# process each item in the found set
	my @urls = ();
	foreach my $gid ( sort @gids ) {
	
		# parse the title data
		push( @urls, "$root/$gid.txt" );
			
	}

	# dump the database and done
	print $cgi->header( -type => 'text/plain', -charset => 'utf-8');
	print join( "\n", @urls ), "\n";
	
}


# done
exit;


sub form {

	return <<EOF
<html>
<head>
	<title>Project Gutenberg - Get URLs</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" href="/etc/style.css">
	<style>
		.item { margin-bottom: 1em }
	</style>
</head>
<div class="header">
	<h1>Project Gutenberg - Get URLs</h1>
</div>

	<div class="col-3 col-m-3 menu">
	  <ul>
		<li><a href="/gutenberg/">Home</a></li>
		<li><a href="/gutenberg/gids2urls.cgi">Get URLs</a></li>
	 </ul>
	</div>

<div class="col-9 col-m-9">

	<p>Given a set of one or more identifiers, this program will return a list of URLs pointing to plain text versions of the items.</p>
	<form method='POST' action='/gutenberg/gids2urls.cgi'>
	<input type='text' name='gids' size='50' value='21711 36000 13500'/>
	<input type='submit' value='Get URLs' />
	</form>

	<div class="footer">
		<p style='text-align: right'>
		Eric Lease Morgan<br />
		May 3, 2019
		</p>
	</div>

</div>

</body>
</html>
EOF
	
}


