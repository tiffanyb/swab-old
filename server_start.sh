#!/bin/bash

export GZ_SIM_RESOURCE_PATH=/app/resources/models

FIRMWARE=$1
CPV=$2 # the gdb script for a particular CPV
# Name of the tmux session
SESSION_NAME="emi"

# Create a new tmux session
tmux new-session -d -s $SESSION_NAME

# Split the window into three panes
tmux split-window -h
tmux split-window -h
tmux split-window -h

tmux select-layout even-horizontal

COMM1="gz sim -s -r -v4 default.sdf"
COMM2="sleep 8 && firmware && gz topic -e -t /world/default/pose/info"
COMM3="qemu-system-arm -machine lm3s6965evb -cpu cortex-m4 -nographic -kernel $FIRMWARE -D /user/data/new_qemu.log.1 -d int,cpu_reset,guest_errors,unimp -gdb tcp::1234 -S"
# COMM4="gdb -q $FIRMWARE"
COMM4="gdb -nw -q -x $CPV $FIRMWARE"

# Send commands to each pane
tmux send-keys -t $SESSION_NAME:0.0 "$COMM1" C-m
tmux send-keys -t $SESSION_NAME:0.1 "$COMM2" C-m
tmux send-keys -t $SESSION_NAME:0.2 "$COMM3" C-m
tmux send-keys -t $SESSION_NAME:0.3 "$COMM4" C-m

# Attach to the session
tmux attach-session -t $SESSION_NAME
