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
from kernel import core

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
        self.bus = self.parameters["busID"]
        self.addrs = self.parameters["addr_list"]

        self.ADDR_UNEXIST = 0
        self.ADDR_FREE    = 1
        self.ADDR_INUSE   = 2

    def detect(self, addr):
        for line in os.popen("i2cdetect -y " + str(self.bus) + (" " + str(addr)) * 2):
            pos = line.find(':')
            if pos == -1: continue
            line = line[pos + 1:-1].strip()
            '''
            print("line=@" + line + "@")
            for i in range(len(line)):
                print("0x%02X " % ord(line[i]), end='')
            print("")
            '''
            if not len(line): continue
            if line == "UU": return self.ADDR_INUSE
            if line == "--": break
            # print("line = @" + line + "@")
            return self.ADDR_FREE
        return self.ADDR_UNEXIST

    def do_test(self):
        for i in range(len(self.addrs)):
            r = self.detect(self.addrs[i])
            print("ADDR[0x%2X] = %s" % (self.addrs[i], str(r)))
            if r == 0:
                self.ret["result"] = "0x%02X" % self.addrs[i]
                break
        return self.ret

if __name__ == '__main__':
	d = {
		"description": "i2c",
		"busID": 1,
		"addr_list" : [0x1A, 0x35, 0x3B, 0x45]
	}
	c = subcore(d, "platform", 0)
	print(c.do_test())

