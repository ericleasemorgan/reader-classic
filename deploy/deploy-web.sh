#!/bin/bash

# Deploy the web components on the production server
#
# This script assumes it is being run as root.


# Copy apache configs
#APACHE_CONFIG_FILES=config/httpd.conf \
#    config/httpd-le-ssl.conf
#for f in $APACHE_CONFIG_FILES; do
#    install -m 666 $f "/etc/httpd/conf/$(basename $f)"
#done

# Copy python service files
# /sv/reader
# /opt/reader/env
# /opt/reader/config.production

# install the cron jobs
install --compare --owner=root --group=root --mode=644 \
  config/cron.d/distant-reader \
  /etc/cron.d/distant-reader

# copy all the static files and cgi scripts
#rsync --checksum --recursive www /data-disk/www/html

# copy the python components
rsync --checksum --recursive webui/ /opt/reader
cp lib/scan_carrels.sh /opt/reader
chown -R app:app /opt/reader
# this needs to run as the app user
cd /opt/reader && sudo -u app env \
    PIPENV_CACHE_DIR=/opt/reader/pip_cache \
    WORKON_HOME=/opt/reader/pip_cache \
    /usr/local/bin/pipenv install --deploy
cd /opt/reader && sudo -u app env \
    PIPENV_CACHE_DIR=/opt/reader/pip_cache \
    WORKON_HOME=/opt/reader/pip_cache \
    /usr/local/bin/pipenv run yoyo apply -b -d sqlite:////data-disk/etc/reader-patrons.db

sv restart reader
systemctl reload httpd
