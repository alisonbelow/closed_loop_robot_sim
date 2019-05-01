"""
Abstract class that will be used to define sensor
Funtionality:
- turn off/on
- abstract _read/detect function
- can update placement pose

Future features:
- Use placement pose to transform detected position to global or robot frame
"""
from abc import ABC, abstractmethod

from sim.src.pose import Pose
from sim.utils.enums import ObjState, SensorType 

class Sensor(ABC):
    @abstractmethod
    def __init__(self, robot, placement_pose: Pose, ID: int, sensor_type):
        self.robot = robot
        self.placement_pose = placement_pose
        self.state = ObjState.UNKNOWN
        self.type = sensor_type
        self.id = ID

    def sensor_type(self) -> SensorType:
        return self.type

    def update_pose(self, new_pose):
        self.placement_pose = new_pose

    @abstractmethod
    def _read(self):
        """
        Perform sensor reading, whatever that may be
        """
        pass
