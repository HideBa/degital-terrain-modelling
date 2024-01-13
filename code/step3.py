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

    las = read_laz(input_file)
    las_info(las)
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

    # # write ground points to a file
    tin = TIN(ground_points)
    raster_bbox = [extent[0], extent[1], extent[3], extent[4]]
    tin.write_dtm(output_file, raster_bbox, 0.5)


if __name__ == "__main__":
    processed_file = preprocess(cfg.INPUT_LAS)
    output_filename = cfg.STEP3_OUTPUT
    create_dtm(processed_file, output_filename)
