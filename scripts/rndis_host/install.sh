#!/bin/bash

if [[ $EUID -ne 0 ]]; then
	echo "This script must be run as root (use sudo)" 1>&2
	exit 1
fi

cp rndis-host /usr/bin/
cp rndis-host.service /etc/systemd/system/
systemctl enable rndis-host.service
systemctl start  rndis-host

exit 0

