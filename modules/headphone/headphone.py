#!/usr/bin/env python
# Author: turmary <turmary@126.com
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
import evdev
import glob
from select import select
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
        self.timeout = self.parameters.get("timeout", None)

    def do_test(self):
        device = glob.glob(self.parameters["device"])
        if not len(device):
            self.ret["result"] = "fail"
            return self.ret
        dev = evdev.device.InputDevice(device[0])
        # print(dev.capabilities(verbose=True, absinfo=True))

        con = core.globaljob.getconsole()
        con.oled_putStatus(str(self.timeout) + "S:INSERT HP")

        last_state = -1
        while last_state != 0:
            r,w,x = select([dev], [], [], self.timeout)
            if not len(r):
                self.ret["result"] = "fail"
                break
            for ev in dev.read():
                print(ev)
                if ev.type == evdev.ecodes.EV_SW and ev.code == evdev.ecodes.SW_HEADPHONE_INSERT:
                    last_state = ev.value
                    if not ev.value:
                        break
                    else:
                        # mute the speaker
                        if self.platform == "PiMicsArrayKit":
                            os.system("amixer -c " + str(self.parameters["card_nr"]) \
                                      + " cset numid=20,iface=MIXER,name='speaker volume' 0")

        con.oled_putStatus("")
        # stop playing
        if self.platform == "PiMicsArrayKit":
            os.system("killall aplay")
            os.system("killall arecord")

        return self.ret

