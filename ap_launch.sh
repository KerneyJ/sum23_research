#!/bin/bash

WORKER=0
API_SOCKET="./fc-logs/firecracker-worker${WORKER}.socket"
LOGFILE="./fc-logs/firecracker-worker${WORKER}.log"
HOST_TAP_DEV="tapvm${WORKER}"
AP_MAC="AA:FC:00:00:00:0${WORKER}"
KERNEL=$1
ROOTFS=$2
ARCH=$(uname -m)

touch $LOGFILE
echo $KERNEL
echo $ROOTFS
curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"log_path\": \"${LOGFILE}\",
        \"level\": \"Debug\",
        \"show_level\": true,
        \"show_log_origin\": true
    }" \
    "http://localhost/logger"


curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"kernel_image_path\": \"${KERNEL}\",
        \"boot_args\": \"${KERNEL_BOOT_ARGS}\"
    }" \
    "http://localhost/boot-source"

curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"drive_id\": \"rootfs\",
        \"path_on_host\": \"${ROOTFS}\",
        \"is_root_device\": true,
        \"is_read_only\": false
    }" \
    "http://localhost/drives/rootfs"

sleep 0.015

curl --unix-socket ${API_SOCKET} \
    -X PUT "http://localhost/network-interfaces/eth0" \
    -H "accept:application/json" \
    -H "Content-Type:application/json" \
    -d "{
      \"iface_id\": \"eth0\",
      \"guest_mac\": \"${AP_MAC}\",
      \"host_dev_name\": \"${HOST_TAP_DEV}\"
    }"

sleep 0.015

curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"action_type\": \"InstanceStart\"
    }" \
    "http://localhost/actions"

