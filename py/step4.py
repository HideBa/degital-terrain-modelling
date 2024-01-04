import os

from ptio import read_laz
from preprocess import remove_outliers
import numpy as np
from pipeline import Pipeline
from lasinfo import las_info


def extract_vegetation(input_path, output_path):
    pipeline = Pipeline(
        input_path,
        output_path,
        ["ClusterID=uint16"],
    )
    pipeline.range().dbscan().execute()
    # pipeline.range().execute()

    las = read_laz(output_path)
    las_info(las)
    bbox = np.concatenate((las.header.mins, las.header.maxs))


if __name__ == "__main__":
    # check if there is a file without outliers
    if not os.path.isfile("./py/data/out/thinned_without_outliers.las"):
        remove_outliers(
            "./py/data/thinned.las",
            "./py/data/out/thinned_without_outliers.las",
        )

    extract_vegetation(
        "./py/data/out/thinned_without_outliers.las",  # TODO: change later
        "./py/data/out/chm.tiff",
    )
