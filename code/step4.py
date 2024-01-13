import tempfile

from ptio import read_laz
from preprocess import preprocess, clip_pc
from pipeline import Pipeline
from lasinfo import las_info
from vegetation_ext import VegetationExtractor
import config as cfg


def extract_vegetation(input_path, output_path):
    with tempfile.NamedTemporaryFile(
        suffix=".las", delete=True, mode="w+t"
    ) as clip_tmp:
        las = read_laz(input_path)
        clip_pc(las, cfg.EXTENT)
        las.write(clip_tmp.name)
        with tempfile.NamedTemporaryFile(
            suffix=".las", delete=True, mode="w+t"
        ) as dbscan_tmp:
            tmp_path = dbscan_tmp.name
            pipeline = Pipeline(
                clip_tmp.name,
                tmp_path,
                ["ClusterID=uint16"],
            )
            pipeline.range().dbscan(6, 4).execute()
            las = read_laz(tmp_path)
            las_info(las)
            veg_extractor = VegetationExtractor(las)
            veg_extractor.find_first_return_of_trees(3)
            raster_bbox = [cfg.EXTENT[0], cfg.EXTENT[1], cfg.EXTENT[3], cfg.EXTENT[4]]
            veg_extractor.rasterize(output_path, raster_bbox, cell_size=0.5)


if __name__ == "__main__":
    processed_file = preprocess(cfg.INPUT_LAS)
    output_filename = cfg.STEP4_OUTPUT

    extract_vegetation(processed_file, output_filename)
