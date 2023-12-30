from ptio import read_laz
from point_cloud import GFTIN
from tin import TIN
import numpy as np


def create_dtm(input_file, output_file):
    las = read_laz(input_file)

    bbox = np.concatenate((las.header.mins, las.header.maxs))
    # print("bbox:", bbox)
    gftin = GFTIN(las, 100, las.points, bbox, False)

    ground_points = gftin.ground_filtering()

    # print static info of the point cloud
    print("ground points:", len(ground_points))
    print("ground points shape:", ground_points.shape)
    print("ground points dtype:", ground_points.dtype)

    # write ground points to a file
    tin = TIN(ground_points)
    tin.write_dtm(output_file)


if __name__ == "__main__":
    # path = (os.path.join(os.path.dirname(__file__), "data/thinned.las"),)
    # print("path---", path)
    # print("--------")
    # print("path1", os.path.dirname(__file__))
    # print("path2", os.path.abspath(__file__))
    # print("path3", os.path.dirname(os.path.abspath(__file__)))
    # print("path4", __file__)
    # print("path5", path)
    # print("--------")

    create_dtm(
        "./py/data/thinned.las",  # TODO: change later
        # path,
        "./data/out/dtm.tif",
    )
