import json
import threading
import paho.mqtt.client as mqtt
import pytest
import time

from sim.infra.topic_utils import gen_influxdb_time
from sim.src.pose import Pose
from sim.src.basic_sensor import BasicSensor
from sim.test.fixtures import fake_robot
from sim.utils.constants import MOSQUITTO_PORT, MOSQUITTO_SERVER, MOSQUITTO_TIMEOUT, BASIC_SENSOR_DETECTION_FREQ
from sim.utils.enums import ObjState

SENSOR_ID = 4
TEST_DURATION = 2   # [s]
PUB_MSG_COUNT = 0

def test_basicSensor(fake_robot):
    """
    Tests basic sensor functionality:
    - sensor is able to publish robot information
    - sensor is able to recieve off commands and stop publishing
    - sensor is able to be turned back on and reassume publishing
    """
    def assert_rx_message(client, userdata, message):
        global PUB_MSG_COUNT
        PUB_MSG_COUNT += 1
        assert(message.payload.decode("utf-8") == DETECTION)

    global PUB_MSG_COUNT
    DETECTION_TOPIC = 'sensor/4/detection'
    
    DETECTION = json.dumps({
        "time": gen_influxdb_time(),
        "detection": {"x": 5.0, "y": 6.0, "z":-3.2}
    })
    STATE_TOPIC = 'sensor/4/state'
    STATE_ON = json.dumps({
        "time": gen_influxdb_time(),
        "control_state": ObjState.ON.value
    })
    STATE_OFF = json.dumps({ 
        "time": gen_influxdb_time(),
        "control_state": ObjState.OFF.value
    })

    # Create subscriber
    client = mqtt.Client()
    client.connect(MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT)
    client.on_message = assert_rx_message
    client.subscribe(DETECTION_TOPIC)
    client.loop_start()

    # Create sensor
    basic_sensor = BasicSensor(fake_robot, Pose(), SENSOR_ID)
    time.sleep(0.05)
    assert(basic_sensor.state == ObjState.ON)
    assert(basic_sensor.state_sub._connected == True)
    assert(basic_sensor.state_sub._subscribed == True)

    # Run for 2s
    basic_sensor.operate()
    time.sleep(TEST_DURATION)
    assert(basic_sensor.detection_pub._connected == True)
    assert(basic_sensor.detection_pub._publishing == True)
    
    # Turn off for 2s
    client.publish(STATE_TOPIC, STATE_OFF)
    time.sleep(TEST_DURATION)
    
    # Turn on for 2s
    client.publish(STATE_TOPIC, STATE_ON)
    time.sleep(TEST_DURATION)

    # Disconnect all
    basic_sensor.disable()
    client.loop_stop()
    client.disconnect()

    assert(PUB_MSG_COUNT == BASIC_SENSOR_DETECTION_FREQ * TEST_DURATION * 2)
