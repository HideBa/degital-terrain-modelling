from ptio import read_laz
from gftin import GFTIN
from preprocess import clip_pc, preprocess
from lasinfo import las_info
from tin import TIN
import numpy as np
import config as cfg
import laspy


def create_dtm(
    input_file,
    output_file,
):
    las = read_laz(input_file)
    las_info(las)
    extent = cfg.EXTENT
    cell_size = cfg.GFTIN_CELL_SIZE
    buffered_extent = [
        extent[0] - cell_size * 2,
        extent[1] - cell_size * 2,
        extent[2],
        extent[3] + cell_size * 2,
        extent[4] + cell_size * 2,
        extent[5],
    ]
    clip_pc(las, buffered_extent)
    las.add_extra_dim(
        laspy.ExtraBytesParams(
            name="is_ground",
            type=np.uint8,  # 0: not ground, 1: ground
        )
    )
    las.is_ground = np.zeros(len(las.points), dtype=np.uint8)

    gftin = GFTIN(las, cfg.GFTIN_CELL_SIZE, extent, debug=True)

    ground_points = gftin.ground_filtering()

    # # Save ground_points to a text file
    # np.savetxt("./py/data/out/debug/ground_points.txt", ground_points)

    # ground_points = np.loadtxt("./py/data/out/debug/ground_points.txt")

    # # write ground points to a file
    tin = TIN(ground_points)
    bbox = cfg.EXTENT
    raster_bbox = [bbox[0], bbox[1], bbox[3], bbox[4]]
    tin.write_dtm(output_file, raster_bbox, 0.5)


if __name__ == "__main__":
    processed_file = preprocess("./py/data/69BZ2_19.las")
    output_filename = "./py/data/out/dtm.tiff"
    create_dtm(processed_file, output_filename)
