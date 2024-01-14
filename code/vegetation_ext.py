import numpy as np
import rasterio
from ptio import write_ras
from startinpy import DT


class VegetationExtractor:
    """
    A class for extracting vegetation from a LAS file.

    Args:
        las (laspy.LASData): The laspy.LASData instance.
        cluster_name (str, optional): The name of the cluster attribute. Defaults to "ClusterID".

    Attributes:
        las (laspy.LASData): The laspy.LASData instance.
        cluster_name (str): The name of the cluster attribute.
        veg_first_returns (ndarray): Array of first return points of vegetation.
        veg_dt (DT): A Delaunay Triangulation object.

    Methods:
        _find_trees: Find the clusters that represent trees.
        _extract_first_returns: Extract the first return points from the LAS data
        find_first_return_of_trees: Find the first return points of trees.
        rasterize: Rasterize the vegetation points into a GeoTIFF file.
        _interpolate: Interpolate the elevation at a given point.
        _highest_veg_point_in_a_cell: Find the highest vegetation point in a cell.
        _to_gridded_points: Convert the bounding box into gridded points.

    """

    def __init__(self, las, cluster_name="ClusterID"):
        self.las = las
        self.cluster_name = cluster_name
        self.veg_first_returns = None
        self.veg_dt = DT()

    def _find_trees(self, las, number_of_returns=3):
        """
        Find the clusters that represent trees.

        Args:
            las (laspy.LASData): The laspy.LASData instance.
            number_of_returns (int, optional): The minimum number of returns for a point to be considered a tree. Defaults to 3.

        Returns:
            list: List of cluster IDs representing trees.

        """
        trees = []
        clusters = np.unique(las.ClusterID)
        for cluster in clusters:
            cluster_points = las.points[las[self.cluster_name] == cluster]
            num_returns = np.unique(cluster_points["number_of_returns"])
            if np.any(num_returns > number_of_returns - 1):
                trees.append(cluster)
        return trees

    def _extract_first_returns(self, las):
        """
        Extract the first return points from the LAS file.

        Args:
            las (laspy.LASData): The laspy.LASData instance.

        Returns:
            ndarray: Array of first return points.

        """
        first_returns = las.points[las.return_number == 1]
        self.veg_first_returns = first_returns
        return first_returns

    def find_first_return_of_trees(self, number_of_returns=3):
        """
        Find the first return points of trees.

        Args:
            number_of_returns (int, optional): The minimum number of returns for a point to be considered a tree. Defaults to 3.

        Returns:
            ndarray: Array of first return points of trees.

        """
        trees = self._find_trees(self.las, number_of_returns)
        first_returns = self._extract_first_returns(self.las)
        first_returns_of_trees = first_returns[
            np.isin(first_returns[self.cluster_name], trees)
        ]
        return first_returns_of_trees

    def rasterize(self, file_path, bbox, cell_size=0.5, nodata=-9999):
        """
        Rasterize the vegetation points into a GeoTIFF file.

        Args:
            file_path (str): The path to save the GeoTIFF file.
            bbox (list): The bounding box of the area of interest [xmin, ymin, xmax, ymax].
            cell_size (float, optional): The size of each cell in the raster grid. Defaults to 0.5.
            nodata (int, optional): The nodata value for the raster. Defaults to -9999.

        """
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
                -cell_size,
            ),
        }
        write_ras(file_path, profile, raster_points)

    def _interpolate(self, p):
        """
        Interpolate the elevation at a given point.

        Args:
            p (list): The coordinates [x, y] of the point.

        Returns:
            float: The interpolated elevation value.

        """
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
        """
        Find the highest vegetation point in a cell.

        Args:
            cell_bbox (list): The bounding box [xmin, ymin, xmax, ymax] of the cell.

        Returns:
            float: The elevation of the highest vegetation point in the cell.

        """
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

    def _to_gridded_points(self, bbox, cell_size, nodata=-9999):
        """
        Convert the bounding box into gridded points.

        Args:
            bbox (list): The bounding box [xmin, ymin, xmax, ymax].
            cell_size (float): The size of each cell in the grid.
            nodata (int, optional): The nodata value for the grid. Defaults to -9999.

        Returns:
            list: List of gridded points [[x, y, z], ...].

        """
        rows = []
        y = bbox[1]
        while y < bbox[3]:
            cols = []
            x = bbox[0]
            while x < bbox[2]:
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
