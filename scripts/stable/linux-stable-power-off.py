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
LVL_RELAY_OFF = GPIO.HIGH
LVL_RELAY_ON  = GPIO.LOW

TIMEOUT_LOGIN = 45 # Seconds
TIMEOUT_SHELL = 5
TIMEOUT_PWROFF= 12
# HOSTNAME = 'beaglebone'
HOSTNAME = 'SCHNEIDER2'

# GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(Pin_Relay, GPIO.OUT)

def power_cycle(off_secs = 2):
    GPIO.output(Pin_Relay, LVL_RELAY_OFF)
    time.sleep(off_secs)
    GPIO.output(Pin_Relay, LVL_RELAY_ON)

is_repower = False
def main():
    with serial.Serial('/dev/ttyAMA0', 115200, timeout=0) as ser:
        ss = SerialSpawn(ser)
        # DEBUG
        ss.logfile = sys.stderr.buffer
        total_cnt = 0
        success_cnt = 0
        fail_cnt = 0

        logfile = time.strftime("LINUX-LOG-%Y-%m-%d-%H.txt", time.localtime())
        f = open(logfile, 'a')

        power_cycle()
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        while True:
            # try:
            #     a = ss.expect('SCHNEIDER2 login:')
            #     ss.sendline('root')
            #     b = ss.expect('root@SCHNEIDER2:')
            #     ss.sendline('poweroff')
            #     power_cycle()
            # except TIMEOUT:
            #     a = ss.expect('SCHNEIDER2 login:')
            #     ss.sendline('root')
            #     b = ss.expect('root@SCHNEIDER2:')
            #     ss.sendline('poweroff')
            # power_cycle()
            # ser_bytes = ser.readline()
            # print(ser_bytes)

            # time.sleep(5)
            # print(str(ss.readline()))
            # print(str(ss.readline()))

            ss.sendline()
            index_login = ss.expect(pattern=[HOSTNAME + ' login:', pexpect.TIMEOUT], timeout = TIMEOUT_LOGIN)
            if index_login == 0:  # normal
                ss.sendline('root')
            elif index_login == 1:  # device get stuck
                print("Device get stuck in index_login.")
                f.write("Device get stuck in index_login.\r\n")
                power_cycle()
                continue;

            # ser_bytes = ser.readline()
            # print(ser_bytes)

            ss.sendline()
            index_shell = ss.expect(pattern=['root@' + HOSTNAME + ':', pexpect.TIMEOUT], timeout = TIMEOUT_SHELL)
            if index_shell == 0:  # normal
                ss.sendline('poweroff')
            elif index_shell == 1:  # device get stuck
                print("Device get stuck in index_shell.")
                f.write("Device get stuck in index_shell.\r\n")
                power_cycle()
                continue;

            '''record log'''
            # data = ss.before
            # ret = chardet.detect(data)
            # print(ret)
            # s = str(data, encoding = "ascii")  
            # print(type(data))
            # print(type(s))
            # f.write(s)

            total_cnt = total_cnt + 1
            is_repower = False

            end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            time.sleep(1)
            index_btldr = ss.expect(pattern=['U-Boot ', pexpect.TIMEOUT], timeout = TIMEOUT_PWROFF)
            if index_btldr == 0:
                fail_cnt = fail_cnt + 1
                print('____________________________________')
                print('****** \033[5;31;43m POWER OFF FAILED \033[0m')
                print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                f.write("POWEROFF FAILED!\r\n")

            elif index_btldr == 1:  # time out = success
                success_cnt = success_cnt + 1
                is_repower = True
                print('____________________________________')
                print('###### \033[1;42m POWER OFF OK! \033[0m')
                print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                f.write("POWEROFF OK!\r\n")
            # print(ss.before)

            print("total_cnt   :", total_cnt)
            print("success_cnt :", success_cnt)
            print("fail_cnt    :", fail_cnt)
            print("start time  :", start_time)
            print("end time    :", end_time)
            print("------------------------------------------------------\n")

            f.write("total_cnt   :" + str(total_cnt) + "\r\n")
            f.write("success_cnt :" + str(success_cnt) + "\r\n")
            f.write("fail_cnt    :" + str(fail_cnt) + "\r\n")
            f.write("start time  :" + start_time + "\r\n")
            f.write("end time    :" + end_time + "\r\n")
            f.write("------------------------------------------------------\r\n\r\n")
            f.flush()

            if is_repower:
                power_cycle()

            start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # print(ss.read())

if __name__ == "__main__":
    main()

