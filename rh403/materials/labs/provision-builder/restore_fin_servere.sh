#!/bin/bash

orgname="Finance"
home="/home/student"
key="id_rsa_foreman_proxy"
foreman_key="$home/$key"
nic="'System ens3'"

if ! [[ $(ping -c1 servere > /dev/null 2> /dev/null) ]]
then
  scp root@capsule:/usr/share/foreman-proxy/.ssh/$key $home > /dev/null 2> /dev/null
  IP=$(ssh root@satellite hammer --no-headers  host list --organization $orgname --fields Name,ip | grep servere | awk '{ print $3 }')
  ssh -i $foreman_key root@"$IP" "nmcli connection modify $nic ipv4.addresses 172.25.250.14/24"
  ssh -i $foreman_key root@"$IP" "nmcli connection up $nic"
  rm -rf $foreman_key
fi