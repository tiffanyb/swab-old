# SWAB Alpha


## How to start

### Start through SACI
SCAI's dockerfile should already contain the command, so you just need to open the container through SCAI's web interface and see the simulation result.

The command SCAI is using is `./entry gui emi/stop/tip`, depending on which CPV you are trying to simulate.

### Start from terminal with GUI

If you want to directly use the container with GUI, you will need two steps:

1. set up VNC server and client

Create a container with forwarded port:

```bash
docker create -p 5900:5900 --name vnc -ti co_simulation
``` 

Inside the container, start the VNC service as a server: 
```bash
x11vnc -usepw -create -forever
```

Outside the container, you need a VNC viewer (e.g., VNC Viewer in Mac OS), and connect to `localhost:5900`, password: `1234`


2. Run scripts and Gazebo GUI

Outside the container: run `gz sim -g`, and you will see Gazebo GUI through the VNC session.

Inside the container: run `./entry.sh server emi/stop/tip`

You start to see simulation from the VNC client/viewer.

### Start from terminal without GUI

There are two ways:

  1. Inside the container: run `./entry.sh server emi/stop/tip`
  2. Outside the container: run `docker run -ti swab /app/entry.sh server emi/stop/tip`

You can observe the rover's movement by the tracker panel (second panel from the left) shown in the tmux session.

## How to develop and debug

I use the terminal + GUI option. In the topic tracking pane, I filtered the output to be r1\_rover specific using `grep -B 1 -A 13 "r1_rover"`.

## Known Issue

The tipover attack doesn't work as expected. This may because of the rover Gazebo model.

## Point of Contact

If you have more questions, you are welcome to contact Tiffany Bao, tbao@asu.edu
