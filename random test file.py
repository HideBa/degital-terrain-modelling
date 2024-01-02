import numpy as np
import laspy
from startinpy import DT

def read_laz_file(filepath):
    with laspy.open(filepath) as file:
        las = file.read()
        points = np.vstack((las.x, las.y, las.z)).transpose()
    return points

def select_lowest_points(points, grid_size):
    min_points = {}
    for x, y, z in points:
        grid_x = int(x // grid_size)
        grid_y = int(y // grid_size)
        key = (grid_x, grid_y)
        if key not in min_points or min_points[key][2] > z:
            min_points[key] = (x, y, z)
    return list(min_points.values())

def create_initial_tin(points):
    tin = DT()
    tin.insert(points)
    return tin

# Example usage
laz_file_path = 'LAS.las'  # Replace with the path to your LAZ file
point_cloud = read_laz_file(laz_file_path)
grid_size = 50  # Grid size, adjust as needed
selected_points = select_lowest_points(point_cloud, grid_size)
initial_tin = create_initial_tin(selected_points)
