import numpy as np
import rasterio
from ptio import write_ras
from startinpy import DT


class VegetationExtractor:
    def __init__(self, las, cluster_name="ClusterID"):
        self.las = las
        self.cluster_name = cluster_name
        self.veg_first_returns = None
        self.veg_dt = DT()

    def _find_trees(self, las, number_of_returns=3):
        trees = []
        clusters = np.unique(las.ClusterID)
        for cluster in clusters:
            cluster_points = las.points[las[self.cluster_name] == cluster]
            # count number of returns of points. If there is a point with more than 4 returns, it is a tree
            num_returns = np.unique(cluster_points["number_of_returns"])
            if np.any(num_returns > number_of_returns - 1):
                trees.append(cluster)
        return trees

    def _extract_first_returns(self, las):
        first_returns = las.points[las.return_number == 1]
        self.veg_first_returns = first_returns
        return first_returns

    def find_first_return_of_trees(self, number_of_returns=3):
        trees = self._find_trees(self.las, number_of_returns)
        first_returns = self._extract_first_returns(self.las)
        first_returns_of_trees = first_returns[
            np.isin(first_returns[self.cluster_name], trees)
        ]
        return first_returns_of_trees

    def rasterize(self, file_path, bbox, cell_size=0.5, nodata=-9999):
        grid_points = np.array(self._to_gridded_points(bbox, cell_size))
        raster_points = grid_points[:, :, 2]
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

    def _interolate(self, p):
        xyz_array = np.column_stack(
            (
                self.veg_first_returns.x,
                self.veg_first_returns.y,
                self.veg_first_returns.z,
            )
        )
        self.veg_dt.insert(xyz_array)
        return self.veg_dt.interpolate({"method": "Laplace"}, [[p[0], p[1]]])

    def _highest_veg_point_in_a_cell(self, cell_bbox):
        xyz_array = np.column_stack(
            (
                self.veg_first_returns.x,
                self.veg_first_returns.y,
                self.veg_first_returns.z,
            )
        )
        x_valid = (cell_bbox[0] <= xyz_array[:, 0]) & (cell_bbox[2] >= xyz_array[:, 0])
        y_valid = (cell_bbox[1] <= xyz_array[:, 1]) & (cell_bbox[3] >= xyz_array[:, 1])

        valid_indices = np.where(x_valid & y_valid)[0]
        points_in_cell = xyz_array[valid_indices]
        if len(points_in_cell) == 0:
            return None
        sorted_array = points_in_cell[points_in_cell[:, 2].argsort()]
        z_max_points = sorted_array[-1]
        return z_max_points[2]

    def _to_gridded_points(self, bbox, cell_size, nodata=-9999):  # meter
        rows = []
        y = bbox[1]
        while y < bbox[3]:
            cols = []
            x = bbox[0]
            while x < bbox[2]:
                # z = self._interolate([x, y])
                z = self._highest_veg_point_in_a_cell(
                    [x, y, x + cell_size, y + cell_size]
                )
                cols.append(
                    [x + (cell_size / 2), y + (cell_size / 2), z if z else nodata]
                )
                x += cell_size
            rows.append(cols)
            y += cell_size
        return rows
