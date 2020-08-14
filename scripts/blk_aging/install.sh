#!/bin/bash

if [[ $EUID -ne 0 ]]; then
	echo "This script must be run as root (use sudo)" 1>&2
	exit 1
fi

install --mode 0755 blockdev_aging /usr/local/bin/
[ -f blockdev_aging.local ] || {
	echo "Prepare a blockdev_aging.local script" 1>&2
	exit 2
}
cp blockdev_aging.local /usr/local/bin/
cp blockdev-aging.service /etc/systemd/system/
systemctl unmask blockdev-aging.service
systemctl enable blockdev-aging.service
systemctl start  blockdev-aging.service

exit 0

