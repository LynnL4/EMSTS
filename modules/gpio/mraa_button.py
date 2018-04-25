#!/usr/bin/env python
# Author: turmary <turmary@126.com>
#
# Author: Baozhu Zuo <zuobaozhu@gmail.com>
# Copyright (c) 2018 Seeed Corporation.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import time
import mraa
from kernel import core

def int_handler(self):
    self.int = 1
    print("int_handler")

class subcore(core.interface):
    def __init__(self,parameters,platform,debug):
        super(subcore,self).__init__(parameters)
        self.parameters = parameters
        self.platform = platform
        self.debug  = debug
        self.ret = {
            "description": self.parameters["description"],
            "result": "ok"
        }
        self.timeout = self.parameters.get("timeout", 6)
        self.input_io_group = []
        self.output_io_group = []

        for pin in parameters["input_io"]:
            self.input_io_group.append(mraa.Gpio(pin))
        for pin in self.input_io_group:
            #setup gpio input direction
            pin.dir(mraa.DIR_IN)

        for pin in parameters["output_io"]:
            self.output_io_group.append(mraa.Gpio(pin))
        for pin in self.output_io_group:
            #setup gpio output direction
            pin.dir(mraa.DIR_OUT)
        # print("core.globaljob =",core.globaljob)

    def do_test(self):
        con = core.globaljob.getconsole()
        con.oled_putStatus(str(self.timeout) + "S:PRESS BUTTON")

        self.int = 0
        # button must be in high level before pressing
        for pin in self.input_io_group:
            if pin.read() == 0:
                self.ret["result"] = str(pin.getPin())
                return self.ret
            pin.isr(mraa.EDGE_FALLING, int_handler, self)

        for i in range(self.timeout):
            for pin in self.output_io_group:
                pin.write(pin.getPin() % 2)
            con.oled_setDisplayOnOff(0)
            if self.int: break
            time.sleep(0.5)

            for pin in self.output_io_group:
                pin.write(1 - pin.getPin() % 2)
            con.oled_setDisplayOnOff(1)
            if self.int: break
            time.sleep(0.5)

        con.oled_setDisplayOnOff(1)
        con.oled_putStatus("")

        # check for button pressed
        for pin in self.input_io_group:
            pin.write(1)
            pin.isrExit()
            if self.int == 0:
                self.ret["result"] = str(pin.getPin())
                return self.ret

        return self.ret

