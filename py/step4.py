import os
from ptio import read_laz
from preprocess import remove_outliers
import numpy as np

from lasinfo import las_info


def extract_veg(inputfile, outputfile):
    las = read_laz(inputfile)
    bbox = np.concatenate((las.header.mins, las.header.maxs))

    las_info(las)

    first_returns = las.points[las.points["return_num"] == 1]
    print("gps_time")
    print(first_returns["gps_time"][0])

    print("first returns:")
    print(len(first_returns))


if __name__ == "__main__":
    # check if there is a file without outliers
    if not os.path.isfile("./py/data/out/thinned_without_outliers.las"):
        remove_outliers(
            "./py/data/thinned.las",
            "./py/data/out/thinned_without_outliers.las",
        )

    extract_veg(
        "./py/data/out/thinned_without_outliers.las",  # TODO: change later
        "./py/data/out/chm.tiff",
    )
