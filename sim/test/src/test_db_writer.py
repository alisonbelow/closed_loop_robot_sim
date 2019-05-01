import json
import paho.mqtt.client as mqtt
import pytest
import time

from influxdb import InfluxDBClient
from sim.infra.topic_utils import ROBOT_MOVE, gen_influxdb_time
from sim.src.db_writer import DBWriter
from sim.utils.constants import INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_USER, INFLUXDB_PW,INFLUXDB_DBNAME, \
                                MOSQUITTO_PORT, MOSQUITTO_SERVER, MOSQUITTO_TIMEOUT
from sim.utils.enums import ObjState

TEST_DURATION = 2   # [s]

def test_db_write():
    TEST_MOCK_DB = 'testdb'

    SENSOR_TOPIC = 'sensor/4/detection'
    SENSOR_READING = json.dumps({ 
        "time": gen_influxdb_time(),
        "detection": {"x": 0.5, "y": 0.5, "z": 0.5}
    })
    SENSOR_X_QUERY = 'SELECT "x" FROM "detection"'
    SENSOR_Y_QUERY = 'SELECT "y" FROM "detection"'
    SENSOR_Z_QUERY = 'SELECT "z" FROM "detection"'

    MOVE_DATA = json.dumps({
        "time": gen_influxdb_time(),
        "move": {"x": 2.0, "y": 4.0, "z": -1.5}, 
        "pose": {"x": 2.0, "y": 4.0, "z": -1.5}
    })
    ROBOT_POSE_X_QUERY = 'SELECT "x" FROM "desired_pose"'
    ROBOT_POSE_Y_QUERY = 'SELECT "y" FROM "desired_pose"'
    ROBOT_POSE_Z_QUERY = 'SELECT "z" FROM "desired_pose"'

    # Create MQT client
    client = mqtt.Client()
    client.connect(MOSQUITTO_SERVER, MOSQUITTO_PORT, MOSQUITTO_TIMEOUT)

    # Create InfluxDB client
    influxdb_client = InfluxDBClient(INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_USER, INFLUXDB_PW, TEST_MOCK_DB)
    databases = influxdb_client.get_list_database()        
    # assert(len(list(filter(lambda db: db['name'] == TEST_MOCK_DB, databases))) == 0)
    
    # Create db_writer
    db_writer = DBWriter(TEST_MOCK_DB)
    time.sleep(0.05)
    assert(db_writer.state == ObjState.ON)
    assert(db_writer.sensor_sub._connected == True)
    assert(db_writer.sensor_sub._subscribed == True)
    assert(db_writer.controller_sub._connected == True)
    assert(db_writer.controller_sub._subscribed == True)

    # Publish info that should be written to db
    client.publish(ROBOT_MOVE, MOVE_DATA)
    client.publish(SENSOR_TOPIC, SENSOR_READING)
    
    time.sleep(0.25)

    # Query db and ensure info written
    influxdb_client.switch_database(TEST_MOCK_DB)

    sensor_result = influxdb_client.query(SENSOR_X_QUERY)
    sensor_result = influxdb_client.query(SENSOR_Y_QUERY)
    sensor_result = influxdb_client.query(SENSOR_Z_QUERY)

    pose_result = influxdb_client.query(ROBOT_POSE_X_QUERY)
    pose_result = influxdb_client.query(ROBOT_POSE_Y_QUERY)
    pose_result = influxdb_client.query(ROBOT_POSE_Z_QUERY)

    db_writer.disable()
    
    # Delete db for subsequent texting
    influxdb_client.drop_database(TEST_MOCK_DB  )