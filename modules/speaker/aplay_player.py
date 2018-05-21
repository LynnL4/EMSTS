#!/usr/bin/env python
#
# Author: turmary <turmary@126.com>
# Copyright (c) 2018 Seeed Corporation.
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
import sys
import time
import threading
import wave
import pyaudio
import audioop
import numpy as np
from kernel import core
from lib import recorder
from lib.snowboy import snowboydecoder


RATE = 16000
CHUNK = 2048
REC_FILE = "/tmp/pimics.wav"

def play_music(device, music):
    os.system("alsactl restore 1")
    os.popen("aplay -r " + str(RATE) + " -D " + device + " " + music)


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

    def white_test(self):
        p = self.parameters
        self.t = threading.Thread(target=play_music,args=(p["device"], p["white"]))

        counter = 0
        mic_rms = [0,0,0,0,0,0,0,0]

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
            print('white channel: {} RMS: {} dB'.format(i, mic_rms[i]), file=sys.stderr)
            if i == 6:
                if self.parameters["ch7"] - self.parameters["bias_c"] > mic_rms[i]  \
                or self.parameters["ch7"] + self.parameters["bias_c"] < mic_rms[i]:
                    self.ret["result"] = self.ret["result"] + "CH7"
            elif i == 7:
                if self.parameters["ch8"] - self.parameters["bias_c"] > mic_rms[i]  \
                or self.parameters["ch8"] + self.parameters["bias_c"] < mic_rms[i]:
                    self.ret["result"] = self.ret["result"] + "CH8"
            elif self.min_list:
                if mic_rms[i] < self.min_list[i]:
                    self.ret["result"] = self.ret["result"] + str(i + 1)
            else:
                if mic_rms[i] < self.parameters["mini"] :
                    self.ret["result"] = self.ret["result"] + str(i + 1)
        print('', file=sys.stderr)

    def snowboy_test(self):
        p = self.parameters
        self.t = threading.Thread(target=play_music,args=(p["device"], p["snowboy"]))

        detection = snowboydecoder.HotwordDetector("lib/snowboy/resources/models/snowboy.umdl", sensitivity=p["sensitivity"])

        counter = 0
        mic_rms = [0,0,0,0,0,0,0,0]

        os.system("rm -f " + REC_FILE + "; arecord -d 3 -f S16_LE -r " \
                + str(RATE) + " -D plughw:1,0 -c 8 " + REC_FILE + " & ")
        while not os.path.exists(REC_FILE):
            time.sleep(0.1)
        while os.path.getsize(REC_FILE) <= 0x200:
            time.sleep(0.1)
        self.t.start()
        time.sleep(1);


        wf = wave.open(REC_FILE, "rb")
        chunk = wf.readframes(wf.getnframes())
        data = np.fromstring(chunk, dtype='int16')
        for i in range(p["snowboy_chans"]):
            ans = detection.detector.RunDetection(np.array(data[i::8], dtype=np.int16).tobytes())
            if ans == 0:
                self.ret["result"] = str(i + 1)
                break
            print('channel: {} hotword detected!'.format(i), file=sys.stderr)
        wf.close()
        print('', file=sys.stderr)

    def do_test(self):
        for i in range(self.fail_times):
            self.ret["result"] = ""
            self.white_test()
            self.t._stop()
            os.system("killall arecord; killall aplay")
            time.sleep(1)
            if self.ret["result"] == "":
                self.ret["result"] = "ok"
                break
        if self.ret["result"] != "ok":
            return self.ret

        time.sleep(1)
        for i in range(self.fail_times * 2):
            self.ret["result"] = ""
            self.snowboy_test()
            self.t._stop()
            os.system("killall arecord; killall aplay")
            time.sleep(1)
            if self.ret["result"] == "":
                self.ret["result"] = "ok"
                break

        p = self.parameters
        self.t = threading.Thread(target=play_music,args=(p["device"], p["white"]))
        self.t.start()
        return self.ret

