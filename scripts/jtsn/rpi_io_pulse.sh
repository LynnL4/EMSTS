#!/bin/bash

listA="       79      232 15    13 19 20        168    51 77 78"
listB="216    50  14  194    16 17 18       149 200 38 76 12"

group_letters="ABCDEFGHIZ"

function gpiodset() {
	local io="$1"
	local v="$2"
	local grp_c=${io:0:1} grp
	local offset=${io:1}

	grp=$(( $(expr index "$group_letters" $grp_c) - 1 ))
	# (( grp -- ))

	cmds="gpioset gpiochip$grp $offset=$v"
	echo $cmds
	$cmds
	r=$?

	return $r
}

: <<'EOF'
while true; do
	for i in $listA; do
		# gpiodset $i 1;
		gpio set $i;
	done
	for i in $listB; do
		# gpiodset $i 0
		gpio clear $i;
	done
	sleep 0.2
	for i in $listA; do
		#gpiodset $i 0;
		gpio clear $i;
	done
	for i in $listB; do
		gpio set $i;
	done
	sleep 0.2
done
EOF

while true; do
	levels=""
	for i in $listA $listB; do
		levels="${levels}$(gpio input $i)"
	done
	echo levels=$levels
	sleep 0.5
done
exit 0
