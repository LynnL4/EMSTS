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
from __future__ import print_function
import sys

class console:
    def __init__(self,parameters,platform):
        self.t = True
     
    def log(self,*args):
        for a in args:
            #只要有一项测试出错，测试失败
            if a["result"] != "ok" and a["result"] != "listen" and  a["result"] != "watch": 
                if self.t == True:
                    self.t = False
            print("*****************************************", end='')
            print(a, end='')
            print("*****************************************")
            sys.stdout.flush()

    def debug(self,*args):
        for a in args:
            print(a)     
    def finish(self):
        if self.t:
            print("test succeed")
        else:
            print("test failed")
        return True

