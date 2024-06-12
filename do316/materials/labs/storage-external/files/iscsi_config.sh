#!/bin/bash
sshpass -p redhat ssh -J lab@utility root@server.srv <<'EOL';

cat <<EOF > ./scsi.sh
FILE=/etc/lvm/lvm.conf

sed 's/#use_devicesfile=1/use_devicesfile=1/' ${FILE}

vgimportdevices -ay

lvchange -ay /dev/vg_iscsi/lv_disk1
lvchange -ay /dev/vg_iscsi/lv_disk2

echo "/backstores/block create name=server.disk1 dev=/dev/vg_iscsi/lv_disk1" | targetcli

echo "/backstores/block create name=server.disk2 dev=/dev/vg_iscsi/lv_disk2" | targetcli

echo "/iscsi/iqn.2021-10.com.example:server.disk1/tpg1/luns create /backstores/block/server.disk1" | targetcli

echo "/iscsi/iqn.2021-10.com.example:server.disk2/tpg1/luns create /backstores/block/server.disk2" | targetcli
EOF

chmod +x ./scsi.sh
sh ./scsi.sh
EOL
