#!/bin/bash

# Deploy the web components on the production server
#
# This script assumes it is being run as root. This might need to be adjusted.


# Copy apache configs
APACHE_CONFIG_FILES=config/httpd.conf \
    config/httpd-le-ssl.conf
for f in $APACHE_CONFIG_FILES; do
    install -m 666 $f /etc/httpd/conf/
done

# copy all the static files and cgi scripts
rsync --checksum --recursive www /data-disk/www/html

# copy the python components
sudo -u app rsync --checksum --recursive webui /opt/reader
sudo -u app env \
    PIPENV_CACHE_DIR=/opt/reader/pip_cache \
    WORKON_HOME=/opt/reader/pip_cache \
    /usr/local/bin/pipenv install --deploy
sv restart reader
