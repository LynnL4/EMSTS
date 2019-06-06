#!/usr/bin/env python3
# tary, 14:49 2019/06/03
from __future__ import print_function
import os
import sys
import time
# serial need:
#   pip install pyserial
import serial

baud_rate = 115200

def rts_cts_check(tty_a, tty_b):
    rt = ''

    try:
        pa = serial.Serial(tty_a, baudrate = baud_rate, timeout = 2)
    except:
        rt = "Cann't open from {}".format(tty_a)
        return rt

    try:
        pb = serial.Serial(tty_b, baudrate = baud_rate, timeout = 2)
    except:
        rt = "Cann't open from {}".format(tty_b)
        pa.close()
        return rt

    if rt == '':
        pa.rts = True
        if not pb.cts:
            rt = "{} CTS False when {} RTS True".format(tty_b, tty_a)

    # time.sleep(1.0)
    if rt == '':
        pa.rts = False
        if pb.cts:
            rt = "{} CTS True when {} RTS False".format(tty_b, tty_a)

    # time.sleep(1.0)
    if rt == '':
        pb.rts = True
        if not pa.cts:
            rt = "{} CTS False when {} RTS True".format(tty_a, tty_b)

    # time.sleep(1.0)
    if rt == '':
        pb.rts = False
        if pa.cts:
            rt = "{} CTS True when {} RTS False".format(tty_a, tty_b)

    pa.close()
    pb.close()
    return rt

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('''Usage:
    {} tty1A,tty1B tty2A,tty2B ...'''.format(sys.argv[0]))
        quit(1)

    for i in range(1, len(sys.argv)):
        pair = sys.argv[i]
        # print("pair[{}] = {}".format(i - 1, pair), end='')

        ttya = "/dev/" + pair.split(',')[0]
        ttyb = "/dev/" + pair.split(',')[1]
        r = rts_cts_check(ttya, ttyb)
        if len(r):
            print("{} ERR {}".format(pair, r))
            quit(2)

        print("{} OK".format(pair))
    quit(0)

