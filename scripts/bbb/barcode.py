#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import time
import serial
import binascii
import evdev

def readID_serial():
    rcv = 'blank'
    timecnt = 5
    while timecnt:
        timecnt = timecnt-1
        if "/dev/ttyACM0" in os.popen("ls /dev/ttyACM*").read() and "/dev/ttyACM1" in os.popen("ls /dev/ttyACM*").read():
            break
        time.sleep(1)

    try:
        port = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=0.5)
    except:
        try:
            port = serial.Serial("/dev/ttyACM1", baudrate=115200, timeout=0.5)
        except IOError:
            print("cannt read /dev/ttyACM1 or /dev/ttyACM0")
            return rcv

    print(port)
    while True:
        rcv = port.read(12)
        print(rcv)
        port.flush()
        if(rcv != '' and rcv[0:3] == 'BBG' and rcv[-1] >= '0' and rcv[-1] <= '9'):
            break
    return rcv

def readID_kbd():
    ID = ''
    path = os.popen("ls /dev/input/by-path/ | grep kbd").read().split('\n', 1)[0]
    if None == path:
        return 'blank'
    path = '/dev/input/by-path/' + path
    dev = evdev.InputDevice(path)
    scancodes = {
        # Scancode: ASCIICode
        0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
        10: u'9', 11: u'0', 12: u'_', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
        20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
        30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u';',
        40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
        50: u'M', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
    }

    for event in dev.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            data = evdev.categorize(event)  # Save the event temporarily to introspect it
            if data.keystate == 1:  # Down events only
                key_lookup = scancodes.get(data.scancode) or u'UNKNOWN:{}'.format(data.scancode)  # Lookup or return UNKNOWN:XX
                if key_lookup != 'CRLF':
                    if key_lookup != 'LSHFT':
                        ID = ID + key_lookup
                else:
                    return ID.encode("utf-8")
def readID():
    out = os.popen("ls /dev/input/by-path/ | grep kbd").read()
    if "kbd" in out:
        print("kbd barcoder detect", file=sys.stderr)
        id = readID_kbd()
    else:
        print("not a kbd barcoder", file=sys.stderr)
        id = readID_serial()
    return id

if __name__ == '__main__':
    print(readID())

