#!/data-disk/bin/perl

# search2queue.cgi - given a few inputs, add a carrel configuration to the queue

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNPU Public License

# June  2, 2020 - first investigations
# July 10, 2020 - added current date and time to provenance


# configure
use constant TODO => '/data-disk/reader-compute/reader-cord/queue/todo';
use constant TYPE => 'cord';

# require
use CGI;
use CGI::Carp qw( fatalsToBrowser );
use strict;

# initialize
my $cgi       = CGI->new;
my $html      = '';
my $shortname = $cgi->param( 'shortname' );
my $username  = $cgi->remote_user();
my $query     = $cgi->param( 'query' );
my $queue     = $cgi->param( 'queue' );

# display home page
if ( ! $shortname | ! $query ) {

	# initialize and update the HTML; simple
	$html =  &template;
	$html =~ s/##QUERY##/$query/e;

}

# do the work
elsif ( $queue ) {

	# initialize some more
	my ( $sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst ) = localtime();
	my $date = sprintf ( "%02d-%02d-%02d", $year+1900, $mon+1, $mday );
	my $time = sprintf ( "%02d:%02d", $hour, $min );
    my $todo = TODO . "/$shortname.tsv";
    
	# update the queue
	open QUEUE, " > $todo" or die "Can't open $todo ($!). Call Eric.\n";
	print QUEUE join( "\t", ( TYPE, $shortname, $date, $time, $username, $query ) ), "\n";
	close QUEUE;
	
	# initialize and update the HTML
	$html = &queue;
	$html =~ s/##SHORTNAME##/$shortname/eg;
	$html =~ s/##USERNAME##/$username/eg;

}

# done
print $cgi->header( -type => 'text/html', -charset => 'utf-8');
print $html;
exit;


sub template {

		return <<EOF
<html>
<head>
	<title>The Distant Reader - COVID-19 literature to study carrel</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" href="/etc/style.css">
	<style>
		.item { margin-bottom: 1em }
	</style>
</head>
<body>
<div class="header">
	<h1>The Distant Reader - COVID-19 literature to study carrel</h1>
</div>

<div class="col-3 col-m-3 menu">
  <ul>
		<li style='margin-bottom: 2em'><a href="/">Distant Reader home</a></li>
		
		<li ><a href="/file2carrel/">File to study carrel</a></li>
		<li><a href="/zip2carrel/">Zip to study carrel</a></li>
		<li><a href="/url2carrel/">URL to study carrel</a></li>
		<li><a href="/urls2carrel/">URLs to study carrel</a></li>
		<li><a href="/trust2carrel/">HathiTrust to study carrel</a></li>
		<li style='margin-bottom: 2em'><a href="/biorxiv2carrel/">Biorxiv to study carrel</a></li>
		
		<li><a href="/gutenberg/">Gutenberg to study carrel</a></li>
		<li><a href="/cord/">CORD-19 to study carrel</a></li>
		
 </ul>
</div>

<div class="col-9 col-m-9">

	<p>Use this form to queue the creation of a study carrel from the results of your COVID-19 literature search.</p>
	
	<form method='GET' action='/cord/search2queue.cgi'>
	<input type='hidden' name="query" value='##QUERY##' />
	<table>
		<tr>
			<td style='text-align:right'>Short name:</td>
			<td><input type='text'
			           name='shortname'
			           autofocus="autofocus"
			           onkeyup="this.value = this.value.replace( /[^a-z|^A-Z|0-9|_|\-]/, '' )" />
			</td>
		</tr>
		<tr>
			<td style='text-align:right'>Action</td>
			<td><input type='submit' name='queue' value='Queue' /></td>
		</tr>
	</table>
	
	</form>

	<div class="footer">
		<p style='text-align: right'>
		Eric Lease Morgan<br />
		December 2, 2020
		</p>
	</div>

</div>

</body>
</html>
EOF

}


sub queue {

		return <<EOF
<html>
<head>
	<title>The Distant Reader - COVID-19 literature to study carrel</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" href="/etc/style.css">
	<style>
		.item { margin-bottom: 1em }
	</style>
</head>
<body>
<div class="header">
	<h1>The Distant Reader - COVID-19 literature to study carrel</h1>
</div>

<div class="col-3 col-m-3 menu">
  <ul>
		<li style='margin-bottom: 2em'><a href="/">Distant Reader home</a></li>
		
		<li ><a href="/file2carrel/">File to study carrel</a></li>
		<li><a href="/zip2carrel/">Zip to study carrel</a></li>
		<li><a href="/url2carrel/">URL to study carrel</a></li>
		<li><a href="/urls2carrel/">URLs to study carrel</a></li>
		<li><a href="/trust2carrel/">HathiTrust to study carrel</a></li>
		<li style='margin-bottom: 2em'><a href="/biorxiv2carrel/">Biorxiv to study carrel</a></li>
		
		<li><a href="/gutenberg/">Gutenberg to study carrel</a></li>
		<li><a href="/cord/">CORD-19 to study carrel</a></li>
		
 </ul>
</div>

<div class="col-9 col-m-9">

	<p><strong>##USERNAME##</strong>, your carrel has been queued for creation. Thank you for your submission!</p>
	
	<div class="footer">
		<p style='text-align: right'>
		Eric Lease Morgan<br />
		December 2, 2020
		</p>
	</div>

</div>

</body>
</html>
EOF

}

