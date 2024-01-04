import os
import tempfile

from ptio import read_laz
from preprocess import remove_outliers
import numpy as np
from pipeline import Pipeline
from lasinfo import las_info
from vegetation_ext import VegetationExtractor


def extract_vegetation(input_path, output_path):
    path = "./py/data/out/debug/dbscan.las"
    pipeline = Pipeline(
        input_path,
        path,
        ["ClusterID=uint16"],
    )
    pipeline.range().dbscan().execute()

    las = read_laz(path)
    las_info(las)
    veg_extractor = VegetationExtractor(las)
    veg_extractor.find_first_return_of_trees(3)
    veg_extractor.rasterize(output_path, cell_size=0.5)


# with tempfile.NamedTemporaryFile(suffix=".las", delete=True, mode="w+t") as tmp:
#     tmp_path = tmp.name
#     pipeline = Pipeline(
#         input_path,
#         tmp_path,
#         ["ClusterID=uint16"],
#     )
#     pipeline.range().dbscan().execute()

#     las = read_laz(tmp_path)
#     las_info(las)
#     veg_extractor = VegetationExtractor(las)
#     veg_extractor.find_first_return_of_trees(3)
#     veg_extractor.rasterize(output_path, cell_size=5)


if __name__ == "__main__":
    # check if there is a file without outliers
    if not os.path.isfile("./py/data/out/thinned_without_outliers.las"):
        remove_outliers(
            "./py/data/thinned.las",
            "./py/data/out/thinned_without_outliers.las",
        )

    extract_vegetation(
        "./py/data/out/thinned_without_outliers.las",  # TODO: change later
        "./py/data/out/vegetation.tiff",
    )
