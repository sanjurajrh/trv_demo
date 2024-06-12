#!/bin/bash

VM_NAME=web1
TMPFILE=$(mktemp --suffix .img)

dd if=/dev/zero of="${TMPFILE}" bs=1M count=50
mkfs.ext4 -F "${TMPFILE}"
mount "${TMPFILE}" /mnt

cat <<EOF > /mnt/index.html
<!doctype html>
<html lang="en">
<head>
  <title>Test page ${VM_NAME}</title>
</head>

<body>
  <h1>Test Page ${VM_NAME}</h1>
   Welcome to ${VM_NAME}.
</body>
</html>
EOF

chmod -R a+rX /mnt
chcon -R -t httpd_sys_content_t /mnt
umount /mnt
qemu-img convert -f raw -O qcow2 "${TMPFILE}" "${VM_NAME}".qcow2
rm -f "${TMPFILE}"
echo "============================> ${VM_NAME}.qcow2"
