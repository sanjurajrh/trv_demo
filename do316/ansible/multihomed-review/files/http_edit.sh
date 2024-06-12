#!/bin/bash
cp /home/lab/.htaccess /var/www/html/
echo "Hello, World! " | sudo tee -a /var/www/html/index.html
sed -i '/<Directory "\/var\/www\/html">/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/httpd/conf/httpd.conf
rm -f /etc/httpd/conf.d/welcome.conf
systemctl enable --now httpd
