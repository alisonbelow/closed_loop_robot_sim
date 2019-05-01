"""
Robot 
Functionality:
- Recieves periodidic move command from controller - callback to move command, move
- Moves from current position to new position with some random error in y direction
- Can be disabled
"""

import json
import random


from sim.infra.mqtt_subscriber import MQTTSubscriber
from sim.infra.topic_utils import ROBOT_MOVE
from sim.src.pose import Pose
from sim.utils.enums import MQTTPahoRC, ObjState

class Robot:
    # TODO move initializations out of __init__() 
    def __init__(self):
        self.state = ObjState.ON
        self.move_sub = MQTTSubscriber(ROBOT_MOVE)
        self.move_sub.subscribe_topic(self.move)
        self.pose = Pose()
    
    def move(self, client, userdata, message):
        """
        Callback for subscription to robot/move_command
        """
        msg = json.loads(message.payload.decode("utf-8")) 
        if self.state == ObjState.ON:
            move_pose = Pose(msg["move"]["x"], msg["move"]["y"], msg["move"]["z"]) 
            y = self._simulate_y_err(move_pose.y)
            self.pose = Pose(move_pose.x, y, move_pose.z)
            
    def disable(self):
        """
        Disable pubsub and turn off
        """
        self.state = ObjState.OFF
        self.move_sub.disconnect()
    
    def _simulate_y_err(self, y) -> float:
        """
        Return random value max +/-5% of input y value 20% of the time (negative 20% of time)
        Else, returns y
        """
        rand_max = 0.05 * y 
        rand_mult = 1 if random.random() < 0.8 else -1
        return y if (random.random() >= 0.2) else y + rand_mult * (rand_max * random.random())
    