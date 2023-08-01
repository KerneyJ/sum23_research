import time
boot_time = time.clock_gettime(time.CLOCK_BOOTTIME)
print(boot_time)

import zmq
import os
import sys
import pickle
import traceback

ip = sys.argv[1]
port = sys.argv[2]

context = zmq.Context()
task_sock = context.socket(zmq.REP)
result_sock = context.socket(zmq.REQ)

task_sock.bind("tcp://{}:{}".format(ip, port))

try:
    from parsl.serialize import unpack_apply_message, serialize
    def execute_task(bufs):
        user_ns = locals()
        user_ns.update({'__builtins__': __builtins__})

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

        exec(code, user_ns, user_ns)
        return user_ns.get(resultname)

    def connect_timeout(socket, addr, timeout=10):
        start = time.time()
        while time.time() - start < timeout:
            try:
                socket.connect(addr)
                return True
            except:
                continue
        return False

    ready_time = time.time()
    result_addr = task_sock.recv()
    result_sock.connect(result_addr.decode())
    task_sock.send("worker {} ready to receive work: {}; boot time: {}".format(port, ready_time, boot_time).encode())
    result_sock.send(b"connected to result socket")
    ack = result_sock.recv()
    while True:
        reqbuf = task_sock.recv()
        req = pickle.loads(reqbuf)
        tid = req["task_id"]
        buf = req["buffer"]
        task_sock.send("Worker: {} received task {}; buff length {}".format(port, tid, len(reqbuf)).encode())
        if reqbuf == b"STOP":
            client_sock.send(b"terminating")
            client_sock.close()
            server_sock.close()
        if reqbuf == b"START":
            continue

        result = execute_task(buf)
        print("Executed task {}".format(tid))
        serialized_result = serialize(result, buffer_threshold=1000000)
        result_package = {'type': 'result', 'task_id': tid, 'result': serialized_result}
        res = pickle.dumps(result_package)
        result_sock.send(res)
        ack = result_sock.recv()
except Exception as e:
    msg = "DEAD: {} \ntraceback: {}".format(str(e), traceback.format_exc())
    print(msg)
    result_sock.send(msg.encode())
