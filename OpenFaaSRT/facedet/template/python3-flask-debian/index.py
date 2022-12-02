from flask import Flask, request, g, Response
import logging

from multiprocessing import Process
from multiprocessing import shared_memory
import os
import sys
import mmap
import time
import scheddl
from function import handler

#with open("/sys/fs/cgroup/cpuset/partition/tasks", "a") as f:
#    f.write(str(os.getpid()))

runrt = int(str(os.getenv("RUNRT")))

def shmopen(fn, length):
    f = os.open("/dev/shm/"+fn, os.O_RDWR| os.O_CREAT)
    os.ftruncate(f, length)
    mm = mmap.mmap(f, 0, prot=mmap.PROT_WRITE)
    return mm

mmframe = shmopen("frame", 480*848*3)
app = Flask(__name__)

#@app.route('/', methods=['GET', 'POST', 'PATCH', 'DELETE'])

def handle():
    dl_args = (
        141000000,
        142000000,
        142000000
        #20 * 1000 * 1000, # runtime in nanoseconds
        #50 * 1000 * 1000, # deadline in nanoseconds
        #50 * 1000 * 1000  # time period in nanoseconds
    )
    if(runrt == 1):
        scheddl.set_deadline(*dl_args)
    handler.handle("req", mmframe, "/dev/shm/test2.jpg")

p = Process(target=handle, args=())
p.start()

@app.route("/_/health")
def healthcheck():
    return "OK"

if __name__ == '__main__':
    #import logging
    #import sys
    #log = logging.getLogger('werkzeug')
    #log.setLevel(logging.ERROR)
    #log.setLevel(logging.INFO)
    app.run('0.0.0.0', 8080, debug=False, threaded = False)
