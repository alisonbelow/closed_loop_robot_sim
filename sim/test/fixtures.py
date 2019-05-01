import pytest

from sim.src.pose import Pose

""""
FakeRobot pytest fixture for testing BasicSensor
Need some sort of object with pose member variable of type Pose 
"""
class FakeRobot:
    def __init__(self, pose: Pose):
        self.pose = pose    

@pytest.fixture(scope='function')
def fake_robot() -> FakeRobot:
    return FakeRobot(Pose(5.0, 6.0, -3.2))
