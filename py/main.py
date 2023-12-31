import os
from ptio import read_laz
from point_cloud import GFTIN
from tin import TIN
import numpy as np


def create_dtm(input_file, output_file):
    las = read_laz(input_file)

    bbox = np.concatenate((las.header.mins, las.header.maxs))
    gftin = GFTIN(las, 100, las.xyz, bbox, False)
    gftin.write_tin_geojson("./py/data/out/gftin.geojson")
    ground_points = gftin.ground_filtering()

    # # Save ground_points to a text file
    # np.savetxt("./py/data/out/ground_points.txt", ground_points)

    # ground_points = np.loadtxt("./py/data/out/ground_points.txt")

    # write ground points to a file
    tin = TIN(ground_points)
    tin.save_geojson("./py/data/out/tin.geojson")
    tin.write_dtm(output_file)


if __name__ == "__main__":
    create_dtm(
        "./py/data/thinned.las",  # TODO: change later
        "./py/data/out/dtm.tif",
    )
