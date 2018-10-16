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
from abc import ABCMeta, abstractmethod
import json
import importlib
from collections import OrderedDict

global globaljob
globaljob = None

class interface:
    __metaclass__ = ABCMeta

    def __init__(self, parameters):
        self.is_enable = parameters.get("status")
        self.is_thread = parameters.get("thread")

    def do_test(self):
        pass

    
class mainjob:
    def __init__(self):
        global globaljob
        self.json_data = json.load(open("config.json",'r'), object_pairs_hook=OrderedDict)
        self.interfaces = []
        print(self.json_data)
        self.console = importlib.import_module(
                            "modules.console." + self.json_data["console"]["file"]
                        ).console(self.json_data["console"], self.json_data["project"])

        globaljob = self

    def getjobs(self):
        for j in self.json_data:
            if j == "project" or j == "console":
                continue
            if self.json_data[j]["status"] == "okay":
                module = self.json_data[j].get("module", j)
                self.interfaces.append(importlib.import_module(
                    "modules." + module + "." + self.json_data[j]["file"]
                ).subcore(
                    self.json_data[j], self.json_data["project"], self.console.debug
                ))
        return self.interfaces

    def getconsole(self):
        return self.console

