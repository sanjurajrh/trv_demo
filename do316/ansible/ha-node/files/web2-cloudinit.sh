#!/bin/bash
useradd -G wheel developer
echo developer | passwd --stdin developer

echo "Welcome to web2" > /var/www/html/index.html
chmod 755 /var/www/html
chmod 644 /var/www/html/index.html

restorecon -R /var/www/html
