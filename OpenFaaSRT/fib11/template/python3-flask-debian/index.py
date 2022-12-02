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
    #os.ftruncate(f, 2*1048576)
    mm = mmap.mmap(f, 0, prot=mmap.PROT_WRITE)
    return mm

mmfib = shmopen("fib", 20899) 
mmtime = shmopen("time", 19)

app = Flask(__name__)

#@app.route('/', methods=['GET', 'POST', 'PATCH', 'DELETE'])

def handle():
    dl_args = (
        220000000,
        450000000,
        450000000
        #20 * 1000 * 1000, # runtime in nanoseconds
        #50 * 1000 * 1000, # deadline in nanoseconds
        #50 * 1000 * 1000  # time period in nanoseconds
    )
    if(runrt == 1):
        scheddl.set_deadline(*dl_args)
    sys.set_int_max_str_digits(30000)
    while(True):
        #print("Hello")
        start_time = time.time_ns()
        mmfib.write(bytes(str(handler.handle("")),'utf-8'))
        mmtime.write(bytes(str(start_time), 'utf-8'))
        #mmtime.write(start_time.to_bytes(1048576, "little"))
        mmfib.seek(0)
        mmtime.seek(0)
        exec_time = time.time_ns()-start_time
        with open("out_.txt", "a") as f:
            f.write(str(start_time)+"\t"+str(exec_time)+"\n")
        #print(time.time_ns()-start_time)
        if(runrt == 1):
            os.sched_yield()
        else:
            try:
                runtime = time.time_ns()-start_time
                time.sleep((450000000 - runtime)/1000000000)
            except:
                time.sleep(0.23)

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
