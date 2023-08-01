print("entered container")
import time
boot_time = time.clock_gettime(time.CLOCK_BOOTTIME)
print("imported time")
import zmq
import os
import sys
import pickle
import traceback
print("imported other libraries")

ip = sys.argv[1]
port = sys.argv[2]

print("got args {} {}".format(ip, port))

context = zmq.Context()
task_sock = context.socket(zmq.REP)
result_sock = context.socket(zmq.REQ)
print("created sockets")

task_sock.bind("tcp://{}:{}".format(ip, port))
print("binded task socket to address")

result_addr = task_sock.recv()
result_sock.connect(result_addr.decode())
task_sock.send(b"hello")
result_sock.send(b"connected to server")
ack = result_sock.recv()
