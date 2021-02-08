#!/bin/bash

# Deploy the web components on the production server
#
# This script assumes it is being run as root. This might need to be adjusted.


# Copy apache configs
for f in config/httpd.conf config/httpd-le-ssl.conf; do
    install -m 666 $f /etc/httpd/conf/
done

# copy all the static files and cgi scripts
rsync --checksum --recursive www /data-disk/www/html

