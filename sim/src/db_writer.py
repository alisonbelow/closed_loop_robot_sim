"""
Subscribes to all sensor detection topics and robot move commands
Saves sensor detection, every entry, with last known desired move position 
Time stamp = message timestamp from sensor data
"""
import json

from influxdb import InfluxDBClient
from sim.infra.mqtt_subscriber import MQTTSubscriber
from sim.infra.topic_utils import SENSOR_DETECTIONS, ROBOT_MOVE
from sim.src.pose import Pose
from sim.utils.constants import INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_USER, INFLUXDB_PW, INFLUXDB_DBNAME
from sim.utils.enums import ObjState

class DBWriter():
    def __init__(self, db=INFLUXDB_DBNAME):
        self.state = ObjState.ON
        self.connect_influxdb(db)
        self.sensor_sub = MQTTSubscriber(SENSOR_DETECTIONS)
        self.sensor_sub.subscribe_topic(self.handle_sensor_data)
        
        self.last_known_desired_pose = Pose()
        self.controller_sub = MQTTSubscriber(ROBOT_MOVE)
        self.controller_sub.subscribe_topic(self.handle_controller_data)

    def connect_influxdb(self, db_name):
        """
        Sets up connection to InfluxDB
        Creates database if doesn't exist
        """
        self.influxdb_client = InfluxDBClient(INFLUXDB_HOST, INFLUXDB_PORT,
                                              INFLUXDB_USER, INFLUXDB_PW,
                                              db_name)
        databases = self.influxdb_client.get_list_database()        
        if len(list(filter(lambda db: db['name'] == db_name, databases))) == 0:
            self.influxdb_client.create_database(db_name)
        self.influxdb_client.switch_database(db_name)

    def disable(self):
        self.state = ObjState.OFF
        self.disabled = True
        self.sensor_sub.disconnect()
        self.controller_sub.disconnect()

    def handle_sensor_data(self, client, userdata, message):
        """
        Callback for sensor data
        """
        msg = json.loads(message.payload.decode("utf-8"))
        self.influxdb_client.write_points(self._convert_to_influxdb_measurement(msg))

    def handle_controller_data(self, client, userdata, message):
        """
        Callback for controller data, update last known desired pose
        """
        msg = json.loads(message.payload.decode("utf-8"))
        self.last_known_desired_pose = Pose(msg["pose"]["x"], msg["pose"]["y"], msg["pose"]["z"])

    def _convert_to_influxdb_measurement(self, message):
        """
        Creates InfluxDB entry
        """
        return [
        {
            'measurement': "detection",
            'tags': {
                'source': "basic_sensor"
            },
            'time': message["time"],
            'fields': {
                "x": float(message["detection"]["x"]),
                "y": float(message["detection"]["y"]),
                "z": float(message["detection"]["z"])
            }        
        },
        {
            'measurement': "desired_pose",
            'tags': {
                'source': "controller"
            },
            'time': message["time"],
            'fields': {
                "x": float(self.last_known_desired_pose.x),
                "y": float(self.last_known_desired_pose.y),
                "z": float(self.last_known_desired_pose.z)
            }
        }]