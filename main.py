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
import threading
import signal
import time


console_lock = threading.Lock()

def do_thread(fun,console,e):
    ret = fun()
    if console_lock.acquire():
        console.log(ret)
        console_lock.release() 
    if ret["result"] != "ok" and ret["result"] != "listen" and  ret["result"] != "watch": 
        e.set()
    
if __name__ == "__main__":
    interfaces = core.mainjob()
    jobs = interfaces.getjobs()
    console = interfaces.getconsole()
    e = threading.Event()
    exit_status = 0
    ts = []
    for j in jobs:
        if j.is_thread ==  "okay":
            t = threading.Thread(target=do_thread,args=(j.do_test,console,e,))
            t.start()
            ts.append(t)

    for i in jobs:
        if i.is_thread !=  "okay":
            ret = i.do_test()
            while not console_lock.acquire():
                time.sleep(0.1)
            console.log(ret)
            console_lock.release()
            if (ret["result"] != "ok" and ret["result"] != "listen" and ret["result"] != "watch") or e.wait(0.1):
                print("join()")
                for ii in ts:
                    ii.join()
                exit_status = 1
                break


    if console.finish():
        quit(exit_status)
    while True:
        time.sleep(1)
    #console.log("%o" % 20)
   
