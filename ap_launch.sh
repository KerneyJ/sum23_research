#!/bin/bash

API_SOCKET="./firecracker.socket"
LOGFILE="./firecracker.log"
KERNEL=$1
ROOTFS=$2
ARCH=$(uname -m)
UB_MAC="06:00:AC:10:00:02"
AP_MAC="AA:FC:00:00:00:01"
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
      \"host_dev_name\": \"tapvm1\"
    }"

sleep 0.015

curl -X PUT --unix-socket "${API_SOCKET}" \
    --data "{
        \"action_type\": \"InstanceStart\"
    }" \
    "http://localhost/actions"

