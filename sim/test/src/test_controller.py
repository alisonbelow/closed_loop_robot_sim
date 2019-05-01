import json
import paho.mqtt.client as mqtt
import pytest
import time

from sim.infra.topic_utils import gen_influxdb_time, ROBOT_MOVE
from sim.src.controller import Controller
from sim.src.pose import Pose
from sim.test.fixtures import fake_robot
from sim.utils.constants import MOSQUITTO_PORT, MOSQUITTO_SERVER, MOSQUITTO_TIMEOUT
from sim.utils.controller_commands import FlatCircle
from sim.utils.enums import ObjState

TEST_DURATION = 2   # [s]

PUB_MSG_COUNT = 0
def test_controller_open_loop(fake_robot):
    """
    Tests controller functionality:
    - controller publishes robot move commands at 1 Hz
    """ 
    def assert_rx_message(client, userdata, message):
        global PUB_MSG_COUNT
        PUB_MSG_COUNT += 1
    
    global PUB_MSG_COUNT

    # Create subscriber
    client = mqtt.Client()
    client.connect(MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT)
    client.on_message = assert_rx_message
    client.subscribe(ROBOT_MOVE)
    client.loop_start()

    # Create controller
    controller = Controller(fake_robot, FlatCircle)
    time.sleep(0.05)
    assert(controller.state == ObjState.ON)
    assert(controller.state_sub._connected == True)
    assert(controller.state_sub._subscribed == True)

    # Run for 2s
    controller.operate()
    time.sleep(TEST_DURATION)
    assert(controller.move_pub._connected == True)
    assert(controller.move_pub._publishing == True)

    # Disconnect all
    controller.disable()
    client.loop_stop()
    client.disconnect()

    assert(PUB_MSG_COUNT == TEST_DURATION)

def test_controller_closed_loop(fake_robot):
    """
    Tests controller closed loop functionality:
    - controller publishes robot move commands at 1 Hz
    - controller is able to receive sensor input and correct the move commands to robot
    """ 
    def assert_rx_message(client, userdata, message):
        msg = json.loads(message.payload.decode("utf-8"))
        assert(msg["move"]["x"] % 1 == 0.5)
        assert(msg["move"]["y"] % 1 == 0.5)
        assert(msg["move"]["z"] % 1 == 0.5)
    
    SENSOR_TOPIC = 'sensor/4/detection'
    FAKE_ROBOT_LOC = json.dumps({ 
        "time": gen_influxdb_time(),
        "detection": {"x": 0.5, "y": 0.5, "z": 0.5}
    })
    MOVE_PLAN = [
        Pose(1.0, 1.0, 1.0),
        Pose(2.0, 2.0, 2.0),
        Pose(3.0, 3.0, 3.0),
        Pose(4.0, 4.0, 4.0),
        Pose(5.0, 5.0, 5.0)
    ]

     # Create subscriber
    client = mqtt.Client()
    client.connect(MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT)
    client.on_message = assert_rx_message
    client.subscribe(ROBOT_MOVE)
    client.loop_start()
    
    # Create controller
    controller = Controller(fake_robot, MOVE_PLAN)
    time.sleep(0.05)
    assert(controller.state == ObjState.ON)
    assert(controller.state_sub._connected == True)
    assert(controller.state_sub._subscribed == True)

    # Run for 2s
    controller.operate()
    client.publish(SENSOR_TOPIC, FAKE_ROBOT_LOC)
    client.publish(SENSOR_TOPIC, FAKE_ROBOT_LOC)
    client.publish(SENSOR_TOPIC, FAKE_ROBOT_LOC)
    time.sleep(TEST_DURATION)
    assert(controller.move_pub._connected == True)
    assert(controller.move_pub._publishing == True)

    # Disconnect all
    controller.disable()
    client.loop_stop()
    client.disconnect()

@pytest.mark.skip
def test_controller_state(fake_robot):
    """
    Tests controller closed loop functionality:
    - controller publishes robot move commands at 1 Hz
    - controller is able to receive sensor input and correct the move commands to robot
    - controller is able to be turned to/from closed loop control
    """ 
    def assert_rx_message(client, userdata, message):
        msg = json.loads(message.payload.decode("utf-8"))
        assert(msg["move"]["x"] % 1 == 0.0)
        assert(msg["move"]["y"] % 1 == 0.0)
        assert(msg["move"]["z"] % 1 == 0.0)
    
    SENSOR_TOPIC = 'sensor/4/detection'
    FAKE_ROBOT_LOC = json.dumps({ 
        "time": gen_influxdb_time(),
        "detection": {"x": 0.5, "y": 0.5, "z": 0.5}
    })
    FAKE_ROBOT_LOC2 = json.dumps({ 
        "time": gen_influxdb_time(),
        "detection": {"x": 1.0, "y": 1.0, "z": 1.0}
    })
    STATE_TOPIC = 'controller/state'
    STATE_ON = json.dumps({
        "time": gen_influxdb_time(),
        "control_state": ObjState.ON.value
    })
    STATE_OFF = json.dumps({ 
        "time": gen_influxdb_time(),
        "control_state": ObjState.OFF.value
    })
    MOVE_PLAN = [
        Pose(1.0, 1.0, 1.0),
        Pose(2.0, 2.0, 2.0),
        Pose(3.0, 3.0, 3.0),
        Pose(4.0, 4.0, 4.0),
        Pose(5.0, 5.0, 5.0)
    ]

     # Create subscriber
    client = mqtt.Client()
    client.connect(MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT)
    client.on_message = assert_rx_message
    client.subscribe(ROBOT_MOVE)
    client.loop_start()
    
    # Create controller
    controller = Controller(fake_robot, MOVE_PLAN)
    time.sleep(0.05)
    assert(controller.state == ObjState.ON)
    assert(controller.state_sub._connected == True)
    assert(controller.state_sub._subscribed == True)

    # Run for 2s with closed loop off
    controller.operate()
    client.publish(STATE_TOPIC, STATE_OFF)
    client.publish(SENSOR_TOPIC, FAKE_ROBOT_LOC)
    client.publish(SENSOR_TOPIC, FAKE_ROBOT_LOC)
    client.publish(SENSOR_TOPIC, FAKE_ROBOT_LOC)
    time.sleep(TEST_DURATION)
    assert(controller.move_pub._connected == True)
    assert(controller.move_pub._publishing == True)

    # Run for 2s with closed loop on 
    client.publish(STATE_TOPIC, STATE_ON)
    client.publish(SENSOR_TOPIC, FAKE_ROBOT_LOC2)
    client.publish(SENSOR_TOPIC, FAKE_ROBOT_LOC2)
    client.publish(SENSOR_TOPIC, FAKE_ROBOT_LOC2)
    time.sleep(TEST_DURATION)
    
    # Disconnect all
    controller.disable()
    client.loop_stop()
    client.disconnect()

MSG_COUNT = 0
@pytest.mark.skip
def test_controller_print_completes(fake_robot):
    """
    Tests controller finish print functionality
    """ 
    def assert_rx_message(client, userdata, message):
        global MSG_COUNT
        MSG_COUNT += 1
    
    global MSG_COUNT
    MOVE_PLAN = [
        Pose(1.0, 1.0, 1.0),
        Pose(2.0, 2.0, 2.0),
        Pose(3.0, 3.0, 3.0),
        Pose(4.0, 4.0, 4.0),
        Pose(5.0, 5.0, 5.0)
    ]

     # Create subscriber
    client = mqtt.Client()
    client.connect(MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT)
    client.on_message = assert_rx_message
    client.subscribe(ROBOT_MOVE)
    client.loop_start()
    
    # Create controller
    controller = Controller(fake_robot, MOVE_PLAN)
    time.sleep(0.05)
    assert(controller.state == ObjState.ON)
    assert(controller.state_sub._connected == True)
    assert(controller.state_sub._subscribed == True)

    # Run 
    controller.operate()
    time.sleep(len(MOVE_PLAN) * 1.5)
    assert(controller.disabled == True)
    assert(controller.move_pub._connected == True)
    assert(controller.move_pub._publishing == True)

    assert(MSG_COUNT == len(MOVE_PLAN))

    # Disconnect all
    controller.disable()
    client.loop_stop()
    client.disconnect()