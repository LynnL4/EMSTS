#!/bin/bash

list="0 1 169 16 4 5 66 115 114 7 6 68 8 9 117 22 23 116 21 18 15 14"

for i in $list; do
	gpio set $i
	sleep 0.1
	gpio clear $i
done

