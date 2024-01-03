import math
import numpy as np
from pyproj import Proj, Transformer
from startinpy import DT

from geojson import write_geojson


class GFTIN:
    def __init__(self, las, cell_size, bbox):
        if las is None:
            raise ValueError("las must not be None")
        self.las = las
        if cell_size <= 0:
            raise ValueError("cell_size must be positive")
        # if len(pts) == 0:
        #     raise ValueError("pts must not be empty")
        if len(bbox) != 6:
            raise ValueError("bbox must have 6 elements")
        self.cell_size = cell_size
        # self.points = pts  # las points
        self.bbox = bbox  # [minx, miny, minz, maxx, maxy, maxz]
        self.dt = DT()
        self._construct_initial_tin()

    # This function is for testing purpose only. The reason why statrinpy's write_geojson isn't used is because it doesn't support WGS84 coordinate system.
    def write_tin_geojson(self, file_path):
        # self.dt.write_geojson(file_path)
        source_crs = Proj(init="epsg:28992")
        destination_crs = Proj(init="epsg:4326")  # WGS84
        transformer = Transformer.from_proj(source_crs, destination_crs)
        reprojected_points = np.array(
            list(transformer.itransform(self.dt.points)), dtype=np.float64
        )
        write_geojson(file_path, reprojected_points)

    def ground_filtering(self, dist_threshold=5, max_angle=5):  # degree
        ground_points = np.empty((0, 3))
        points = self.las.points
        xyz_points = self.las.xyz
        for i, p in enumerate(xyz_points):
            try:
                tri = self.dt.locate(p)
            except Exception:
                print("point isn't inside of triangle")
                try:
                    nearest_point = self.dt.closest_point(p[0], p[1])
                    tri = self.dt.incident_triangles_to_vertex(nearest_point)[0]
                except Exception:
                    print("point isn't inside of triangle")

                    points.is_ground[i] = 0
                    continue
            # d is the intersection point of the triangle and the vertical line from p
            tri_vetecies = [self.dt.points[i] for i in tri]  # [[x, y, z]]
            d = self._intersection_point_of_triangle(tri_vetecies, p)
            dist = np.linalg.norm(p - d)
            if dist > dist_threshold:
                points.is_ground[i] = 0
                continue
            a, b, c = tri_vetecies
            angle_a_p = self._angle_between_two_vectors(a, d, p)
            angle_b_p = self._angle_between_two_vectors(b, d, p)
            angle_c_p = self._angle_between_two_vectors(c, d, p)
            if angle_a_p > max_angle or angle_b_p > max_angle or angle_c_p > max_angle:
                points.is_ground[i] = 0
                continue

            points.is_ground[i] = 1
            ground_points = np.vstack((ground_points, p))
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
        points = np.empty((0, 3))
        for row in cells:
            for cell in row:
                lowest_point = self._find_lowest_point_in_a_cell(
                    cell, 1
                )  # TODO configure this number later
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
