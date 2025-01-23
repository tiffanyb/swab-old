#!/bin/bash

export GZ_SIM_RESOURCE_PATH=/app/resources/models
FIRMWARE=$1
CPV=$2 # the gdb script for a particular CPV

COMM1="gz sim -s -r -v4 default.sdf"
COMM2="sleep 8 && firmware && gz topic -e -t /world/default/pose/info"
#COMM3="qemu-system-arm -machine lm3s6965evb -cpu cortex-m4 -nographic -kernel $FIRMWARE -D /user/data/new_qemu.log.1 -d int,cpu_reset,guest_errors,unimp -gdb tcp::1234 -S"
## COMM4="gdb -q $FIRMWARE"
#COMM4="gdb -nw -q -x $CPV $FIRMWARE"

$COMM1 2>/dev/null &

sleep 8 && firmware

qemu-system-arm -machine lm3s6965evb -cpu cortex-m4 -nographic -kernel $FIRMWARE -D /user/data/new_qemu.log.1 -d int,cpu_reset,guest_errors,unimp -gdb tcp::1234 -S &

sleep 8 && gdb -nw -q -x $CPV $FIRMWARE


