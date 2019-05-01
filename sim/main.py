"""
Main function for closed loop control robot simulation
Future features: 
    - use config file for sensor configuration and 3D print design inputs
"""

import signal
import time

from sim.src.robot import Robot
from sim.src.basic_sensor import BasicSensor
from sim.src.controller import Controller
from sim.src.db_writer import DBWriter
from sim.src.pose import Pose
from sim.utils.controller_commands import FlatCircle

# https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python
class SIGINT_handler():
    def __init__(self):
        self.SIGINT = False
    
    def signal_handler(self, signal, frame):
        print("CTRL+C pressed! Exiting.")
        self.SIGINT = True

def main():
    # Create robot, sensors, controller
    robot = Robot()
    basic_sensor = BasicSensor(robot, Pose(), 1)
    controller = Controller(robot, FlatCircle)
    db_writer = DBWriter()

    # Run sensors/controllers
    basic_sensor.operate()
    controller.operate()

    # Add Ctrl+C handler
    handler = SIGINT_handler()
    signal.signal(signal.SIGINT, handler.signal_handler)

    # Run until interrupt or print completed
    while True:
        if handler.SIGINT or controller.print_completed:
            break
    
    # Disable objects
    robot.disable()
    basic_sensor.disable()
    controller.disable()
    db_writer.disable()

if __name__ == "__main__":
    main()