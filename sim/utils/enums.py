from enum import Enum

class ObjState(Enum):
    """
    Is object (sensor, controller, robot) on, off, or in indeterminate state
    """
    OFF = 0
    ON = 1
    UNKNOWN = 2

class SensorType(Enum):
    """
    Type of sensor
    """
    UNKNOWN = 0
    BASIC = 1
    # ...

class MQTTPahoRC(Enum):
    """
    https://mntolia.com/sample-page/, add own RC after 5
    """
    SUCCESS = 0
    CONNECTION_REFUSED__INCORRECT_PROTOCOL = 1
    CONNECTION_REFUSED__INVALID_CLIENT_ID = 2
    CONNECTION_REFUSED__SERVER_UNAVAILABLE = 3
    CONNECTION_REFUSED__BAD_USERNAME_PASSWORD = 4
    CONNECTION_REFUSED__NOT_AUTHORIZED = 5
    PUBLISHER_NOT_CONNECTED = 6