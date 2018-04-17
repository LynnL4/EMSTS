#!/usr/bin/env python
# Author: turmary <turmary@126.com>
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
from kernel import core
import time
import os
import mraa


ADDR_ADC121 = 0x50
REG_ADDR_RESULT = 0x00
REG_ADDR_ALERT  = 0x01
REG_ADDR_CONFIG = 0x02
REG_ADDR_LIMITL = 0x03
REG_ADDR_LIMITH = 0x04
REG_ADDR_HYST   = 0x05
REG_ADDR_CONVL  = 0x06
REG_ADDR_CONVH  = 0x07

V_REF = 3.095
 
class ADC121C021:
    def __init__(self, busid, addr):
        self.bus = mraa.I2c(busid)
        self.bus.address(addr)

        self.bus.writeReg(REG_ADDR_CONFIG, 0x20)
 
    def value(self):
        "Read ADC data 0-4095."
        data_list = self.bus.readBytesReg(REG_ADDR_RESULT, 2)
        # print('data list', data_list)
        data = ((data_list[0] & 0x0f) << 8 | data_list[1]) & 0xfff
        return data

    def valueToVolts(self, v):
        return v * V_REF * 2 / 4096
 

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
        self.myAnalogDigitalConv = ADC121C021(self.parameters["busID"], ADDR_ADC121)

    def do_test(self):
        for a in range(10):
            val = self.myAnalogDigitalConv.value()
            voltsVal = self.myAnalogDigitalConv.valueToVolts(val)
            if self.parameters["volts"] - self.parameters["bias"] > voltsVal  \
            or self.parameters["volts"] + self.parameters["bias"] < voltsVal:
                self.ret["result"] = "failed"
            #print("ADC value: %s Volts = %s" % (val, voltsVal))
            time.sleep(.05)

        return self.ret


if __name__ == '__main__':
	d = {
		"volts": 3.0,
		"bias" : 0.2
	}
	a = ADC121C021(0, ADDR_ADC121)
	print(a.value())
	print("voltage = %f\n" % a.valueToVolts(a.value()))

