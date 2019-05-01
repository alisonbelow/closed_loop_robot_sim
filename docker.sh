#!/bin/bash 

REPO="relativity"
IMAGE="cl_robot"
TAG="0.1"

# Command to install docker
if [ "$1" == "install" ]
then
    # sudo apt-get remove docker docker-engine docker.io
    # sudo apt-get update
    # sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
    # curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    # sudo apt-key fingerprint 0EBFCD88
    # sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    # sudo apt-get update
    sudo apt-get install docker-ce
    sudo docker run hello-world

    # Add your user to docker group to use with non-sudo access
    # sudo groupadd docker
    # sudo usermod -aG docker $USER       
    
    echo "*****************************"
    echo "Please log in and out of your user account to use docker as a non-super user"
    echo "Then you can proceed with testing your docker install with the command:"
    echo "docker run hello-world"
    echo "*****************************"
    exit

# Command to build docker container
elif [ "$1" == "build" ]
then
    docker build --build-arg UID=$(id -u) \
                 --build-arg GID=$(id -g) \
                 --build-arg UNAME=$(id -un) \
                 --tag ${REPO}/${IMAGE}:${TAG} \
                 -f env/Dockerfile .
    exit
# Command to run container with entrypoint project.sh script
# TODO change this to running main.py/whatever to run whole stack
# Add $2 to add arg to run.sh script
elif [ "$1" == "run" ]
then
    docker run -it --entrypoint ./run.sh ${REPO}/${IMAGE}:${TAG}
    exit

# Command to run container with bash
elif [ "$1" == "bash" ]
then
    docker run \
               -it \
               -w $HOME \
               -v /tmp/.X11-unix:/tmp/.X11-unix \
               -v $(pwd)/../closed_loop_robot_sim:/home/$(id -un)/closed_loop_robot_sim \
               -p 3000:3000 -p 8888:8888 -p 8086:8086 \
               -p 1883:1883 -p 9001:9001 \
               -e INFLUXDB_DB=defaultdb \
               -e INFLUXDB_ADMIN_USER=admin \
               -e INFLUXDB_ADMIN_PASSWORD=adminpass \
               -e INFLUXDB_USER=user \
               -e INFLUXDB_USER_PASSWORD=userpass \
               -e PATH=$PATH:/home/$(id -un)/closed_loop_robot_sim \
               --volume /sys/fs/cgroup:/sys/fs/cgroup:ro \
               --volume $(pwd)/env/grafana/provisioning:/etc/grafana/provisioning \
               ${REPO}/${IMAGE}:${TAG} \
               bash

# Command to open another container attached to running container with bash
# Will attach to last open docker container
elif [ "$1" == "another" ]
then 
    docker exec -it `docker ps | grep ${REPO}/${IMAGE}:${TAG} | cut -d' ' -f1` /bin/bash

# Command to delete container
elif [ "$1" == "remove" ]
then
    docker rm $(docker stop $(docker ps -a -q --filter ancestor=${REPO}/${IMAGE}:${TAG} --format="{{.ID}}"))
    docker image rm ${REPO}/${IMAGE/}:${TAG}

# Default no arg or not recognized
else      
    echo "ERROR: Invalid argument supplied to script, must execute with 'build', 'run', 'remove', or 'bash'"
    exit
fi