# Relativity - Closed Loop Robot Control

## How to Setup Environment

Clone this repository onto a Linux system (Ubuntu). Enter the closed_loop_robot_sim directory.

```sh
cd path/to/cloned/directory/closed_loop_robot_sim
```

Robot simulation can be run in docker container. First, the user must install docker, or verify it is installed on your machine. To install execute the `docker.sh` script with the argument `install`. After the installation concludes log out of and into your user account to be able to use docker as a non-sudo user.

```sh
# To install docker
./docker.sh install

# To check if installed
docker --version
# Should output 'Docker version X.X.X, build XXX' if installed
```

Then, you can create the docker image that will be used to run the simulation. To do so, run the below command:

```sh 
# To build image, run script with argument install
./docker.sh build
```

NOTE: The first time you run this, it will take ~10 min to build the container. After the image is built is on your system, you can check for it by running the command:

```sh
docker images
# You should see output like:
# REPOSITORY            TAG     IMAGE ID    CREATED             SIZE
# relativity/cl_robot   0.1    ...         A few seconds ago   1.13 GB
```

You can remove this docker image from your computer with the command: `./docker.sh remove`  
You can run the docker container to an interactive terminal with the command `./docker.sh bash`  
You can attach to the running docker container by opening a new terminal window/tab with the command: `./docker.sh another`  

## How to Run

Open Grafana interface in Firefox or similar browser at `http://localhost:3000/`. It make take several refreshes to open.  
Robot sim will be running in the docker container, and information being sent to your local browser.  

Log into Grafana with username `admin` and password `admin`.  
Open the dashboard "Sensor Dashboard". Once logged in,this option should be available on the home page under 'Recently viewed dashboards'. 

```sh
cd path/to/cloned/directory
./docker.sh bash

# In docker container
./run.sh
```

## Testing

I did not unit test (lack of time), but I did write some pytest files to verify basic functionality of components and do integration testing for pub/sub.

All tests can be run in docker bash (`./docker.sh bash`) with the `pytest` command.

```sh
pytest test/infra/test_mqtt_wrappers.py     # Test test_mqtt_wrappers.py script
pytest -s test/infra/test_mqtt_wrappers.py  # Test test_mqtt_wrappers.py script with log output display
pytest -v test/infra/test_mqtt_wrappers.py  # Test test_mqtt_wrappers.py script with test summary output display
```

## To Do/Current Status

See docs/remaining_work.md

## Software Design diagram

TODO

## Troubleshooting

To check if Grafana server is running, execute command `sudo service grafana-server status` in docker terminal.  

To check if InfluxDB server is running, execute command `sudo service influxdb status` in docker terminal.  
Can also check server is active with command `curl -sl -I localhost:8086/ping`.

To check if Grafana server is running, execute command `sudo service mosquitto status` in docker terminal.  

To see all statuses, execute command `sudo service --status-all` in docker terminal.  
