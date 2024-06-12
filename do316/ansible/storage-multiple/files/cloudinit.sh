#!/bin/bash
useradd -G wheel developer
echo developer | passwd --stdin developer
wget -O /root/dbmove.sh http://utility.lab.example.com:8080/dbmove.sh
chmod 700 /root/dbmove.sh
systemctl stop mariadb
mkfs.xfs /dev/vdc
mount /dev/vdc /mnt
chown mysql:mysql /mnt
cp -a /var/lib/mysql/* /mnt
umount /mnt
systemctl start mariadb
