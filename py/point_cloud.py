import math
import numpy as np
from startinpy import DT


GFTIN_CELL_SIZE = 100  # meters


class GFTIN:
    def __init__(self, las, cell_size, pts, bbox, outliner_removal=True):
        self.las = las
        if cell_size <= 0:
            raise ValueError("cell_size must be positive")
        if len(pts) == 0:
            raise ValueError("pts must not be empty")
        if len(bbox) != 6:
            raise ValueError("bbox must have 6 elements")
        self.cell_size = cell_size
        self.points = pts  # numpy array
        self.bbox = bbox  # [minx, miny, minz, maxx, maxy, maxz]
        self.dt = DT()
        self._construct_initial_tin()
        # if outliner_removal:
        # TODO: remove outliners

    def ground_filtering(self, dist_threshold=0.5, max_angle=30):  # degree
        ground_points = np.array([])
        points = self.points
        for p in points:
            try:
                tri = self.dt.locate(p)
            except Exception:
                print("point isn't inside of triangle")
                nearest_point = self.dt.closest_point(p)
                tri = self.dt.incident_triangles_to_vertex(nearest_point)[0]
            # d is the intersection point of the triangle and the vertical line from p
            d = self._intersection_point_of_triangle(tri, p)
            dist = math.dist(p, d)
            if dist > dist_threshold:
                continue
            a, b, c = tri
            angle_a_p = self._angle_between_two_vectors(a, d, p)
            angle_b_p = self._angle_between_two_vectors(b, d, p)
            angle_c_p = self._angle_between_two_vectors(c, d, p)
            if angle_a_p > max_angle or angle_b_p > max_angle or angle_c_p > max_angle:
                continue
            ground_points = np.append(ground_points, p)
        return ground_points

    def _angle_between_two_vectors(self, a, b, c):
        ab = math.dist(a, b)
        ac = math.dist(a, c)
        cos_a = ab / ac
        a_rad = math.acos(cos_a)
        return math.degrees(a_rad)

    def _intersection_point_of_triangle(self, tri, p):
        a, b, c = tri
        ab = b - a
        ac = c - a
        n = np.cross(ab, ac)
        coefficient = -np.dot(n, a)  # plane equation coefficients

        if (
            abs(np.dot(n, p) + coefficient) < 1e-6
        ):  # TODO: check what epsion value is appropriate
            return n

        t = -(np.dot(n, p) + coefficient) / np.dot(n, n)
        d = p + t * n
        return d

    def _construct_initial_tin(self):
        points_for_tin = self._extreact_lowest_points()
        self.dt.insert(points_for_tin)

    def _extreact_lowest_points(self):
        cells = self._divide_extent_by_cell_size()
        # points is a list of laspy.points.PointFormat
        points = []
        for row in cells:
            for cell in row:
                lowest_point = self._find_lowest_point_in_a_cell(cell)
                points.extend(lowest_point)

        p = points[0]
        print(p)
        x = p.x
        print(x)
        # covert laspy.points.PointFormat to simple [x,y,z] array
        # TODO: start from here
        arr = []
        for i, p in enumerate(points):
            x = p.x
            y = p.y
            z = p.z
            print("x:", x)
            print("y:", y)
            print("z:", z)
            arr.append([p.x, p.y, p.z])

        points = np.array(arr)
        return arr

    def _find_lowest_point_in_a_cell(self, cell, num=1):
        cell_bbox = [
            cell[0] - (self.cell_size / 2),
            cell[1] - (self.cell_size / 2),
            cell[0] + (self.cell_size / 2),
            cell[1] + (self.cell_size / 2),
        ]  # [minx, miny, maxx, maxy]
        points = self.points
        x_valid = (cell_bbox[0] <= points.x) & (cell_bbox[2] >= points.x)
        y_valid = (cell_bbox[1] <= points.y) & (cell_bbox[3] >= points.y)

        valid_indices = np.where(x_valid & y_valid)[0]
        print("valid_indices:", valid_indices)
        points_in_cell = points[valid_indices]

        z_min_indices = np.argsort(points_in_cell.z)[-num:]

        min_points = points_in_cell[z_min_indices]
        return min_points

    def _divide_extent_by_cell_size(self):
        rows = []
        y = self.bbox[1]
        while y < self.bbox[4]:
            columns = []
            x = self.bbox[0]
            while x < self.bbox[3]:
                columns.append([x + (self.cell_size / 2), y + (self.cell_size / 2)])
                x += self.cell_size
            rows.append(columns)
            y += self.cell_size
        return rows


def ground_filtering_with_tin_refinement():
    pass


def find_lowest_point():
    pass


def outlier_removal():
    pass


def thinning():
    pass
