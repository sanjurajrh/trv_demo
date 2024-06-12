#!/bin/bash
useradd -G wheel developer
echo developer | passwd --stdin developer

DEV=/dev/vdc

mkfs.xfs "${DEV}"
mount "${DEV}" /var/www/html

cp /usr/share/httpd/icons/apache_pb2.png /var/www/html

cat <<EOF > /var/www/html/index.html
<!doctype html>
<html lang="en">
<head>
  <title>Test page</title>
</head>
<body>
  <h1>Test Page</h1>
   <img src="apache_pb2.png" alt="Powered by Apache">
</body>
</html>
EOF

chmod -R a+rX /var/www/html
chcon -R -t httpd_sys_content_t /var/www/html

UUID=$(lsblk -o UUID --nodeps --noheadings --raw "${DEV}")
echo "UUID=${UUID} /var/www/html xfs defaults 0 2" >> /etc/fstab
