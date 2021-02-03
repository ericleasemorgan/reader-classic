#!/data-disk/bin/perl

# search2queue.cgi - given a few inputs, add a carrel configuration to the queue

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNPU Public License

# June      2, 2020 - first investigations
# July     10, 2020 - added current date and time to provenance
# November 28, 2020 - my very own Arivata; on Thanksgiving vacation in Lancaster during a pandemic


# configure
use constant TODO => '/data-disk/reader-compute/reader-classic/queue/todo';
use constant TYPE => 'url2carrel';

# require
use CGI;
use CGI::Carp qw( fatalsToBrowser );
use strict;

# initialize
my $cgi       = CGI->new;
my $html      = '';
my $shortname = $cgi->param( 'shortname' );
my $email     = $cgi->param( 'email' );
my $url       = $cgi->param( 'url' );
my $confirm   = $cgi->param( 'confirm' );
my $queue     = $cgi->param( 'queue' );

# display home page
if ( ! $shortname | ! $email | ! $url ) {

	# initialize and update the HTML; simple
	$html =  &template;
	$html =~ s/##URL##/$url/e;

}

# confirm input
elsif ( $confirm ) {

	# initialize and update the HTML; simple
	$html = &confirm;
	$html =~ s/##SHORTNAME##/$shortname/eg;
	$html =~ s/##EMAIL##/$email/eg;
	$html =~ s/##URL##/$url/eg;

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
	print QUEUE join( "\t", ( TYPE, $shortname, $date, $time, $email, $url ) ), "\n";
	close QUEUE;
	
	# initialize and update the HTML
	$html = &queue;
	$html =~ s/##SHORTNAME##/$shortname/eg;

}

# done
print $cgi->header( -type => 'text/html', -charset => 'utf-8');
print $html;
exit;


sub template {

		return <<EOF
<html>
<head>
	<title>The Distant Reader - URL to study carrel</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" href="/etc/style.css">
	<style>
		.item { margin-bottom: 1em }
	</style>
</head>
<body>
<div class="header">
	<h1>The Distant Reader - URL to study carrel</h1>
</div>

<div class="col-3 col-m-3 menu">
  <ul>
		<li style='margin-bottom: 2em'><a href="/">Distant Reader home</a></li>
		
		<li><a href="/file2carrel/">File to study carrel</a></li>
		<li><a href="/zip2carrel/">Zip to study carrel</a></li>
		<li>URL to study carrel</li>
		<li><a href="/urls2carrel/">URLs to study carrel</a></li>
		<li><a href="/trust2carrel/">HathiTrust to study carrel</a></li>
		<li style='margin-bottom: 2em'><a href="/biorxiv2carrel/">Biorxiv to study carrel</a></li>
		
		<li><a href="/gutenberg/">Gutenberg to study carrel</a></li>
		<li><a href="/cord/">COVID-19 to study carrel</a></li>
		
 </ul>
</div>

<div class="col-9 col-m-9">

	<p>Use this form to queue the creation of a study carrel with the results of a Solr query.</p>
	
	<form method='GET' action='./'>
	<table>
		<tr>
			<td style='text-align:right'>Short name:</td>
			<td><input type='text' name='shortname' autofocus="autofocus" /></tdb>
		</tr>
		<tr>
			<td style='text-align:right'>Email address:</td>
			<td><input type='text' name='email' /></td>
		</tr>
		<tr>
			<td style='text-align:right'>URL:</td>
			<td><input name="url" /></td>
		</tr>
			<td style='text-align:right'>Action</td>
			<td><input type='submit' name='confirm' value='Configure (Step #1 of 2)' /></td>
		<tr>
	</table>
	
	</form>

	<div class="footer">
		<p style='text-align: right'>
		Eric Lease Morgan<br />
		November 28, 2020
		</p>
	</div>

</div>

</body>
</html>
EOF

}


sub confirm {

		return <<EOF
<html>
<head>
	<title>URL to study carrel</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" href="/etc/style.css">
	<style>
		.item { margin-bottom: 1em }
	</style>
</head>
<body>
<div class="header">
	<h1>URL to study carrel</h1>
</div>

<div class="col-3 col-m-3 menu">
  <ul>
		<li><a href="./">Home</a></li>
 </ul>
</div>

<div class="col-9 col-m-9">

	<p>Below is a confirmation of the work.</p>
	
	<table>
		<tr>
			<td style='text-align:right'><strong>Short name</strong>:</td>
			<td>##SHORTNAME##</tdb>
		</tr>
		<tr>
			<td style='text-align:right'><strong>Email address</strong>:</td>
			<td>##EMAIL##</td>
		</tr>
		<tr>
			<td style='text-align:right'><strong>URL</strong>:</td>
			<td>##URL##</td>
		</tr>
	</table>

	<p>If this is correct, then queue it, and your carrel will be initialized momentarily. If not, then please go back.</p>

	<form method='GET' action='./'>
	<input type='hidden' name='shortname' value='##SHORTNAME##' />
	<input type='hidden' name='email' value='##EMAIL##' />
	<input type='hidden' name='url' value='##URL##' />
	<table>
		</tr>
			<td style='text-align:right'>Action</td>
			<td><input type='submit' name='queue' value='Queue (Step #2 of 2)' /></td>
		<tr>
	</table>
	</form>
	
	
	<div class="footer">
		<p style='text-align: right'>
		Eric Lease Morgan<br />
		November 28, 2020
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
	<title>URL to study carrel</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" href="/etc/style.css">
	<style>
		.item { margin-bottom: 1em }
	</style>
</head>
<body>
<div class="header">
	<h1>search2queue</h1>
</div>

<div class="col-3 col-m-3 menu">
  <ul>
		<li><a href="./">Home</a></li>
 </ul>
</div>

<div class="col-9 col-m-9">

	<p>Your carrel has been queued for creation.</p>

	<p>Our system looks for items in the queue every 60 seconds or so. When it sees that there is more work to do, it will initialize the carrel and submit it for creation. Once submitted, it takes another 120 seconds or so for a newly created computer to spin up. When that is done you ought to be able to use your Web browser to monitor and then use the carrel.</p>
	<p>Please wait between 60 and 180 seconds or so, and then see: <a href='http://gutenberg.distantreader.org/carrels/##SHORTNAME##/'>http://gutenberg.distantreader.org/carrels/##SHORTNAME##/</a>. You can go there right now, but you will probably get an error message.</p>

	<p>Thank you for your submission!</p>
	
	<div class="footer">
		<p style='text-align: right'>
		Eric Lease Morgan<br />
		November 28, 2020
		</p>
	</div>

</div>

</body>
</html>
EOF

}

