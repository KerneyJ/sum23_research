import time
# boottime = time.clock_gettime(time.CLOCK_BOOTTIME)
boottime = time.time()

import socket
import os
import sys
import pickle
import traceback

ip="10.0.{}.2".format(sys.argv[1])
port=20001

client_sock = None
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind((ip, port))
server_sock.listen()

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
    client_sock, address = server_sock.accept()
    # res = client_sock.recv(1024)
    # result_socket_addr = pickle.loads(res)
    # raise Exception("Received result socket addr {}".format(result_socket_addr))
    # if not connect_timeout(result_sock, result_socket_addr):
    #     raise Exception("Worker was unable to connect to result socket")
    client_sock.sendall("ready to receive work:{}; boot time:{}".format(ready_time, boottime).encode())
    msg = client_sock.recv(1024)
    result_sock_address = pickle.loads(msg)
    result_sock.connect(result_sock_address)
    while True:
        reqbuf = client_sock.recv(2 ** 20)
        req = pickle.loads(reqbuf)
        tid = req["task_id"]
        buf = req["buffer"]
        client_sock.sendall("Received task {}; buff length {} and buf {}".format(tid, len(reqbuf), req).encode())
        if reqbuf == b"STOP":
            client_sock.sendall(b"terminating")
            client_sock.close()
            server_sock.close()
            os.system("reboot")
        if reqbuf == b"start":
            continue
        # In future surround the below in seperate try catches like process_worker_pool.py
        
        result = execute_task(buf)
        serialized_result = serialize(result, buffer_threshold=1000000)
        result_package = {'type': 'result', 'task_id': tid, 'result': serialized_result}
        res = pickle.dumps(result_package)
        #res = "Execute task: {}".format(result).encode()
        result_sock.sendall(res)
except Exception as e:
    msg = "DEAD: {} \ntraceback: {}".format(str(e), traceback.format_exc())
    result_sock.sendall(msg.encode())
    client_sock.sendall(msg.encode())
    server_sock.close()
    if client_sock:
        client_sock.close()
    os.system("reboot")
