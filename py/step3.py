import os
from ptio import read_laz
from gftin import GFTIN
from preprocess import remove_outliers
from lasinfo import las_info
from tin import TIN
import numpy as np
import laspy

GFTIN_CELL_SIZE = 30  # meters


def create_dtm(
    input_file,
    output_file,
):
    las = read_laz(input_file)
    # las.add_extra_dim(
    #     laspy.ExtraBytesParams(
    #         name="is_ground",
    #         type=np.uint8,  # 0: not ground, 1: ground
    #     )
    # )
    # las.is_ground = np.zeros(len(las.points), dtype=np.uint8)

    # bbox = np.concatenate((las.header.mins, las.header.maxs))
    # gftin = GFTIN(las, GFTIN_CELL_SIZE, bbox)

    # gftin.write_tin_geojson("./py/data/out/debug/gftin.geojson")
    # ground_points = gftin.ground_filtering()

    # # # Save ground_points to a text file
    # np.savetxt("./py/data/out/debug/ground_points.txt", ground_points)

    ground_points = np.loadtxt("./py/data/out/debug/ground_points.txt")

    # write ground points to a file
    tin = TIN(ground_points)
    tin.save_geojson("./py/data/out/debug/tin.geojson")
    tin.write_dtm(output_file, 0.5)

    return las


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
