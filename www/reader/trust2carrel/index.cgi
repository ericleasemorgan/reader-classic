#!/data-disk/bin/perl -w

# trust2queue.cgi - given a few inputs, add a carrel configuration to the queue

# Eric Lease Morgan <emorgan@nd.edu>
# (c) University of Notre Dame; distributed under a GNPU Public License

# November 29, 2020 - my very own Arivata; on Thanksgiving vacation in Lancaster during a pandemic


# configure
use constant BACKLOG => '/data-disk/reader-compute/reader-trust/queue/backlog';
use constant TODO    => '/data-disk/reader-compute/reader-trust/queue/todo';
use constant TYPE    => 'trust';
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
my $username   = $cgi->remote_user();
my $queue      = $cgi->param(  'queue' );
my $handle     = $cgi->upload( 'tsv' );

# display home page
if ( ! $shortname | ! $handle ) {

	# initialize and update the HTML; simple
	$html =  &template;

}

# do the work
elsif ( $queue ) {

	# get the basename of the loaded file, and move it to the backlog
	my $file = $cgi->tmpFileName( $handle );
	my ( $name, $path, $extension ) = fileparse( $file, qr/\.[^.]*/ );
	move( $file, BACKLOG . "/$name.tsv" ) or die "Can't move $file ($!). Call Eric.";

	# initialize the to-do record
	my ( $sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst ) = localtime();
	my $date = sprintf ( "%02d-%02d-%02d", $year+1900, $mon+1, $mday );
	my $time = sprintf ( "%02d:%02d", $hour, $min );
    my $todo = TODO . "/$shortname.tsv";
    
	# update the queue
	open QUEUE, " > $todo" or die "Can't open $todo ($!). Call Eric.\n";
	print QUEUE join( "\t", ( TYPE, $shortname, $date, $time, $username, "$name.tsv" ) ), "\n";
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
	<title>The Distant Reader - HathiTrust metadata file to study carrel</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" href="/etc/style.css">
	<style>
		.item { margin-bottom: 1em }
	</style>
</head>
<body>
<div class="header">
	<h1>The Distant Reader - HathiTrust metadata file to study carrel</h1>
</div>

<div class="col-3 col-m-3 menu">
  <ul>
		<li style='margin-bottom: 2em'><a href="/">Distant Reader home</a></li>
		
		<li ><a href="/file2carrel/">File to study carrel</a></li>
		<li><a href="/zip2carrel/">Zip to study carrel</a></li>
		<li><a href="/url2carrel/">URL to study carrel</a></li>
		<li><a href="/urls2carrel/">URLs to study carrel</a></li>
		<li>HathiTrust to study carrel</li>
		<li style='margin-bottom: 2em'><a href="/biorxiv2carrel/">Biorxiv to study carrel</a></li>
		
		<li><a href="/gutenberg/">Gutenberg to study carrel</a></li>
		<li><a href="/cord/">CORD-19 to study carrel</a></li>
		
 </ul>
</div>

<div class="col-9 col-m-9">

	<p>Use this form to queue a HathiTrust metadata (.tsv) file to be processed by the Distant Reader.</p>
	
	<form action="./" method="post" enctype="multipart/form-data">
	<table>
		<tr>
			<td style='text-align:right'>One-word name describing your carrel:</td>
			<td><input type='text'
			           name='shortname'
			           autofocus="autofocus"
			           onkeyup="this.value = this.value.replace( /[^a-z|^A-Z|0-9|_|\-]/, '' )" />
			</td>
		</tr>
		<tr>
			<td style='text-align:right'>HathiTrust metadata file:</td>
			<td><input type="file" name="tsv" accept=".tsv" /></td>
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
	<title>The Distant Reader - HathiTrust metadata file to study carrel</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" href="/etc/style.css">
	<style>
		.item { margin-bottom: 1em }
	</style>
</head>
<body>
<div class="header">
	<h1>The Distant Reader - HathiTrust metadata file to study carrel</h1>
</div>

<div class="col-3 col-m-3 menu">
  <ul>
		<li style='margin-bottom: 2em'><a href="/">Distant Reader home</a></li>
		
		<li ><a href="/file2carrel/">File to study carrel</a></li>
		<li><a href="/zip2carrel/">Zip to study carrel</a></li>
		<li><a href="/url2carrel/">URL to study carrel</a></li>
		<li><a href="/urls2carrel/">URLs to study carrel</a></li>
		<li>HathiTrust to study carrel</li>
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
		November 29, 2020
		</p>
	</div>

</div>

</body>
</html>
EOF

}

