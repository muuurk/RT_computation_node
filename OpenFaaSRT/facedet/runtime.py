from flask import Flask, request, g, Response
import logging

from multiprocessing import Process
from multiprocessing import shared_memory
import os
import mmap
import time
import scheddl
import handler

#with open("/sys/fs/cgroup/cpuset/partition/tasks", "a") as f:
#    f.write(str(os.getpid()))

def shmopen(fn, length):
    f = os.open("/dev/shm/"+fn, os.O_RDWR| os.O_CREAT)
    os.ftruncate(f, length)
    #os.ftruncate(f, 2*1048576)
    mm = mmap.mmap(f, 0, prot=mmap.PROT_WRITE)
    return mm

mmfib = shmopen("fib", 20899) 
mmtime = shmopen("time", 19)

app = Flask(__name__)

#@app.route('/', methods=['GET', 'POST', 'PATCH', 'DELETE'])

def handle():
    dl_args = (
        20 * 1000 * 1000, # runtime in nanoseconds
        50 * 1000 * 1000, # deadline in nanoseconds
        50 * 1000 * 1000  # time period in nanoseconds
    )

    scheddl.set_deadline(*dl_args)
    while(True):
        start_time = time.time_ns()
        mmfib.write(bytes(str(handler.fib()),'utf-8'))
        mmtime.write(bytes(str(start_time), 'utf-8'))
        #mmtime.write(start_time.to_bytes(1048576, "little"))
        mmfib.seek(0)
        mmtime.seek(0)
        #print(time.time_ns()-start_time)


p = Process(target=handle, args=())
p.start()

@app.route("/healthz")
def healthcheck():
    return "OK"

if __name__ == '__main__':
    #import logging
    #import sys
    #log = logging.getLogger('werkzeug')
    #log.setLevel(logging.ERROR)
    #log.setLevel(logging.INFO)
    app.run('0.0.0.0', 8080, debug=False, threaded = False)
