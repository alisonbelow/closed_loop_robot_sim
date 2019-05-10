#!/bin/bash

INFLUXDB_VERSION=1.7.6
ENV CHRONOGRAF_VERSION=1.7.11
ENV GRAFANA_VERSION=6.1.4

sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
sudo apt-get -y update
sudo apt-get -y dist-upgrade

sudo apt-get -y --force-yes install \
        apt-utils \
        ca-certificates \
        curl \
        git \
        htop \
        libfontconfig \
        nano \
        net-tools \
        openssh-server \
        supervisor \
        wget \
        gnupg \
        sudo \
        build-essential python3.6 python3.6-dev python3-pip python3.6-venv \
        mosquitto mosquitto-clients

sudo curl -sL https://deb.nodesource.com/setup_10.x | bash -
sudo apt-get install -y nodejs
sudo mkdir -p /var/log/supervisor
sudo rm -rf .profile

# Install InfluxDB
wget https://dl.influxdata.com/influxdb/releases/influxdb_${INFLUXDB_VERSION}_amd64.deb
sudo dpkg -i influxdb_${INFLUXDB_VERSION}_amd64.deb && rm influxdb_${INFLUXDB_VERSION}_amd64.deb

# Install Chronograf
wget https://dl.influxdata.com/chronograf/releases/chronograf_${CHRONOGRAF_VERSION}_amd64.deb
sudo dpkg -i chronograf_${CHRONOGRAF_VERSION}_amd64.deb && rm chronograf_${CHRONOGRAF_VERSION}_amd64.deb

# Install Grafana
wget https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana_${GRAFANA_VERSION}_amd64.deb
sudo dpkg -i grafana_${GRAFANA_VERSION}_amd64.deb && rm grafana_${GRAFANA_VERSION}_amd64.deb

# Grafana and InfluxDB setup
sudo cp env/dep/grafana.ini /etc/grafana/grafana.ini
sudo cp env/dep/init.sh /etc/init.d/influxdb
sudo chmod +x /etc/init.d/influxdb

update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
update-alternatives --install /usr/bin/python python /usr/bin/python3.6 2 \
python -m pip install pip --upgrade 

cp env/dep/requirements.txt /home/${UNAME}/requirements.txt

export PATH=$PATH:${HOME}/.local/bin
export PYTHONPATH=$PYTHONPATH:${HOME}/.local/lib/python3.6/site-packages:${HOME}/.local/bin
python3.6 -m pip install pip --upgrade
python3.6 -m pip install --user -r ${HOME}/requirements.txt

sudo service grafana-server stop
sudo service grafana-server restart
sudo service influxdb start
sudo service mosquitto start