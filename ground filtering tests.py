import math
import numpy as np
import laspy
import startinpy

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2)

def ground_filtering(laz_file_path, d_max, alpha_max):
    dt = startinpy.DT()
    dt.read_las(laz_file_path)

    ground_points = []
    for i in range(dt.number_of_vertices()):
        point = Point(*dt.get_point(i))
        if ground_test(point, d_max, alpha_max, dt, i):
            ground_points.append(point)

    return ground_points

def ground_test(point, d_max, alpha_max, dt, point_index):
    d, alpha = compute_geometric_properties(point, dt, point_index)
    if d is not None and alpha is not None:
        return d <= d_max and alpha <= alpha_max
    return False

def compute_geometric_properties(point, dt, point_index):
    # Find the closest point in the TIN to the given point
    closest_point_index = dt.closest_point(point.x, point.y)
    if closest_point_index is None:
        return None, None

    # Get the incident triangles to the closest point
    incident_triangles = dt.incident_triangles_to_vertex(closest_point_index)

    if not incident_triangles:
        return None, None

    triangle = incident_triangles[0]
    p0 = dt.get_point(triangle[0])
    p1 = dt.get_point(triangle[1])
    p2 = dt.get_point(triangle[2])

    vector1 = np.array([p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]])
    vector2 = np.array([p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]])
    normal_vector = np.cross(vector1, vector2)

    point_vector = np.array([point.x - p0[0], point.y - p0[1], point.z - p0[2]])
    d = np.abs(np.dot(point_vector, normal_vector)) / np.linalg.norm(normal_vector)

    vectors_to_point = [
        [point.x - p0[0], point.y - p0[1], point.z - p0[2]],
        [point.x - p1[0], point.y - p1[1], point.z - p1[2]],
        [point.x - p2[0], point.y - p2[1], point.z - p2[2]]
    ]
    largest_angle = 0
    for v in vectors_to_point:
        angle = math.acos(np.dot(normal_vector, v) / (np.linalg.norm(normal_vector) * np.linalg.norm(v)))
        largest_angle = max(largest_angle, angle)

    return d, math.degrees(largest_angle)

def main():
    laz_file_path = "output_cropped_file.laz"
    d_max = 1.0
    alpha_max = 45
    ground_points = ground_filtering(laz_file_path, d_max, alpha_max)
    print(f"Number of ground points: {len(ground_points)}")

if __name__ == "__main__":
    main()
