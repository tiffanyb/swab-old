#!/bin/bash

if [ "$1" = "emi" ]; then
	/app/start.sh /app/firmwareM4_executable.elf /app/gdb_script/emi_compass.py
elif [ "$1" = "stop" ]; then
	/app/start.sh /app/firmwareM4_executable.elf /app/gdb_script/stop_rover.py
elif [ "$1" = "tip" ]; then
	/app/start.sh /app/firmwareM4_executable.elf /app/gdb_script/tip_over.py
else
	echo "No CPV provided"
fi
