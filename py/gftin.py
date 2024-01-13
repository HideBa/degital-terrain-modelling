import math
import numpy as np
from startinpy import DT

from geojson import transform_points, write_geojson


class GFTIN:
    def __init__(self, las, cell_size, bbox, debug=False):
        if las is None:
            raise ValueError("las must not be None")
        self.las = las
        if cell_size <= 0:
            raise ValueError("cell_size must be positive")
        if len(bbox) != 6:
            raise ValueError("bbox must have 6 elements")
        self.cell_size = cell_size
        self.bbox = bbox  # [minx, miny, minz, maxx, maxy, maxz]
        self.dt = DT()
        self.debug = debug
        self._construct_initial_tin()
        self.write_tin_geojson("./py/data/out/debug/startin.geojson")

    # This function is for testing purpose only. The reason why statrinpy's write_geojson isn't used is because it doesn't support WGS84 coordinate system.
    def write_tin_geojson(self, file_path):
        # points = self.dt.points
        # triangles = [
        #     [points[i], points[j], points[k]] for i, j, k in self.dt.get_triangles()
        # ]
        # points = transform_points(points, "epsg:28992", "epsg:4326")
        # triangles = transform_points(triangles, "epsg:28992", "epsg:4326")
        write_geojson(
            file_path,
            self.dt.points,
            "epsg:28992",
            "epsg:4326",
        )

    def ground_filtering(self, dist_threshold=5, max_angle=30):  # degree
        points = self.las.points[self.point_indices_in_bbox()]
        xyz_points = self.las.xyz[self.point_indices_in_bbox()]
        print("gftin number of poinsts: ", len(points))
        for i, p in enumerate(xyz_points):
            try:
                tri = self.dt.locate(p[0], p[1])
            except Exception:
                try:
                    nearest_point = self.dt.closest_point([p[0], p[1]])
                    tri = self.dt.incident_triangles_to_vertex(nearest_point)[0]
                except Exception:
                    print("Warning!!!!!!!!!!!!")

                    points.is_ground[i] = 0
                    continue
                print("point isn't inside of triangle")
                points.is_ground[i] = 0
                continue
            # d is the intersection point of the triangle and the vertical line from p
            tri_vetecies = [self.dt.points[i] for i in tri]  # [[x, y, z]]
            d = self._intersection_point_of_triangle(tri_vetecies, [p[0], p[1], p[2]])
            dist = np.linalg.norm([p[0], p[1], p[2]] - d)
            if dist > dist_threshold:
                points.is_ground[i] = 0
                continue
            a, b, c = tri_vetecies
            angle_a_p = self._angle_between_two_vectors(a, d, [p[0], p[1], p[2]])
            angle_b_p = self._angle_between_two_vectors(b, d, [p[0], p[1], p[2]])
            angle_c_p = self._angle_between_two_vectors(c, d, [p[0], p[1], p[2]])
            if angle_a_p > max_angle or angle_b_p > max_angle or angle_c_p > max_angle:
                points.is_ground[i] = 0
                continue
            points.is_ground[i] = 1
        ground_points_indices = np.where(points.is_ground == 1)[0]
        ground_points = xyz_points[ground_points_indices]
        self.las.points = points
        return ground_points

    def _angle_between_two_vectors(self, a, b, c):
        ab = math.dist(a, b)
        ac = math.dist(a, c)
        if ab == 0 or ac == 0:
            return 0
        cos_a = ab / ac

        # To prevent math domain error. This is because of the floating point error.
        if 1 < cos_a < 1 + 1e-6:
            cos_a = 1
        elif -1 - 1e-6 < cos_a < -1:
            cos_a = -1
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
        # TODO: check if d is inside of triangle
        return d

    def _construct_initial_tin(self):
        points_for_tin = self._extract_lowest_points()
        self.dt.insert(points_for_tin)

    def _extract_lowest_points(self):
        cells = self._divide_extent_by_cell_size()
        reshaped_cell = np.array(cells).reshape(-1, 2)

        if self.debug is True:
            write_geojson(
                "./py/data/out/debug/cells.geojson",
                reshaped_cell,
                "epsg:28992",
                "epsg:4326",
            )

        points = np.empty((0, 3))
        for row in cells:
            for cell in row:
                lowest_point = self._find_lowest_point_in_a_cell(cell, 1)
                points = np.vstack((points, lowest_point))
        return points

    def _find_lowest_point_in_a_cell(self, cell, num=1):
        cell_bbox = [
            cell[0] - (self.cell_size / 2),
            cell[1] - (self.cell_size / 2),
            cell[0] + (self.cell_size / 2),
            cell[1] + (self.cell_size / 2),
        ]  # [minx, miny, maxx, maxy]
        points = self.las.xyz
        x_valid = (cell_bbox[0] <= points[:, 0]) & (cell_bbox[2] >= points[:, 0])
        y_valid = (cell_bbox[1] <= points[:, 1]) & (cell_bbox[3] >= points[:, 1])

        valid_indices = np.where(x_valid & y_valid)[0]
        points_in_cell = points[valid_indices]
        sorted_array = points_in_cell[points_in_cell[:, 2].argsort()]
        z_min_points = sorted_array[:num]
        return z_min_points

    def _divide_extent_by_cell_size(self):
        rows = []
        y = (
            self.bbox[1] - self.cell_size * 2
        )  # this is to have buffer so that all points have a triangle below them
        while y < self.bbox[4] + self.cell_size * 2:
            columns = []
            x = self.bbox[0] - self.cell_size * 2
            while x < self.bbox[3] + self.cell_size * 2:
                columns.append([x + (self.cell_size / 2), y + (self.cell_size / 2)])
                x += self.cell_size
            rows.append(columns)
            y += self.cell_size
        return rows

    def point_indices_in_bbox(self):
        points = self.las.points
        x_valid = (self.bbox[0] <= points.x) & (self.bbox[3] >= points.x)
        y_valid = (self.bbox[1] <= points.y) & (self.bbox[4] >= points.y)
        z_valid = (self.bbox[2] <= points.z) & (self.bbox[5] >= points.z)
        valid_indices = np.where(x_valid & y_valid & z_valid)[0]
        return valid_indices
