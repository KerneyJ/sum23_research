# measure boottime for ubuntu
import socket
import os
import time
import threading
import httpx
import json

pwd = "/home/jamie/funcx_virtines_sum23/firecracker"
api_socket = f"{pwd}/firecracker.socket"
logfile = f"{pwd}/firecracker.log"

kernel = f"{pwd}/vmlinux-4.14-x86_64.bin" # for ubuntu -> "ub_vmlinux.bin"
kernel_boot_args="console=ttyS0 reboot=k panic=1 pci=off"

rootfs = f"{pwd}/parsl-alpine-rootfs.ext4" # for ubuntu -> "ubuntu-18.04.ext4"
fc_mac = "AA:FC:00:00:00:01" # for ubuntu ->"06:00:AC:10:00:02"
tap_dev="tapvm1" # for ubuntu -> "tap0"
guest_netdev = "eth0" # for ubuntu -> net1

#ip = "172.16.0.2" # for ubuntu
ip = "10.0.0.2" # alpine ip
port = 20001

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
transport = httpx.HTTPTransport(uds=api_socket)
client = httpx.Client(transport=transport)
stay_alive = True

def query():
    while stay_alive:
        s.sendto(b"hello", (ip, port))
        time.sleep(1)

#t = threading.Thread(target=query)
#t.start()

os.system(f"touch {logfile}") 
#os.system("echo 3 > /proc/sys/vm/drop_caches") # empty out buffer cache

data_startlog = {"log_path": logfile, "level": "Debug", "show_level": True, "show_log_origin": True}
data_addbootsource = {"kernel_image_path": kernel, "boot_args": kernel_boot_args}
data_setrootfs = {"drive_id": "rootfs", "path_on_host": rootfs, "is_root_device": True, "is_read_only": False}
data_setupnet = {"iface_id": guest_netdev, "guest_mac": fc_mac, "host_dev_name": tap_dev}
data_startinstance = {"action_type": "InstanceStart"}


# os.system("bash ./ub_launch.sh") # replace this with requests
client.put("http://localhost/logger", content=json.dumps(data_startlog).encode())
client.put("http://localhost/boot-source", content=json.dumps(data_addbootsource).encode())
client.put("http://localhost/drives/rootfs", content=json.dumps(data_setrootfs).encode())
client.put(f"http://localhost/network-interfaces/{guest_netdev}", content=json.dumps(data_setupnet).encode())
time.sleep(0.015)

start = time.time()
client.put("http://localhost/actions", content=json.dumps(data_startinstance).encode())

def connect_timeout(socket, i, p, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            socket.connect((i, p))
        except:
            continue

connect_timeout(s, ip, port)
data = s.recv(1024)
#data, addr = s.recvfrom(1024)
#stay_alive = False
end = float(data)

print(end - start - 2*0.015)
s.close()
