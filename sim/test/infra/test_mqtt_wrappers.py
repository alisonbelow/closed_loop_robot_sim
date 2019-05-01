"""
Tests wrappers around Paho MQTT library
Requires active mosquitto server to be running
If get connection error result code, try 'sudo service mosquitto restart'

To test: pytest -s test_mqtt_wrappers.py
"""

import json
import paho.mqtt.client as mqtt
import pytest
import time
from sim.src.sensor import Sensor

from sim.infra.mqtt_publisher import MQTTPublisher
from sim.infra.mqtt_subscriber import MQTTSubscriber
from sim.utils.constants import MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT
from sim.utils.enums import MQTTPahoRC, ObjState

PUB_MSG_COUNT = 0
def test_simplePublisher():
    """
    Tests publisher wrapper with mqtt subscriber
    """
    def assert_rx_message(client, userdata, message):
        global PUB_MSG_COUNT
        PUB_MSG_COUNT += 1
        assert(message.payload.decode("utf-8") == DATA)

    global PUB_MSG_COUNT
    TOPIC = 'test/data'
    DATA = 'my message data here'
    
    simple_sub = mqtt.Client()
    simple_sub.on_message = assert_rx_message
    simple_sub.connect(MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT)
    simple_sub.subscribe(TOPIC)
    simple_sub.loop_start()
    
    time.sleep(0.05)

    pub = MQTTPublisher(TOPIC)
    pub.start_publish()
    assert(pub._connected == True)
    assert(pub._publishing == True)
    rc = pub.publish_topic(DATA)
    assert(rc == MQTTPahoRC.SUCCESS)
    pub.stop_publish()
    assert(pub._connected == True)
    assert(pub._publishing == False)
    pub.disconnect()
    assert(pub._connected == False)
    assert(pub._publishing == False)
    simple_sub.disconnect()
    simple_sub.loop_stop()

    assert(PUB_MSG_COUNT == 1)

SUB_MSG_COUNT = 0
def test_simpleSubscriber():
    """
    Tests subscriber wrapper with mqtt publishers
    """
    def assert_rx_message(client, userdata, message):
        global SUB_MSG_COUNT
        SUB_MSG_COUNT += 1
        assert(message.payload.decode("utf-8") == DATA)

    global SUB_MSG_COUNT
    TOPIC = 'test/data'
    DATA = 'my message data here'
    simple_pub = mqtt.Client()
    simple_pub.connect(MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT)

    sub = MQTTSubscriber(TOPIC)
    assert(sub._connected == False)
    assert(sub._subscribed == False)
    sub.subscribe_topic(assert_rx_message)
    assert(sub._connected == True)
    assert(sub._subscribed == True)
    time.sleep(0.05)
    simple_pub.publish(TOPIC, DATA)

    sub.unsubscribe()
    assert(sub._connected == True)
    assert(sub._subscribed == False)
    simple_pub.publish(TOPIC, DATA)
    sub.resubscribe()
    assert(sub._connected == True)
    assert(sub._subscribed == True)

    sub.disconnect()
    time.sleep(0.01)
    assert(sub._connected == False)
    assert(sub._subscribed == False)
    simple_pub.disconnect()
    assert(SUB_MSG_COUNT == 1)

JSON_MSG_COUNT = 0
def test_sendJSON():
    """
    Tests subscriber and publisher wrapper with JSON messages
    """
    def assert_rx_message(client, userdata, message):
        global JSON_MSG_COUNT
        JSON_MSG_COUNT += 1
        jsonifyed = json.loads(message.payload.decode("utf-8")) 
        assert(jsonifyed == DATA)
        assert(ObjState(jsonifyed["state"]) == ObjState.ON)

    global JSON_MSG_COUNT
    TOPIC = 'test/json'
    DATA = {"sensor": "basic sensor", "id": 4, "state": ObjState.ON.value}

    pub = MQTTPublisher(TOPIC)
    pub.start_publish()
    
    sub = MQTTSubscriber(TOPIC)
    sub.subscribe_topic(assert_rx_message)
    time.sleep(0.025)

    rc = pub.publish_topic(json.dumps(DATA))
    assert(rc == MQTTPahoRC.SUCCESS)
    time.sleep(0.025)

    pub.disconnect()
    sub.disconnect()    
    assert(JSON_MSG_COUNT == 1)

