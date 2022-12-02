# OpenFaaS RT runtime with EDF
OpenFaaS python3-flask-debian image modified to be able to run periodic tasks with EDF scheduler.

Currently the runtime reads and writes shared memory of the host computer. /dev/shm is attached to the container as hostPath.

To run tasks in EDF scheduler the container should be privileged.

OpenFaaS does not support attached volumes and privileged containers.

## Steps to start RT function in OpenFaaS

To use the RT runtime download and copy the content of python3-flask-debian-rt to your templates/python3-flask-debian-rt

faas --new --language python3-flask-debian-rt <name_of_your_function>

Write your function's code in <name_of_your_function>/handler.py

Add dependencies in <name_of_your_functon>/requirements.tyt

Add the followings to the <name_of_your_function>.yml under image tag
```
    environment:
      RUNRT: 0
```
RUNRT = 0 means don't run with EDF, RUNRT = 1 means use EDF

Patch your function to use host's shared memory and be able to use EDF
```
kubectl patch deployment -n openfaas-fn <name_of_your_function> --patch '{"spec": {"template": {"spec": {"volumes": [{"name": "shm", "hostPath": {"path": "/dev/shm", "type": "Directory"}}, {"name": "cpuset", "hostPath": {"path": "/sys/fs/cgroup/cpuset", "type": "Directory"}}], "containers": [{"name": "<name_of_your_function>", "securityContext": {"privileged": true, "runAsUser": 0}, "volumeMounts": [{"name": "shm", "mountPath": "/dev/shm"}, {"name": "cpuset", "mountPath": "/sys/fs/cgroup/cpuset"}]}]}}}}'
```
Set your function's CPU affinity (We use a single core in this example)

On the Kubernetes controller get your pod's conainer ID:
```
kubectl describe pod -n openfaas-fn facedet-6686c9f78d-2ghcv | grep "Container ID"
Container ID:   docker://c5361dd45c0724cb1e5518f026996a65dafbd62457a56fb880d1f8fa2b5d4e1c
```
On the Kubernetes worker where your function is running:
```
cd /sys/fs/cgroup/cpuset/kubepods.slice/kubepods-besteffort.slice
echo 0 > ./kubepods-besteffort-pod4b066b2b_1090_48e3_9b24_08039a536669.slice/docker-c5361dd45c0724cb1e5518f026996a65dafbd62457a56fb880d1f8fa2b5d4e1c.scope/cpuset.cpus
```
This will set the CPU affinity of your function pod to CPU 0
