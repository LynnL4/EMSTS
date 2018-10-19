#!/usr/bin/env python
# tary, 14:49 2018/10/18
import os
import sys
import time
# serial need:
#   pip install pyserial
import serial

tty_dev = "/dev/ttyACM0"

def serial_read(cmd = None):
    rcv = ''

    timecnt = 3
    while timecnt:
        timecnt -= 1
        if tty_dev in os.popen("ls /dev/ttyACM*").read():
            break
        time.sleep(1)
    if not timecnt:
        return rcv

    try:
        port = serial.Serial(tty_dev, baudrate = 115200, timeout = 2)
    except:
        print("Cann't read from {}".format(tty_dev))
        return rcv
    # print(port)

    if cmd:
	port.write(cmd + "\r\n")
	port.flush()

    while True:
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
    inp = raw_input("")
    if inp == '':
        quit(1)
    print(serial_read(inp))
    quit(0)
