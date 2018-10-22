#!/usr/bin/env python
# tary, 14:49 2018/10/18
from __future__ import print_function
import os
import sys
import time
# serial need:
#   pip install pyserial
import serial

tty_dev = "/dev/ttyACM0"
new_line="\r\n"

def serial_read(cmd = None):
    rcv = ''

    timecnt = 3
    while timecnt:
        timecnt -= 1
        match = "ls " + tty_dev[0:] + "*"
        # print("match = {}".format(match))
        if tty_dev in os.popen(match).read():
            break
        time.sleep(1)
    if not timecnt:
        return None

    try:
        port = serial.Serial(tty_dev, baudrate = 115200, timeout = 2)
    except:
        print("Cann't read from {}".format(tty_dev))
        return rcv
    # print(port)

    if cmd:
	port.write(cmd + new_line)
	port.flush()

    for i in range(8):
	# maximum 1024 bytes once reading
        rcv = port.read(1024)
        port.flush()
        if rcv != '':
            break
    # print(rcv)
    port.close()
    return rcv

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        tty_dev= sys.argv[1]
    # if len(sys.argv) >= 3:
    #    new_line = ''
    inp = raw_input("")
    if inp == '':
        quit(1)
    print("serial_rw cmd: {}".format(inp), file=sys.stderr)
    r = serial_read(inp);
    if r is None:
        quit(2)
    print(r)
    quit(0)

