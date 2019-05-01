"""
Basic Sensor that will adhere to robot at end of end effector
Functionality:
- Placeholder sensor
- Will read position of where robot is in global frame (has knowledge of what robot connected to)
- Initially publishing sensor data, can be turned off/on via sensor/ID/state topic

Future features:
- Real sensor simulating real data
"""
import json
import threading
import time

from sim.src.pose import Pose
from sim.src.robot import Robot
from sim.src.sensor import Sensor

from sim.infra.mqtt_publisher import MQTTPublisher
from sim.infra.mqtt_subscriber import MQTTSubscriber
from sim.infra.topic_utils import SENSOR_PREFIX, STATE_SUFFIX, DETECTION_SUFFIX, gen_influxdb_time
from sim.utils.constants import BASIC_SENSOR_DETECTION_FREQ
from sim.utils.enums import MQTTPahoRC, ObjState, SensorType

class BasicSensor(Sensor):
    def __init__(self, robot, placement_pose, ID):
        super().__init__(robot, placement_pose, ID, SensorType.BASIC)
        self.state = ObjState.ON
        self.detection_topic = SENSOR_PREFIX + str(self.id) + DETECTION_SUFFIX
        self.detection_pub = MQTTPublisher(self.detection_topic)

        self.state_topic = SENSOR_PREFIX + str(self.id) + STATE_SUFFIX
        self.state_sub = MQTTSubscriber(self.state_topic)
        self.state_sub.subscribe_topic(self.control_state)
        
        self.disabled = False
    
    def disable(self):
        """
        Disable pubsub and turn off
        """
        self.disabled = True
        self.state = ObjState.OFF
        self.pub_thread.join()
        self.state_sub.disconnect()
        self.detection_pub.stop_publish()
        self.detection_pub.disconnect()
    
    def control_state(self, client, userdata, message):
        """
        Callback for subscription to sensor/ID/state
        """
        msg = json.loads(message.payload.decode("utf-8"))

        if ObjState(msg["control_state"]) == ObjState.ON:
            # Turn on and enable publisher
            self.state = ObjState.ON
            self.detection_pub.start_publish()
        elif ObjState(msg["control_state"]) == ObjState.OFF:
            # Turn off and disable publisher
            self.state = ObjState.OFF
            self.detection_pub.stop_publish()

    def operate(self):
        """
        Periodic publish operation
        """    
        self.disabled = False
        self.state = ObjState.ON
        self.pub_thread = threading.Thread(target=self._publish_thread)
        self.pub_thread.start()

    def _publish_thread(self):
        self.detection_pub.start_publish()
        period = 1.0 / BASIC_SENSOR_DETECTION_FREQ

        while not self.disabled:
            begin_time = time.time()
            self.detection_pub.publish_topic(self._detect_msg())
            # Sleep for remainder of loop
            time.sleep(period - (begin_time - time.time()))

    def _read(self) -> Pose:
        """
        Dummy function!!!! Returns current robot pose in global frame
        Should be simulated somehow as true sensor
        """
        return self.robot.pose
    
    def _detect_msg(self) -> str:
        """
        Creates message of detected sensor location (global frame currently)
        """
        sensor_pose = self._read()
        return json.dumps({"time": gen_influxdb_time(),
                           "detection": {"x": sensor_pose.x, "y": sensor_pose.y, "z": sensor_pose.z}})