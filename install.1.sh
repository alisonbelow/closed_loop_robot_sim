#!/bin/bash

sudo apt-get remove docker docker-engine docker.io
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install docker-ce

# Add your user to docker group to use with non-sudo access
sudo groupadd docker
sudo usermod -aG docker $USER       
sudo chown ${USER} /var/run/docker.sock

echo "*****************************"
echo "Please log out and back in"
echo "Then proceed with testing your docker install with the command:"
echo "docker run hello-world"
echo "*****************************"