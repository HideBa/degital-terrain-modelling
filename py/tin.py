import numpy as np
import rasterio
from ptio import write_ras
from startinpy import DT


class TIN:
    def __init__(self, points):
        self.points = points
        self.dt = DT()
        self.dt.insert(points)

    def save_geojson(self, file_path):
        self.dt.write_geojson(file_path)

    def _laplace_interpolate(self, p):
        # if not self.dt.is_inside_convex_hull(p[0], p[1]):
        #     return np.nan

        # tri = self.dt.locate(p)
        # p0, p1, p2 = self.dt.points[tri[0]], self.dt.points[tri[1]], self.dt.points[tri[2]]
        # TODO: fix later
        return self.dt.interpolate({"method": "Laplace"}, [[p[0], p[1]]])

    def to_gridded_points(self, cell_size):  # meter
        bbox = self.dt.get_bbox()  # [minx, miny, maxx, maxy]
        rows = []
        y = bbox[1]
        while y < bbox[3]:
            cols = []
            if y > bbox[3]:
                break
            x = bbox[0]
            while x < bbox[2]:
                if x > bbox[2]:
                    break
                z = self._laplace_interpolate([x, y])
                cols.append([x + (cell_size / 2), y + (cell_size / 2), z[0]])
                x += cell_size
            rows.append(cols)
            y += cell_size
        return rows

    def write_dtm(self, file_path):
        grid_points = np.array(self.to_gridded_points(0.5))
        # TODO: change profile later
        raster_points = grid_points[:, :, 2]
        profile = {
            "driver": "GTiff",
            "dtype": "float32",
            "nodata": -9999,
            "height": raster_points.shape[0],
            "width": raster_points.shape[1],
            "count": 1,
            "crs": "EPSG:28992",
            "transform": rasterio.transform.from_origin(  # type: ignore
                grid_points[0][0][0],
                grid_points[0][0][1],
                0.5,
                0.5,
            ),
        }
        write_ras(file_path, profile, raster_points)
