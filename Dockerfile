FROM ubuntu:22.04
# RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
#     DEBIAN_FRONTEND=noninteractive apt-get install -y \
#         gz-harmonic \
#         python3 \
#         python3-gz-transport13 \
#         python3-gz-msgs10 \
# 	qemu-system \
# 	x11vnc
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y curl lsb-release gnupg git tmux gdb qemu-system python3 python3-click python3-zmq && \
    curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y gz-harmonic

RUN mkdir /app
WORKDIR /app
ADD --keep-git-dir=false https://github.com/px4/px4-gazebo-models.git /app/resources
ENV GZ_SIM_RESOURCE_PATH=/app/resources/worlds:/app/resources/models

COPY src /app/src 
COPY gdb_script /app/gdb_script
COPY entry.sh /app/entry.sh
COPY vis_start.sh /app/vis_start.sh
COPY server_start.sh /app/server_start.sh
COPY firmwarem4_executable.elf /app/firmwareM4_executable.elf

RUN apt-get install -y gdb-multiarch
RUN mkdir -p /user/data
RUN echo 'alias firmware="python3 /app/src/publisher_firmware.py"' >> ~/.bashrc
RUN echo 'alias gdb="gdb-multiarch"' >> ~/.bashrc

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y x11vnc xvfb
# RUN x11vnc -usepw -create -forever

# CMD /bin/bash -c "/app/entry.sh server stop"
