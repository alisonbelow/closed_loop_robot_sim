"""
Controller 
Functionality:
- Periodidic move command sent to robot
- Subscriber to sensor(s) data
- Computes difference between desired robot position and sensor output
- Updates latest move command with this information
- Closed loop control portion can be turned on and off
- If open loop, will publish next move according to input design, not actual robot pose
- Closed loop initially enabled, can be controlled via controller/state topic

Future features:
- Input config for sensors and types, must be able to handle more
"""

import json
import threading
import time

from sim.src.pose import Pose
from sim.src.sensor import Sensor
from sim.src.robot import Robot

from sim.infra.mqtt_publisher import MQTTPublisher
from sim.infra.mqtt_subscriber import MQTTSubscriber
from sim.infra.topic_utils import SENSOR_DETECTIONS, STATE_SUFFIX, CONTROLLER_PREFIX, ROBOT_MOVE, gen_influxdb_time
from sim.utils.constants import MOVE_COMMAND_FREQ
from sim.utils.enums import MQTTPahoRC, ObjState, SensorType

class Controller:
    def __init__(self, robot, print_design):
        self.state = ObjState.ON

        self.sensor_sub = MQTTSubscriber(SENSOR_DETECTIONS)
        self.sensor_sub.subscribe_topic(self.handle_sensor_data)
        self.move_pub = MQTTPublisher(ROBOT_MOVE)
        self.state_sub = MQTTSubscriber(CONTROLLER_PREFIX + STATE_SUFFIX)
        self.state_sub.subscribe_topic(self.control_state)
        self.sensor_msg_count = 0
        self.sensor_msg_count_prev = 0

        self.closed_loop = True
        self.disabled = False

        self.print_design = print_design
        self.pattern_seq = 0
        self.print_completed = False

        self.robot_actual_pose = Pose()
        self.robot_previous_pose = Pose()
        self.robot_desired_pose = Pose()
        self.relative_move = Pose()
        
    def disable(self):
        """
        Disable pubsub and turn off
        """
        self.disabled = True
        self.state = ObjState.OFF
        self.pub_thread.join()
        self.move_pub.stop_publish()
        self.move_pub.disconnect()
        self.state_sub.disconnect()
        self.sensor_sub.disconnect()

    def control_state(self, client, userdata, message):
        """
        Callback for subscription to controller/state
        Turns closed loop correction of robot pose off
        Still allows periodic move commands to robot
        """
        msg = json.loads(message.payload.decode("utf-8"))

        if ObjState(msg["control_state"]) == ObjState.ON:
            self.closed_loop = True
        elif ObjState(msg["control_state"]) == ObjState.OFF:
            self.closed_loop = False

    def handle_sensor_data(self, client, userdata, message):
        """
        Callback for sensor data, given in global frame for basic_sensor currently
        """
        msg = json.loads(message.payload.decode("utf-8"))
        self.sensor_msg_count += 1
        self.robot_actual_pose = Pose(msg["detection"]["x"], msg["detection"]["y"], msg["detection"]["z"])

    def operate(self):
        """
        Operation of read cycle and publish cycle
        """    
        self.disabled = False
        self.state = ObjState.ON
        self.pub_thread = threading.Thread(target=self._publish_thread)
        self.pub_thread.start()

    def _publish_thread(self):
        self.move_pub.start_publish()
        period = 1.0 / MOVE_COMMAND_FREQ

        while not (self.disabled or self.print_completed):
            begin_time = time.time()
            # Compute next move from updated sensor info (or not), and publish
            self._compute_move_command()
            # Save how many sensor messages sent up to this time publishing
            self.sensor_msg_count_prev = self.sensor_msg_count
            self.move_pub.publish_topic(self._pose_msg())
            
            # Sleep for remainder of loop
            time.sleep(period - (begin_time - time.time()))        

        # Finished print 
        if self.print_completed:
            self.disable()    

    def _compute_move_command(self):
        """
        Computes the desired global coord and relative move command according to pattern
        """
        self.robot_desired_pose = self._get_next_pattern_location()
          
        # If open loop or no new sensor messages published since previous publish or no sensor messages
        if not self.closed_loop or self.sensor_msg_count == self.sensor_msg_count_prev:
            self.relative_move = self.robot_desired_pose - self.robot_previous_pose
        # If closed loop
        else:
            self.relative_move = self.robot_desired_pose - self.robot_actual_pose
    
        # Previous pose is now current target pose (should be where robot is moving )
        self.robot_previous_pose = self.robot_desired_pose

    def _get_next_pattern_location(self):
        """
        Returns next coord pair in pattern
        """
        next_move = self.print_design[self.pattern_seq] 
        self.pattern_seq += 1

        # End of desired controller pattern, ending
        if self.pattern_seq == len(self.print_design):
            self.print_completed = True
            return Pose(0.0,0.0,0.0)
            
        return next_move

    def _pose_msg(self) -> str:
        """
        Creates message of robot move command (relative) and desired end pose (global frame)
        """
        return json.dumps(
            {"time": gen_influxdb_time(),
             "move": {"x": self.relative_move.x, "y": self.relative_move.y, "z": self.relative_move.z}, 
             "pose": {"x": self.robot_desired_pose.x, "y": self.robot_desired_pose.y, "z": self.robot_desired_pose.z}}
        )