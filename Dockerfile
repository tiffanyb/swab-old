FROM ubuntu:22.04
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        gz-harmonic \
        python3 \
        python3-gz-transport13 \
        python3-gz-msgs10 \
	qemu-system \
	x11vnc

RUN mkdir /app
WORKDIR /app
ADD --keep-git-dir=false https://github.com/px4/px4-gazebo-models.git /app/resources
ENV GZ_SIM_RESOURCE_PATH=/app/resources/worlds:/app/resources/models

COPY src /app/src 
COPY gdb_script /app/gdb_script
COPY entry.sh /app/entry.sh
COPY vis_start.sh /app/vis_start.sh
COPY server_start.sh /app/server_start.sh
COPY firmwareM4_executable.elf /app/firmwareM4_executable.elf

RUN ./entry.sh server stop
