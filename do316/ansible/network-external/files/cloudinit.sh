#!/bin/bash
useradd -G wheel developer
echo developer | passwd --stdin developer
restorecon /var/www/html/*
