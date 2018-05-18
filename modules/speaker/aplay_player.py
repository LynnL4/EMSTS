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
import os
import sys
import time
import threading
import wave
import pyaudio
import audioop
import numpy as np
from kernel import core
from lib import recorder


RATE = 16000
CHUNK = 2048
REC_FILE = "/tmp/pimics.wav"

def play_music(p):
    os.system("alsactl restore 1")
    os.popen("aplay -r " + str(RATE) + " -D " + p["device"] + " /opt/music/" + p["music"])


class subcore(core.interface):
    def __init__(self,parameters,platform,debug):
        super(subcore,self).__init__(parameters)
        self.parameters = parameters
        self.platform = platform
        self.debug  = debug
        self.ret = {
            "description": self.parameters["description"],
            "result": ""
        }
        self.skip = self.parameters.get("skip", 1)
        self.loop = self.parameters.get("loop", 30)
        self.min_list = self.parameters.get("min_list", None)
        self.fail_times = self.parameters.get("fail_times", 5)

    def inner_test(self):
        self.t = threading.Thread(target=play_music,args=(self.parameters,))
        if self.platform == "respeaker v2":
            os.system("arecord -d 1 -f S16_LE -r " + str(RATE) + " -Dhw:0,0 -c 8 /tmp/aaa.wav")
            self.t.start()

        counter = 0
        mic_rms = [0,0,0,0,0,0,0,0]

        if self.platform == "respeaker v2":   time.sleep(3)

        os.system("rm -f " + REC_FILE + "; arecord -d 7 -f S16_LE -r " \
                + str(RATE) + " -D plughw:1,0 -c 8 " + REC_FILE + " & ")
        while not os.path.exists(REC_FILE):
            time.sleep(0.1)
        while os.path.getsize(REC_FILE) <= 0x200:
            time.sleep(0.1)
        self.t.start()
        time.sleep(1);

        wf = wave.open(REC_FILE, "rb")
        chunk = wf.readframes(CHUNK)
        while chunk != b'':
                for i in range(8):
                    data = np.fromstring(chunk, dtype='int16')
                    data = data[i::8].tostring()
                    rms = audioop.rms(data, 2)
                    # rms_db = 17 * np.log10(rms)
                    # print('cnt: {} channel: {} RMS: {} dB'.format(counter, i, rms), file=sys.stderr)
                    if counter >= self.skip:
                        mic_rms[i] = mic_rms[i] + rms

                counter = counter + 1
                if counter >= self.skip + self.loop:
                    break
                chunk = wf.readframes(CHUNK)
                time.sleep(CHUNK * 1.1 / RATE)

        for i in range(8):
            mic_rms[i] = mic_rms[i] / self.loop
            print('channel: {} RMS: {} dB'.format(i, mic_rms[i]), file=sys.stderr)
            if i == 6:
                if self.parameters["ch7"] - self.parameters["bias_c"] > mic_rms[i]  \
                or self.parameters["ch7"] + self.parameters["bias_c"] < mic_rms[i]:
                    self.ret["result"] = self.ret["result"] + "ch7"
            elif i == 7:
                if self.parameters["ch8"] - self.parameters["bias_c"] > mic_rms[i]  \
                or self.parameters["ch8"] + self.parameters["bias_c"] < mic_rms[i]:
                    self.ret["result"] = self.ret["result"] + "ch8"
            elif self.min_list:
                if mic_rms[i] < self.min_list[i]:
                    self.ret["result"] = self.ret["result"] + str(i + 1)
            else:
                if mic_rms[i] < self.parameters["mini"] :
                    self.ret["result"] = self.ret["result"] + str(i + 1)

    def do_test(self):
        for i in range(self.fail_times):
            self.ret["result"] = ""
            self.inner_test()
            if self.ret["result"] == "":
                self.ret["result"] = "ok"
                break
            self.t._stop()
            os.system("killall arecord; killall aplay")
            time.sleep(1);
        return self.ret

