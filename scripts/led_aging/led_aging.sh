#!/bin/sh
# tary, 16:46 2013-4-22

x=$(/bin/ps -ef | /bin/grep "[l]ed_aging")
if [ ! -n "$x" -a -x /usr/bin/led_aging ]; then
	/usr/bin/led_aging &
fi
