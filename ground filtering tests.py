import numpy as np
import laspy
import math
from startinpy import DT

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2)

def read_laz_file(filepath):
    with laspy.open(filepath) as file:
        las = file.read()
        points = np.vstack((las.x, las.y, las.z)).transpose()
    return points

def select_lowest_points(points, grid_size):
    min_points = {} # Initializes an empty dictionary to store the minimum elevation points for each grid cell.
    for x, y, z in points: #Iterates over each point in the point cloud. Each point is represented by its x, y, z coordinates
        grid_x = int(x // grid_size) #Calculates the grid cell's x-coordinate by integer division of the point's x-coordinate by the grid size.
        grid_y = int(y // grid_size) #same but y
        key = (grid_x, grid_y) #Forms a tuple key representing the grid cell coordinates.
        if key not in min_points or min_points[key][2] > z: # Checks if the grid cell is not already in min_points or if the current point has a lower elevation than the stored point.
            min_points[key] = (x, y, z) # Updates the min_points dictionary with the current point, either because it's the first point in that cell or it has a lower elevation.
    return list(min_points.values()) #returns a list of the lowest points from each grid cell.


def create_initial_tin(points):
    tin = DT()
    tin.insert(points)
    return tin

def compute_geometric_properties(point, dt):
    # Find the closest point in the TIN to the given point
    closest_point_index = dt.closest_point(point.x, point.y) #Finds the closest point in the triangulation to the given point.
    if closest_point_index is None:
        return None, None #if closest point oenst exist return none

    # Get the incident triangles to the closest point
    incident_triangles = dt.incident_triangles_to_vertex(closest_point_index)

    if not incident_triangles:
        return None, None #if no triangle return none 

    triangle = incident_triangles[0]
    p0 = dt.get_point(triangle[0])
    p1 = dt.get_point(triangle[1])
    p2 = dt.get_point(triangle[2]) #get vertices of triangle

    vector1 = np.array([p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]])
    vector2 = np.array([p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]]) #Calculates two vectors from the triangle vertices for use in the cross product.
    normal_vector = np.cross(vector1, vector2) #normal vector calc

    point_vector = np.array([point.x - p0[0], point.y - p0[1], point.z - p0[2]]) # Creates a vector from a vertex of the triangle to the given point.
    d = np.abs(np.dot(point_vector, normal_vector)) / np.linalg.norm(normal_vector) #Calculates the perpendicular distance from the point to the triangle plane.

    vectors_to_point = [
        [point.x - p0[0], point.y - p0[1], point.z - p0[2]],
        [point.x - p1[0], point.y - p1[1], point.z - p1[2]],
        [point.x - p2[0], point.y - p2[1], point.z - p2[2]]
    ] #Constructs vectors from each triangle vertex to the point.
    largest_angle = 0 #Initializes the largest angle value.
    for v in vectors_to_point:
        angle = math.acos(np.dot(normal_vector, v) / (np.linalg.norm(normal_vector) * np.linalg.norm(v)))
        largest_angle = max(largest_angle, angle) #Calculates the angle between each vector and the normal vector, updates largest_angle if larger.

    return d, math.degrees(largest_angle)

def ground_test(d, largest_angle, d_max, alpha_max):
    return d < d_max and largest_angle < alpha_max

def update_tin_with_ground_points(point_cloud, initial_tin, d_max, alpha_max):
    tin = DT()
    # Insert points from initial_tin into the new tin object, skipping the infinite vertex
    for pt in initial_tin.points[1:]:
        tin.insert_one_pt(*pt) #Inserts each point into the new TIN object.

    for point in point_cloud:
        point_obj = Point(point[0], point[1], point[2]) #Creates a Point object from the current point in the point cloud.
        d, largest_angle = compute_geometric_properties(point_obj, tin) #Computes geometric properties for the point.
        if d is not None and largest_angle is not None: #Checks if the computed properties are valid.
            if ground_test(point_obj, d, largest_angle, d_max, alpha_max): #Applies the ground test to determine if the point is ground.
                tin.insert_one_pt((point[0], point[1], point[2])) #If the point passes the ground test, it's added to the TIN.

    return tin



# test usage
laz_file_path = 'LAS.las'  # Replace with the path to your LAZ file
point_cloud = read_laz_file(laz_file_path)
grid_size = 50  # Grid size, adjust as needed
selected_points = select_lowest_points(point_cloud, grid_size)
initial_tin = create_initial_tin(selected_points)
d_max = 10  # maximum allowed perpendicular distance
alpha_max = 45  # maximum allowed angle in degrees
final_tin = update_tin_with_ground_points(point_cloud, initial_tin, d_max, alpha_max)

