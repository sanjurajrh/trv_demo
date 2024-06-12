#!/bin/bash

DEV=/dev/vdc

if [ ! -b "${DEV}" ]
then
    echo "${DEV} does not exist or is not a block device." >&2
    exit 1
fi

mount "${DEV}" /var/www/html
chmod -R a+rX /var/www/html
chcon -R -t httpd_sys_content_t /var/www/html

UUID=$(lsblk -o UUID --nodeps --noheadings --raw "${DEV}")
echo "UUID=${UUID} /var/www/html ext4 defaults 0 2" >> /etc/fstab

echo "Mount successful"
