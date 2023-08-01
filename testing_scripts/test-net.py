import zmq
import time

def connect_timeout(socket, ip, port, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            socket.connect("tcp://{}:{}".format(ip, port))
            return True
        except:
            continue
    return False

context = zmq.Context()

ip = "10.0.0.1"
port = 30000

worker_sock = context.socket(zmq.REQ)
result_sock = context.socket(zmq.REP)
result_addr = "tcp://{}:{}".format(ip, port)
result_sock.bind(result_addr)

print("trying to connect")

if not connect_timeout(worker_sock, ip, port+1):
    print("unable to connect to socket")

worker_sock.send(result_addr.encode())
init_msg = worker_sock.recv()
print("received init message: {}".format(init_msg))
ack = result_sock.recv()
print("recvied result: {}".format(ack))
result_sock.send(b"ack")
