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
from lib import display
import time

class console:
    def __init__(self,parameters,platform):
        self.parameters = parameters
        self.platform = platform        
        self.t = True
        self.d = display.display()
        self.d.start()
        self.data_json = {}           
    def log(self,*args):
        for a in args:
            # Failed on any one item failing
            if a["result"] != "ok" and a["result"] != "listen" and  a["result"] != "watch": 
                if self.t == True:
                    self.t = False

            self.data_json.clear()
            self.data_json["type"] = "text"
            self.data_json["description"] = a["description"]
            self.data_json["result"] = a["result"].upper()
            self.d.data.put(self.data_json)
            time.sleep(0.1)

    def debug(self,*args):
        for a in args:
            print(a)     
    def finish(self):

        if self.platform =="respeaker v2":
            self.data_json.clear()
            self.data_json["type"] = "picture"
            self.data_json["path"] = "/opt/pic/rgb.png"
            self.data_json["location"] = "right"
            self.d.data.put(self.data_json)
            time.sleep(0.1)

            self.data_json["location"] = "left"
            self.d.data.put(self.data_json)
            time.sleep(0.1)
            
        self.data_json.clear()
        self.data_json["type"] = "finish"    
        self.data_json["finish"] = self.t
        self.d.data.put(self.data_json)
        if self.t:
            print("test succeed")
        else:
            print("test failed")
