#!/bin/bash

if [ "$1" = "emi" ]; then
	./vis_start.sh ./firmwareM4_executable.elf ./gdb_script/emi_compass.py
elif [ "$1" = "stop" ]; then
	./vis_start.sh ./firmwareM4_executable.elf ./gdb_script/stop_rover.py
elif [ "$1" = "tip" ]; then
	./vis_start.sh ./firmwareM4_executable.elf ./gdb_script/tip_over.py
else
	echo "No CPV provided"
fi
