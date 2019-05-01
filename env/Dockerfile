FROM ubuntu:16.04
LABEL maintainer="Alison Below <alisonbelow@gmail.com>"

# Default versions
ENV INFLUXDB_VERSION=1.7.6
ENV CHRONOGRAF_VERSION=1.7.11
ENV GRAFANA_VERSION=6.1.4

# Fix bad proxy issue
COPY env/dep/system/99fixbadproxy /etc/apt/apt.conf.d/99fixbadproxy

WORKDIR /root

# Install Grafana, InfluxDB, Chronograf, Mosquitto, Python3.6
# Source = https://hub.docker.com/r/philhawthorne/docker-influxdb-grafana/
RUN rm /var/lib/apt/lists/* -vf \
    # Base dependencies
    && apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:jonathonf/python-3.6 \
    && apt-add-repository ppa:mosquitto-dev/mosquitto-ppa \
    && apt-get -y update \
    && apt-get -y dist-upgrade \
    && apt-get -y --force-yes install \
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
        mosquitto mosquitto-clients \
    && curl -sL https://deb.nodesource.com/setup_10.x | bash - \
    && apt-get install -y nodejs \
    && mkdir -p /var/log/supervisor \
    && rm -rf .profile \
    # Install InfluxDB
    && wget https://dl.influxdata.com/influxdb/releases/influxdb_${INFLUXDB_VERSION}_amd64.deb \
    && dpkg -i influxdb_${INFLUXDB_VERSION}_amd64.deb && rm influxdb_${INFLUXDB_VERSION}_amd64.deb \
    # Install Chronograf
    && wget https://dl.influxdata.com/chronograf/releases/chronograf_${CHRONOGRAF_VERSION}_amd64.deb \
    && dpkg -i chronograf_${CHRONOGRAF_VERSION}_amd64.deb && rm chronograf_${CHRONOGRAF_VERSION}_amd64.deb \
    # Install Grafana
    && wget https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana_${GRAFANA_VERSION}_amd64.deb \
    && dpkg -i grafana_${GRAFANA_VERSION}_amd64.deb && rm grafana_${GRAFANA_VERSION}_amd64.deb \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Configure Grafana
COPY env/dep/grafana.ini /etc/grafana/grafana.ini

# Configure InfluxDB
COPY env/dep/init.sh /etc/init.d/influxdb
RUN sudo chmod +x /etc/init.d/influxdb

# Make python 3.5 default 
RUN update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.6 2 \
    && python -m pip install pip --upgrade 

# Create temp user (changes to actual user if build on Linux system) and give sudo permissions
# Make a home directory, create user testuser
ARG UID=1000
ARG GID=1000
ARG UNAME=testuser

# Create identical user in docker container, give sudo permission
RUN mkdir -p /home/${UNAME} && \
    echo "${UNAME}:x:${UID}:${GID}:${UNAME},,,:/home/${UNAME}:/bin/bash" >> /etc/passwd && \
    echo "${UNAME}:x:${UID}:" >> /etc/group && \
    echo "${UNAME} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/${UNAME} && \ 
    chmod 0440 /etc/sudoers.d/${UNAME} && \
    chown ${UID}:${GID} -R /home/${UNAME}

# Set up home environment
USER ${UNAME}
ENV HOME /home/${UNAME}

WORKDIR ${HOME}

# Install pip requirements, set python paths
COPY env/dep/requirements.txt /home/${UNAME}/requirements.txt
ENV PATH "$PATH:${HOME}/.local/bin"
ENV PYTHONPATH "$PYTHONPATH:${HOME}/.local/lib/python3.6/site-packages:${HOME}/.local/bin"
RUN python3.6 -m pip install pip --upgrade \ 
    && python3.6 -m pip install --user -r ${HOME}/requirements.txt

ENTRYPOINT sudo service grafana-server stop \
    && sudo service grafana-server restart \
    && sudo service influxdb start \
    && sudo service mosquitto start \
    && /bin/bash