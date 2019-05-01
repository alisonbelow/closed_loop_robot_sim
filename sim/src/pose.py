"""
Defines simple Pose class (3D coord) to be used for sim
"""

class Pose():
    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self.x = x
        self.y = y
        self.z = z

    # Define basic operators for Pose
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y  and self.z == other.z
    
    def __neq__(self, other):
        return self.x != other.x or self.y != other.y  or self.z != other.z          

    def __add__(self, other):
        return Pose(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Pose(self.x - other.x, self.y - other.y, self.z - other.z)

    def __str__(self):
        return "[{},{},{}]".format(self.x, self.y, self.z)
    