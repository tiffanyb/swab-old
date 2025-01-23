#!/bin/bash

if [ "$1" = "gui" ]; then
	START='/app/vis_start.sh'
elif [ "$1" = "server" ]; then
	START='/app/server_start.sh'
else
	echo "No mode provided"
	exit 1;
fi


if [ "$2" = "emi" ]; then
	GDB="./gdb_script/emi_compass.py"
elif [ "$2" = "stop" ]; then
	GDB="./gdb_script/stop_rover.py"
elif [ "$2" = "tip" ]; then
	GDB="./gdb_script/tip_over.py"
else
	echo "No CPV provided"
	exit 1;
fi

$START /app/firmwareM4_executable.elf $GDB

