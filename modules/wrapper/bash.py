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
import re
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
        self.cmd = self.parameters["cmd"]

        self.RET_OK = 0
        self.RET_FAIL = 255

    def _cmd_test(self):
        for line in os.popen(self.cmd + "; echo \"###RESULT=$?###\";"):
            match = re.match(r'###RESULT=([0-9]+)###', line)
            if match is None: continue

            r = int(match.group(1))
            # print("result = %d" % r)
            return r
        return self.RET_FAIL

    def do_test(self):
        r = self._cmd_test()
        if r != self.RET_OK:
            self.ret["result"] = "0x%02X" % r
        return self.ret

if __name__ == '__main__':
    d = {
	"description": "EEPROM",
	"cmd" : "eeprom-wp"
    }
    c = subcore(d, "platform", 0)
    print(c.do_test())

