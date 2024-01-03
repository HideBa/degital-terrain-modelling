import os
from ptio import read_laz
from gftin import GFTIN
from preprocess import remove_outliers
from tin import TIN
import numpy as np

GFTIN_CELL_SIZE = 100  # meters


def create_dtm(
    input_file,
    output_file,
):
    # las = read_laz(input_file)

    # bbox = np.concatenate((las.header.mins, las.header.maxs))
    # gftin = GFTIN(las, GFTIN_CELL_SIZE, las.xyz, bbox)
    # gftin.write_tin_geojson("./py/data/out/debug/gftin.geojson")
    # ground_points = gftin.ground_filtering()

    # # Save ground_points to a text file
    # np.savetxt("./py/data/out/debug/ground_points.txt", ground_points)

    ground_points = np.loadtxt("./py/data/out/debug/ground_points.txt")

    # write ground points to a file
    tin = TIN(ground_points)
    tin.save_geojson("./py/data/out/debug/tin.geojson")
    tin.write_dtm(output_file)


if __name__ == "__main__":
    if not os.path.isfile("./py/data/out/thinned_without_outliers.las"):
        remove_outliers(
            "./py/data/thinned.las",
            "./py/data/out/thinned_without_outliers.las",
        )

    create_dtm(
        "./py/data/out/thinned_without_outliers.las",  # TODO: change later
        "./py/data/out/dtm.tiff",
    )
