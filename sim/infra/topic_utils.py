"""
Utilities for MQTT
"""

from datetime import datetime

# General
DETECTION_SUFFIX = '/detection'
STATE_SUFFIX = '/state'

# Sensor topics
SENSOR_PREFIX = 'sensor/'
SENSOR_DETECTIONS = 'sensor/+/detection' 

# Robot topics
ROBOT_MOVE = 'robot/move_command'

# Controller topics
CONTROLLER_PREFIX = 'controller/'

# Generate timestamp in InfluxDB format
def gen_influxdb_time():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')