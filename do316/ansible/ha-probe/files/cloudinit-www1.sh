#!/bin/bash
echo "Welcome to www1" > /var/www/html/index.html
chmod 644 /var/www/html/index.html

# Fake status endpoint
mkdir /var/www/html/health
echo "OK" > /var/www/html/health/index.html
chmod 755 /var/www/html/health
chmod 644 /var/www/html/health/index.html

restorecon -R /var/www/html
