#!/data-disk/bin/perl -w

# urls2queue.cgi - given a few inputs, add a carrel configuration to the queue

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNPU Public License

# November 29, 2020 - my very own Arivata; on Thanksgiving vacation in Lancaster during a pandemic


# configure
use constant BACKLOG => '/data-disk/reader-compute/reader-classic/queue/backlog';
use constant TODO    => '/data-disk/reader-compute/reader-classic/queue/todo';
use constant TYPE    => 'zip2carrel';
use constant POSTMAX => 1024 * 5000;

# require
use CGI;
use CGI::Carp qw( fatalsToBrowser );
use File::Basename;
use File::Copy;
use strict;

# initialize
$CGI::POST_MAX = POSTMAX;
my $cgi        = CGI->new;
my $html       = '';
my $shortname  = $cgi->param(  'shortname' );
my $email      = $cgi->param(  'email' );
my $queue      = $cgi->param(  'queue' );
my $handle     = $cgi->upload( 'zip' );

# display home page
if ( ! $shortname | ! $email | ! $handle ) {

	# initialize and update the HTML; simple
	$html =  &template;

}

# do the work
elsif ( $queue ) {

	# get the basename of the loaded file, and move it to the backlog
	my $file = $cgi->tmpFileName( $handle );
	my ( $name, $path, $extension ) = fileparse( $file, qr/\.[^.]*/ );
	move( $file, BACKLOG . "/$name.zip" ) or die "Can't move $file ($!). Call Eric.";

	# initialize the to-do record
	my ( $sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst ) = localtime();
	my $date = sprintf ( "%02d-%02d-%02d", $year+1900, $mon+1, $mday );
	my $time = sprintf ( "%02d:%02d", $hour, $min );
    my $todo = TODO . "/$shortname.tsv";
    
	# update the queue
	open QUEUE, " > $todo" or die "Can't open $todo ($!). Call Eric.\n";
	print QUEUE join( "\t", ( TYPE, $shortname, $date, $time, $email, "$name.zip" ) ), "\n";
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
	<title>The Distant Reader - Zip file to study carrel</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" href="/etc/style.css">
	<style>
		.item { margin-bottom: 1em }
	</style>
</head>
<body>
<div class="header">
	<h1>The Distant Reader - Zip file to study carrel</h1>
</div>

<div class="col-3 col-m-3 menu">
  <ul>
		<li style='margin-bottom: 2em'><a href="/">Distant Reader home</a></li>
		
		<li><a href="/file2carrel/">File to study carrel</a></li>
		<li>Zip to study carrel</li>
		<li><a href="/url2carrel/">URL to study carrel</a></li>
		<li><a href="/urls2carrel/">URLs to study carrel</a></li>
		<li><a href="/trust2carrel/">HathiTrust to study carrel</a></li>
		<li style='margin-bottom: 2em'><a href="/biorxiv2carrel/">Biorxiv to study carrel</a></li>
		
		<li><a href="/gutenberg/">Gutenberg to study carrel</a></li>
		<li><a href="/cord/">COVID-19 to study carrel</a></li>
		
 </ul>
</div>

<div class="col-9 col-m-9">

	<p>Use this form to queue a zip file containing any number of other files (plus an optional file named "metadata.csv") to be processed by the Distant Reader.</p>
	
	<form action="./" method="post" enctype="multipart/form-data">
	<table>
		<tr>
			<td style='text-align:right'>One-word name describing your carrel:</td>
			<td><input type='text'
			           name='shortname'
			           size='50'
			           autofocus="autofocus"
			           onkeyup="this.value = this.value.replace( /[^a-z|^A-Z|0-9|_|\-]/, '' )" />
			</td>
		</tr>
		<tr>
			<td style='text-align:right'>Your email address:</td>
			<td><input type='text' name='email' size='50' /></td>
		</tr>
		<tr>
			<td style='text-align:right'>A zip file:</td>
			<td><input type="file" name="zip" accept=".zip" /></td>
		</tr>
			<td style='text-align:right'>Action</td>
			<td><input type='submit' name='queue' value='Queue the file' /></td>
		<tr>
	</table>
	
	</form>

	<div class="footer">
		<p style='text-align: right'>
		Eric Lease Morgan<br />
		November 29, 2020
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
	<title>Zip file to study carrel</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" href="/etc/style.css">
	<style>
		.item { margin-bottom: 1em }
	</style>
</head>
<body>
<div class="header">
	<h1>Zip file to study carrel</h1>
</div>

<div class="col-3 col-m-3 menu">
  <ul>
		<li><a href="./">Home</a></li>
 </ul>
</div>

<div class="col-9 col-m-9">

	<p>Your carrel <strong>##SHORTNAME##</strong> has been queued for creation. Thank you for your submission!</p>
	
	<div class="footer">
		<p style='text-align: right'>
		Eric Lease Morgan<br />
		November 29, 2020
		</p>
	</div>

</div>

</body>
</html>
EOF

}

