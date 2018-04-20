#!/usr/bin/env python
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
import sys
import threading
from lib import recorder
import numpy as np
import audioop
def play_music(p):
    os.popen(" aplay -D " + p["device"] + " /opt/music/" + p["music"])


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
    def do_test(self):
        t = threading.Thread(target=play_music,args=(self.parameters,))
        if self.platform == "respeaker v2":
            os.system("arecord -d 1 -f S16_LE -r 16000 -Dhw:0,0 -c 8 /tmp/aaa.wav")
            t.start()

        counter = 0
        mic_rms = [0,0,0,0,0,0,0,0]
        all_rms = 0
        if self.platform == "respeaker v2":   time.sleep(3)
        if self.platform == "PiMicsArrayKit": time.sleep(0.5)

            
        with recorder.recorder(16000, 8, 16000 / 16)  as mic:
            if self.platform == "PiMicsArrayKit":
                t.start()
            for chunk in mic.read_chunks():
                for i in range(8):
                    data = np.fromstring(chunk, dtype='int16')
                    data = data[i::8].tostring()
                    rms = audioop.rms(data, 2)
                    #rms_db = 17 * np.log10(rms)
                    #print('channel: {} RMS: {} dB'.format(i,rms))
                    if counter != 0:
                        mic_rms[i] = mic_rms[i] + rms
                                                             
                if counter == 30:
                    break
                counter = counter + 1
        for i in range(8):
            mic_rms[i] = mic_rms[i] / 30
            print('channel: {} RMS: {} dB'.format(i, mic_rms[i]), file=sys.stderr)
            if i == 6:
                if self.parameters["ch7"] - self.parameters["bias_c"] > mic_rms[i]  \
                or self.parameters["ch7"] + self.parameters["bias_c"] < mic_rms[i]:
                    self.ret["result"] = "ch7"  
                    break
            elif i == 7:
                if self.parameters["ch8"] - self.parameters["bias_c"] > mic_rms[i]  \
                or self.parameters["ch8"] + self.parameters["bias_c"] < mic_rms[i]:
                    self.ret["result"] = "ch8"
                    break
            else:
                if mic_rms[i] < self.parameters["mini"] :
                    self.ret["result"] = str(i)
                    break
        return self.ret

