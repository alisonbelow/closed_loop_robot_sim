
# Design Decisions

## Language

Options: C++, Python, JS, Go **--> choose Python**  
Why?  
* Easiest to make prototype
* Easy to virtualize with environment and keep track of libraries used
* Testing = easy and no installation overhead like with Google Test
* Don't know Go/JS well enough to learn for project

## Environment

The prompt instructions said "include installation instructions for a vanilla OS". For my development purposes I am going to containerize the work so that the project can be run on my machine and on the reviewer's machine through Docker.  

Should involve only a local install of Docker, and then everything will be fully automated. Offers ability to run project as a whole, or to enter dev env and "play around" in Linux terminal to develop/test further. If time allows, will include installation script for dependencies for Linux OS (assuming Ubuntu/Debian enabled). Current con = takes a few minutes to build docker image.

I did not use the off-the-shelf Grafana or InfluxDB containers. This was done to demonstrate my ability to create docker environment/ability to install necessary dependencies. Especially with prototyping where the creation and slimming down of image is advantageous for time, I would use the general Grafana/InfluxDB containers.

## Communication/Messaging

REST, RPC, and Brokered messaging --> **choose brokered messaging**  
Why? 
* Applicable for IoT/large data streams with pubsub communications
* Can abstract away producers/consumers  
* Message broker can be used to feed information to database and to recieve information from data panel  
* Asynchronous communication = desired 

Resource: [REST vs RPC vs Brokered Messaging](https://medium.com/@natemurthy/rest-rpc-and-brokered-messaging-b775aeb0db3)

What type of pub/sub brokered messaging = what type of python microservice?
Some initial options considered: LCM, MQTT, Google Cloud Py pubsub, RabbitMQ = AMQP --> **chose MQTT**  
Why?  
* Easy-to-use documentation/python library 
* Can install local server for demonstration purposes (not secure, but can be made secure with [efforts](https://www.bevywise.com/blog/creating-ssl-certificate-secure-mqtt-communication/)
* LCM = used at work, a bit more overhead to work with but comes with tools for debugging, maybe should have been selected
* Never used GC - not going to try with this project

Resource: [Microservice guide](https://microservices.io/patterns/communication-style/messaging.html)  

## DB/Visualization

I am new to the world of time series databases and data visualization with tools, as explained during our interview. I did some quick research on the options listed in the prompt and saw that InfluxDB with Grafana or Chronograf (InfluxDB maker Grafana alternative) is a popular choice, so selected this.

This option was pretty much a shot in the dark, but turned out okay. I cannot figure out (1) how to automate visualization of the Grafana dashboard and DB setup and (2) how to make output persist with proper permissions in Docker.

## Sensor

Chose to get architecture working and not focus on sensor selection/simulation. The abstract `Sensor` class should be extended for these future sensors.