#!/bin/bash

TMPFILE=$(mktemp --suffix .img)

dd if=/dev/zero of="${TMPFILE}" bs=1M count=50
mkfs.ext4 -F "${TMPFILE}"
mount "${TMPFILE}" /mnt
cp /usr/share/icons/Adwaita/512x512/apps/utilities-terminal.png /mnt

cat <<EOF > /mnt/index.html
<!doctype html>
<html lang="en">
<head>
  <title>Test page</title>
</head>

<body>
  <h1>Test Page</h1>
   <img src="utilities-terminal.png" alt="System terminal">
</body>
</html>
EOF

chmod -R a+rX /mnt
chcon -R -t httpd_sys_content_t /mnt
umount /mnt
qemu-img convert -f raw -O qcow2 "${TMPFILE}" data.qcow2
rm -f "${TMPFILE}"
echo "============================> data.qcow2"
