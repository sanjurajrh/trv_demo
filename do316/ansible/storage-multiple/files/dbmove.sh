#!/bin/bash

ROOT_DB_DIR="/mariadb"

# Pre-flight tests
ERROR=0
if [ -d "${ROOT_DB_DIR}" ]
then
    echo "The ${ROOT_DB_DIR} already exists." >&2
    ERROR=1
fi

if [ -f /etc/my.cnf.d/mariadb-server-do316.cnf ]
then
    echo "The updated MariaDB Server configuration file already exists." >&2
    ERROR=1
fi

for DEV in /dev/vdd /dev/vde /dev/vdf
do
    if [ ! -b "${DEV}" ]
    then
        echo "The ${DEV} block device does not exist." >&2
        ERROR=1
        continue
    fi

    SIZE=$(lsblk -o SIZE,MOUNTPOINT,FSTYPE --nodeps --noheadings --raw --bytes "${DEV}")
    NUM_ITEMS=$(echo "${SIZE}" | wc -w)
    if [ ${NUM_ITEMS} -ne 1 ]
    then
        echo "The ${DEV} block device is already used." >&2
        ERROR=1
        continue
    fi

    if [ ${SIZE} -lt 104857600 ]
    then
        echo "The ${DEV} block device is too small." >&2
        ERROR=1
    fi
done

if [ "${ERROR}" -ne 0 ]
then
    exit 1
fi


echo
echo
echo "#### Formating the devices"
for DEV in /dev/vdd /dev/vde /dev/vdf
do
    mkfs.xfs "${DEV}"
done


echo
echo
echo "#### Stoping the MariaDB Server"
systemctl stop mariadb.service

echo
echo
echo "#### Backing up MariaDB Server data directory"
if [ ! -d /var/lib/mysql.SAVE ]
then
    cp -a /var/lib/mysql /var/lib/mysql.SAVE
fi
if [ ! -f /etc/fstab.SAVE ]
then
    cp -a /etc/fstab /etc/fstab.SAVE
fi


echo
echo
echo "#### Preparing the MariaDB Server directories"
semanage fcontext -a -t mysqld_db_t '/mariadb(/.*)?'
mkdir -p "${ROOT_DB_DIR}/data" "${ROOT_DB_DIR}/redo" "${ROOT_DB_DIR}/undo"
if [ $? -ne 0 ]
then
    rm -rf "${ROOT_DB_DIR}" &> /dev/null
    exit 2
fi


echo
echo
echo "#### Mounting the filesystems"
for DEV_mount in /dev/vdd:data /dev/vde:redo /dev/vdf:undo
do
    DEV=$(echo ${DEV_mount} | cut -d: -f1)
    PT=$(echo ${DEV_mount} | cut -d: -f2)
    UUID=$(lsblk -o UUID --nodeps --noheadings --raw "${DEV}")
    echo "UUID=${UUID} ${ROOT_DB_DIR}/${PT} xfs defaults 0 2" >> /etc/fstab
done
mount /dev/vdd "${ROOT_DB_DIR}/data" && \
mount /dev/vde "${ROOT_DB_DIR}/redo" && \
mount /dev/vdf "${ROOT_DB_DIR}/undo"
if [ $? -ne 0 ]
then
    mv /etc/fstab.SAVE /etc/fstab
    exit 2
fi
chown -R mysql:mysql "${ROOT_DB_DIR}"
chmod -R 755 "${ROOT_DB_DIR}"
restorecon -R "${ROOT_DB_DIR}"


echo
echo
echo "#### Moving database files"
mv /var/lib/mysql/ibdata1 /var/lib/mysql/sakila "${ROOT_DB_DIR}/data" && \
mv /var/lib/mysql/ib_logfile* "${ROOT_DB_DIR}/redo" &&
ln -s "${ROOT_DB_DIR}/data/sakila" /var/lib/mysql
if [ $? -ne 0 ]
then
    mv /etc/fstab.SAVE /etc/fstab
    umount /dev/vdd
    umount /dev/vde
    umount /dev/vdf
    wipefs -a -f /dev/vdd
    wipefs -a -f /dev/vde
    wipefs -a -f /dev/vdf
    if [ ! -d /var/lib/mysql.SAVE ]
    then
        rm -rf /var/lib/mysql
        mv /var/lib/mysql.SAVE /var/lib/mysql
    fi
    exit 2
fi

echo
echo
echo "#### Updating the MariaDB Server configuration"
cat <<EEEE > /etc/my.cnf.d/mariadb-server-do316.cnf
[mysqld]
innodb_data_home_dir = ${ROOT_DB_DIR}/data/
innodb_log_group_home_dir = ${ROOT_DB_DIR}/redo
innodb_undo_directory = ${ROOT_DB_DIR}/undo
EEEE


echo
echo
echo "#### Starting the MariaDB Server"
systemctl start mariadb.service
echo Done
