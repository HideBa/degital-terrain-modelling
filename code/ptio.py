import laspy
import rasterio


def read_laz(file_path):
    with laspy.open(file_path, "r") as f:
        las = f.read()
        return las


def write_ras(file_path, profile, data):
    with rasterio.open(file_path, "w", **profile) as dst:
        dst.write(data, 1)
