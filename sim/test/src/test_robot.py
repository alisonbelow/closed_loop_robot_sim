import json
import paho.mqtt.client as mqtt
import pytest
import time

from sim.infra.topic_utils import ROBOT_MOVE, gen_influxdb_time
from sim.src.pose import Pose
from sim.src.robot import Robot
from sim.utils.constants import MOSQUITTO_PORT, MOSQUITTO_SERVER, MOSQUITTO_TIMEOUT
from sim.utils.enums import ObjState

def test_robot_verifyMoves():
    """
    Tests basic robot functionality:
    - robot updates pose when receives move command
    """
    pub = mqtt.Client()
    pub.connect(MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT)
    
    MOVE_DATA = json.dumps({
            "time": gen_influxdb_time(),
            "move": {"x": 2.0, "y": 4.0, "z": -1.5}, 
            "pose": {"x": 2.0, "y": 4.0, "z": -1.5}
        })

    robot = Robot()
    assert(robot.state == ObjState.ON)
    assert(robot.move_sub._connected)
    assert(robot.move_sub._subscribed)
    assert(robot.pose == Pose(0.0, 0.0, 0.0))

    pub.publish(ROBOT_MOVE, MOVE_DATA)
    time.sleep(0.05)

    assert(robot.pose.x == 2.0)
    assert(robot.pose.z == -1.5)
    y_lower_bounds = 0.95 * 4.0
    y_upper_bounds = 1.05 * 4.0
    assert(robot.pose.y >= y_lower_bounds and robot.pose.y <= y_upper_bounds)

    robot.disable()
    time.sleep(0.05)
    assert(robot.state == ObjState.OFF)
    assert(robot.move_sub._connected == False)
    assert(robot.move_sub._subscribed == False)
    pub.disconnect()
