import os

import numpy as np
import pdal
from ptio import read_laz


def remove_outliers(input_path, output_path, nb_neighbors=10, std_ratio=2.0):
    pipeline_setting = """
    [
        "{input}",
        {{
            "type": "filters.outlier",
            "method": "statistical",
            "mean_k": {nb_neighbors},
            "multiplier": {std_ratio}
        }},
        "{output}"
    ]
    """.format(
        input=input_path,
        output=output_path,
        nb_neighbors=nb_neighbors,
        std_ratio=std_ratio,
    )
    pipeline = pdal.Pipeline(pipeline_setting)
    pipeline.execute()


def clip_pc(las, bbox):  # bbox = [minx, miny, minz, maxx, maxy, maxz]
    x_invalid = (bbox[0] <= las.points.x) & (bbox[3] >= las.points.x)
    y_invalid = (bbox[1] <= las.points.y) & (bbox[4] >= las.points.y)
    z_invalid = (bbox[2] <= las.points.z) & (bbox[5] >= las.points.z)
    good_indices = np.where(x_invalid & y_invalid & z_invalid)[0]
    las.points = las.points[good_indices]


def nth_thinning(input_path, n, output_path):
    las = read_laz(input_path)
    valid_indices = np.array([i for i in range(len(las.points)) if i % n == 0])
    las.points = las.points[valid_indices]
    las.write(output_path)


def preprocess(original_filename):
    thinned_filename = f"{os.path.splitext(original_filename)[0]}_thinned.las"
    no_outlier_filename = f"{os.path.splitext(thinned_filename)[0]}_no_outliers.las"

    if not os.path.isfile(thinned_filename):
        nth_thinning(original_filename, 2, thinned_filename)
        print("===thinned file created===")
    if not os.path.isfile(no_outlier_filename):
        remove_outliers(thinned_filename, no_outlier_filename)
        print("===no outlier file created===")
    return no_outlier_filename
