#!/usr/bin/env python3
import time

print("Entered parsl script {}".format(time.time()))

import parsl
from parsl.config import Config
from parsl.executors import HighThroughputExecutor
from parsl.providers import LocalProvider
from parsl import python_app

singularity = HighThroughputExecutor(
    cores_per_worker=1,
    label="htex_container",
    max_workers=2,
    start_method="container",
    container_type="singularity",
    container_ip="10.0.0.1",
    container_img_path="/home/jamie/funcx_virtines_sum23/singularity/boot.sif",
    provider=LocalProvider(
        init_blocks=1,
        max_blocks=1,
        min_blocks=1,
        nodes_per_block=1,
    ),
)

docker = HighThroughputExecutor(
    cores_per_worker=1,
    label="htex_container",
    max_workers=2,
    start_method="container",
    container_type="docker",
    container_ip="10.0.0.1",
    container_img_path="jamie:test_app",
    provider=LocalProvider(
        init_blocks=1,
        max_blocks=1,
        min_blocks=1,
        nodes_per_block=1,
    ),
)

parsl.load(Config(
    executors=[docker]
))

@python_app
def inc(x):
    return x + 1

if __name__ == '__main__':
    futs = []
    for i in range(20):
        futs.append(inc(i))

    while len(futs) > 0:
        for f in futs:
            if f.done():
                print(f.result())
                futs.remove(f)
