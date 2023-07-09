import time
# boottime = time.clock_gettime(time.CLOCK_BOOTTIME)
boottime = time.time()

import zmq
import socket
import os
import sys
import pickle
import traceback

ip="10.0.{}.2".format(sys.argv[1])
port=20001

context = zmq.Context()
task_sock = context.socket(zmq.REP)
result_sock = context.socket(zmq.REQ)
task_sock.bind("tcp://{}:{}".format(ip,port))

# Parsl worker Loop
try:
    from parsl.serialize import unpack_apply_message, serialize
    def execute_task(bufs):
        user_ns = locals()
        user_ns.update({'__builtins__': __builtins__})
        # f, args, kwargs = pickle.loads(bufs)
        
        f, args, kwargs = unpack_apply_message(bufs, user_ns, copy=False)
        prefix = "parsl_"
        fname = prefix + "f"
        argname = prefix + "args"
        kwargname = prefix + "kwargs"
        resultname = prefix + "result"

        user_ns.update({fname: f,
                        argname: args,
                        kwargname: kwargs,
                        resultname: resultname})

        code = "{0} = {1}(*{2}, **{3})".format(resultname, fname,
                                               argname, kwargname)
        exec(code, user_ns, user_ns) # parsl_result = 1 + 2 for testing
        return user_ns.get(resultname)

    def connect_timeout(socket, addr, timeout=10):
        start = time.time()
        connected = False
        while time.time() - start < timeout:
            try:
                socket.connect(addr)
                connected = True
            except:
                continue
        return connected

    ready_time = time.time()
    result_addr = task_sock.recv()
    result_sock.connect(result_addr.decode())
    task_sock.send("worker {} ready to receive work: {}; boot time: {}".format(sys.argv[1], ready_time, boottime).encode())
    result_sock.send(b"connected to result socket")
    ack = result_sock.recv()
    while True:
        reqbuf = task_sock.recv()
        req = pickle.loads(reqbuf)
        tid = req["task_id"]
        buf = req["buffer"]
        task_sock.send("Worker: {} received task {}; buff length {}".format(ip, tid, len(reqbuf)).encode())
        if reqbuf == b"STOP":
            client_sock.sendall(b"terminating")
            client_sock.close()
            server_sock.close()
            os.system("reboot")
        if reqbuf == b"start":
            continue
        # In future surround the below in seperate try catches like process_worker_pool.py
        
        result = execute_task(buf)
        print("Executed task {}".format(tid))
        serialized_result = serialize(result, buffer_threshold=1000000)
        result_package = {'type': 'result', 'task_id': tid, 'result': serialized_result}
        res = pickle.dumps(result_package)
        result_sock.send(res)
        ack = result_sock.recv()
except Exception as e:
    msg = "DEAD: {} \ntraceback: {}".format(str(e), traceback.format_exc())
    result_sock.send(msg.encode())
    result_sock.close()
    if task_sock:
        task_sock.close()
    os.system("reboot")
