#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
# Copyright (C) 2020 Seeed Technology Co.,Ltd.
#               turmary@126.com
#
# Original written by Cai-90hou.
#
#   Some boards could not power off properly, 
# after the board power off, it will start up automatically
# a few seconds later.
#   This script will found these conditions.
# and record the probability.
#
import RPi.GPIO as GPIO
import time
import sys

import serial
from pexpect_serial import SerialSpawn
import pexpect
import chardet

# pin 6
Pin_Relay = 6
# Pin_Relay = 5
LVL_RELAY_OFF = GPIO.HIGH
LVL_RELAY_ON  = GPIO.LOW

# off_secs --- The time for DC capacitor discharging
DC_OFF_SECS     = 8
TIMEOUT_LOGIN   = 45 # Seconds
TIMEOUT_SHELL   = 8
SHELL_TO_PWROFF = 1
TIMEOUT_PWROFF  = 10
# HOSTNAME = 'beaglebone'
HOSTNAME = 'SCHNEIDER2'

# GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(Pin_Relay, GPIO.OUT)

def power_cycle():
    GPIO.output(Pin_Relay, LVL_RELAY_OFF)
    time.sleep(DC_OFF_SECS)
    GPIO.output(Pin_Relay, LVL_RELAY_ON)

def decode_all(pe):
    d = pe.before
    if not d:
        return ""
    # print(chardet.detect(d))
    # print(type(d), d)
    while True:
        try:
            s = str(d, encoding = "ascii")
        except:
            d = d[1:]
        else:
            break
    #print(type(s), s)
    return s

def main():
    with serial.Serial('/dev/ttyAMA0', 115200, timeout=0) as ser:
        ss = SerialSpawn(ser)
        # DEBUG
        ss.logfile = sys.stderr.buffer
        total_cnt = 0
        success_cnt = 0
        fail_cnt = 0
        first      = True
        log_first  = ""

        logfile = time.strftime("LINUX-LOG-%Y-%m-%d-%H.txt", time.localtime())
        f = open(logfile, 'a')

        f.write("DC_OFF_SECS      = {}\n".format(DC_OFF_SECS))
        f.write("TIMEOUT_LOGIN    = {}\n".format(TIMEOUT_LOGIN))
        f.write("TIMEOUT_SHELL    = {}\n".format(TIMEOUT_SHELL))
        f.write("SHELL_TO_PWROFF  = {}\n".format(SHELL_TO_PWROFF))
        f.write("TIMEOUT_PWROFF   = {}\n".format(TIMEOUT_PWROFF))

        power_cycle()
        tm_start = time.localtime()
        while True:
            # try:
            #     a = ss.expect('SCHNEIDER2 login:')
            #     ss.sendline('root')
            #     b = ss.expect('root@SCHNEIDER2:')
            #     ss.sendline('poweroff')
            #     power_cycle()
            # except TIMEOUT:
            #     pass
            # power_cycle()
            # ser_bytes = ser.readline()
            # print(ser_bytes)

            ss.sendline()

            if first:
                log_first += decode_all(ss)
            index_login = ss.expect(pattern=[HOSTNAME + ' login:', pexpect.TIMEOUT], timeout = TIMEOUT_LOGIN)
            if index_login == 0:  # normal
                ss.sendline('root')
            elif index_login == 1:  # device get stuck
                print("Wait login TIMEOUT!!!")
                f.write("Wait login TIMEOUT!!!\n")
                power_cycle()
                log_first += decode_all(ss)
                f.write("### BOOT LOG ###\n" + log_first)
                f.write("\n\n\n\n\n")
                continue;

            # ser_bytes = ser.readline()
            # print(ser_bytes)

            ss.sendline()
            if first:
                log_first += decode_all(ss)
            index_shell = ss.expect(pattern=['root@' + HOSTNAME + ':', pexpect.TIMEOUT], timeout = TIMEOUT_SHELL)
            if index_shell == 0:  # normal
                pass
            elif index_shell == 1:  # device get stuck
                print("Wait shell TIMEOUT!!!")
                f.write("Wait shell TIMEOUT!!!\n")
                power_cycle()
                continue

            # Wait for system startup complete
            """
            for i in range(SHELL_TO_PWROFF):
                ss.sendline('systemd-analyze time')
                index_analyze = ss.expect(pattern=['Startup finished', pexpect.TIMEOUT], timeout = 1)
                if index_analyze == 0:
                    break
                time.sleep(1)

            time.sleep(5)
            ss.sendline('ifconfig wlan0 down')
            time.sleep(0.5)
            ss.sendline('rmmod wlcore_sdio')
            time.sleep(SHELL_TO_PWROFF - 5)
            """
            time.sleep(SHELL_TO_PWROFF)

            time.sleep(0.1)
            ss.sendline('poweroff')

            total_cnt = total_cnt + 1
            is_repower = False

            if first:
                log_first += decode_all(ss)
            index_pwroff = ss.expect(pattern=['reboot: Power down', pexpect.TIMEOUT], timeout = TIMEOUT_PWROFF)
            tm_pwrdn = time.localtime()
            if first:
                log_first += decode_all(ss)
            index_btldr = ss.expect(pattern=['U-Boot ', pexpect.TIMEOUT], timeout = 4)
            if index_btldr == 0:
                fail_cnt = fail_cnt + 1
                print('____________________________________')
                print('****** \033[5;31;43m POWER OFF FAILED \033[0m')
                print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                f.write("POWEROFF FAILED!\n")

            elif index_btldr == 1:  # time out = success
                success_cnt = success_cnt + 1
                is_repower = True
                print('____________________________________')
                print('###### \033[1;42m POWER OFF OK! \033[0m')
                print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                f.write("POWEROFF OK!\n")

            fa = "FAIL        : {}\n".format(fail_cnt)
            ot = "OK/TOTAL    : {} / {}\n".format(success_cnt, total_cnt)
            tm_start_str = time.strftime("%Y-%m-%d %H:%M:%S", tm_start)
            st = "START       : {}\n".format(tm_start_str)
            ps = time.mktime(tm_pwrdn) - time.mktime(tm_start)
            cy = "USED        : {} Secs\n".format(ps)
            print(fa + ot + st + cy, end = '')
            print("------------------------------------------------------\n")

            if first:
                log_first += decode_all(ss)
                f.write("### BOOT LOG ###\n" + log_first)
                f.write("\n\n\n\n\n")

            f.write(fa + ot + st + cy)
            f.write("------------------------------------------------------\n\n")
            f.flush()

            if is_repower:
                power_cycle()

            tm_start = time.localtime()
            first = False

if __name__ == "__main__":
    main()

