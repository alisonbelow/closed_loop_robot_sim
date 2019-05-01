"""
Example 3D printing designs
"""

import math
import numpy as np
import matplotlib.pyplot as plt

from sim.src.pose import Pose

# Print circle max(z_range) high
def _draw_circle(radius, z_range):
    pts = []
    z = 1.0
    for z in z_range:
        for t in range(0, 360):
            t = math.radians(t)
            x = radius * math.cos(t) + 1.25 * radius
            y = radius * math.sin(t) + 1.25 * radius
            pts.append(Pose(x,y,z))
    return pts

# Print spiral increasing in height
# Reference for spiral pattern:
# https://gist.github.com/eliatlarge/d3d4cb8ba8f868bf640c3f6b1c6f30fd
def _draw_spiral(radius):
    pts = []
    dist = 0.0
    step = radius/360 
    res = 3 * radius
    t = 0.0
    z = 0.0
    
    while dist * math.hypot(math.cos(t), math.sin(t)) < radius:
        x = dist * math.cos(t) + 1.25 * radius
        y = dist * math.sin(t) + 1.25 * radius
        if (t % 360 == 0.0): z += 1
        pts.append(Pose(x,y,z))
        dist += step
        t += res
    return pts

FlatCircle = _draw_circle(2.0, range(0,1))
Circle2Rad = _draw_circle(2.0, range(0,5))
Circle4Rad = _draw_circle(4.0, range(0,5))
Circle8Rad = _draw_circle(8.0, range(0,5))
Circle16Rad = _draw_circle(16.0, range(0,5))
Spiral2Rad = _draw_spiral(2.0)
Spiral4Rad = _draw_spiral(4.0)
Spiral8Rad = _draw_spiral(8.0)
Spiral16Rad = _draw_spiral(16.0)