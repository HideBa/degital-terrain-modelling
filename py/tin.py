import math
import numpy as np
import rasterio
from ptio import write_ras
from startinpy import DT

from geojson import write_geojson


class TIN:
    def __init__(self, points, debug=False):
        self.points = points
        self.dt = DT()
        self.dt.insert(points)
        self.debug = debug

    def save_geojson(self, file_path):
        write_geojson(file_path, self.points, "epsg:28992", "epsg:4326")

    def _laplace_interpolate(self, p):
        true_interpolated_value = self.dt.interpolate(
            {"method": "Laplace"}, [[p[0], p[1]]]
        )
        return true_interpolated_value[0]
        # if np.isnan(true_interpolated_value[0]):
        #     print("true_interpolated_value is None, skip")
        #     return np.nan
        # # TODO: fix later
        # p = [p[0], p[1], 0.0]
        # p_index = self.dt.insert_one_pt(p[0], p[1], p[2])
        # if self.dt.is_vertex_convex_hull(p_index):  # impossible to interpolate
        #     self.dt.remove(p_index)
        #     return np.nan
        # triangles = self.dt.incident_triangles_to_vertex(p_index)

        # weight_z_pairs = []
        # for i, tri in enumerate(triangles):
        #     p0_i, p1_i, p2_i = tri
        #     p0, p1, p2 = (
        #         tuple(self.dt.points[p0_i]),
        #         tuple(self.dt.points[p1_i]),
        #         tuple(self.dt.points[p2_i]),
        #     )
        #     next_tri = triangles[(i + 1) % len(triangles)]
        #     p3_i, p4_i, p5_i = next_tri
        #     p3, p4, p5 = (
        #         tuple(self.dt.points[p3_i]),
        #         tuple(self.dt.points[p4_i]),
        #         tuple(self.dt.points[p5_i]),
        #     )

        #     common_points_indices = list(
        #         set([p0_i, p1_i, p2_i]).intersection(set([p3_i, p4_i, p5_i]))
        #     )
        #     cc1 = self._circimcircle_center(p0, p1, p2)
        #     cc2 = self._circimcircle_center(p3, p4, p5)
        #     if cc1 is None or cc2 is None:
        #         continue
        #     voronoi_edge_length = math.dist(cc1, cc2)
        #     edge = math.dist(
        #         self.dt.points[common_points_indices[0]],
        #         self.dt.points[common_points_indices[1]],
        #     )
        #     weight = voronoi_edge_length / edge
        #     common_points_indices.remove(p_index)
        #     z = self.dt.points[common_points_indices[0]][2]
        #     weight_z_pairs.append([weight, z])
        # interpolated_value = sum([w * z for w, z in weight_z_pairs]) / sum(
        #     [w for w, _ in weight_z_pairs]
        # )

        # self.dt.remove(p_index)
        # print("my implementation:", interpolated_value)
        # print("startin implementation:", true_interpolated_value[0])
        # print("diff:", interpolated_value - true_interpolated_value[0])
        # return true_interpolated_value[0]

    def _circimcircle_center(self, p0, p1, p2):
        ax, ay = p0[0], p0[1]
        bx, by = p1[0], p1[1]
        cx, cy = p2[0], p2[1]
        d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if d == 0:
            return None
        ux = (
            (ax**2 + ay**2) * (by - cy)
            + (bx**2 + by**2) * (cy - ay)
            + (cx**2 + cy**2) * (ay - by)
        ) / d
        uy = (
            (ax**2 + ay**2) * (cx - bx)
            + (bx**2 + by**2) * (ax - cx)
            + (cx**2 + cy**2) * (bx - ax)
        ) / d
        return [ux, uy]

    def to_gridded_points(self, cell_size):  # meter
        bbox = self.dt.get_bbox()  # [minx, miny, maxx, maxy]
        rows = []
        y = bbox[1]
        while y < bbox[3]:
            cols = []
            x = bbox[0]
            while x < bbox[2]:
                z = self._laplace_interpolate([x, y])
                cols.append([x + (cell_size / 2), y + (cell_size / 2), z])
                x += cell_size
            rows.append(cols)
            y += cell_size
        return rows

    def write_dtm(self, file_path, cell_size, nodata=-9999):
        grid_points = np.array(self.to_gridded_points(cell_size))
        raster_points = grid_points[:, :, 2]

        if self.debug:
            reshaped = grid_points.reshape(-1, 3)
            write_geojson("./py/data/out/debug/grid_points.geojson", reshaped)

        profile = {
            "driver": "GTiff",
            "dtype": "float32",
            "nodata": nodata,
            "height": raster_points.shape[0],
            "width": raster_points.shape[1],
            "count": 1,
            "crs": "EPSG:28992",
            "transform": rasterio.transform.from_origin(
                grid_points[0][0][0],
                grid_points[0][0][1],
                cell_size,
                -cell_size,  # Negative because the raster's origin is top-left
            ),
        }
        write_ras(file_path, profile, raster_points)
