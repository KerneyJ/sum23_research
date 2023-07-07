#!/bin/bash
for i in $(seq 0 $(expr $1 - 1))
do
    ip tuntap add tapvm$i mode tap
    ip addr add 10.0.$i.1/24 dev tapvm$i
    ip link set tapvm$i up
done
