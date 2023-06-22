#!/bin/bash
ip tuntap add tapvm1 mode tap
ip addr add 10.0.0.1/24 dev tapvm1
ip link set tapvm1 up
