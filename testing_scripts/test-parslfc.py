#!/usr/bin/env python3
import time

print("Entered parsl script {}".format(time.time()))
import parsl
from parsl.config import Config
from parsl.executors import FirecrackerExecutor
from parsl.providers import LocalProvider
from parsl import python_app

executor = FirecrackerExecutor(
    fc_path="/home/jamie/funcx_virtines_sum23/firecracker/firecracker/build/cargo_target/x86_64-unknown-linux-musl/debug",
    unixsock_path="/home/jamie/funcx_virtines_sum23/firecracker/fc-logs",
    kernel_path="/home/jamie/funcx_virtines_sum23/firecracker/vmlinux-4.14-x86_64.bin",
    rootfs_path="/home/jamie/funcx_virtines_sum23/firecracker/fsimgs/py310-ttywriteable-rootfs.ext4",
    tap_dev="tapvm", 
    cores_per_worker=1,
    label="firecracker-executor",
    max_workers=1,
    worker_debug=True,
    provider=LocalProvider(
        init_blocks=1,
        max_blocks=1,
        min_blocks=1,
        nodes_per_block=1,
    ),
)

parsl.load(Config(
    executors=[executor]
))

@python_app
def your_mom(x):
    import time
    #time.sleep(0)
    return time.time()

if __name__=='__main__':
    futs = []
    for i in range(20):
        futs.append(your_mom(i))

    while len(futs) > 0:
        for f in futs:
            if f.done():
                print(f.result())
                futs.remove(f)
