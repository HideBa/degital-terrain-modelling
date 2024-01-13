import os
import numpy as np
import rasterio
from preprocess import preprocess
import config as cfg
import step3
import step4


# TODO: debug why DTM and vegetation have different shape
def create_chm(dtm_filepath, vegetation_filepath, output_filepath, cell_size=0.5):
    # it expects dtm and vegetation file has same crs and resolution
    with rasterio.open(dtm_filepath) as dtm:
        dtm_data = dtm.read(1)
        dtm_nodata = dtm.nodata
        dtm_transform = dtm.transform
        dtm_bbox = dtm.bounds
        dtm_crs = dtm.crs
    with rasterio.open(vegetation_filepath) as veg:
        vegetation_data = veg.read(1)
        vegetation_nodata = veg.nodata
        vegetation_transform = veg.transform
        vegetation_bbox = veg.bounds
        vegetation_crs = veg.crs

    chm_data = np.zeros(dtm_data.shape)
    for i in range(dtm_data.shape[0]):
        if vegetation_data.shape[0] <= i:
            break
        for j in range(dtm_data.shape[1]):
            if vegetation_data.shape[1] <= j:
                break
            if (
                dtm_data[i][j] != dtm_nodata
                and vegetation_data[i][j] != vegetation_nodata
            ):
                chm = vegetation_data[i][j] - dtm_data[i][j]
                if chm < 0:  # there is no minus since vegetation is higher than ground
                    chm = 0
                chm_data[i][j] = chm

    dtm_minx, dtm_miny, dtm_maxx, dtm_maxy = dtm_bbox
    (
        vegetation_minx,
        vegetation_miny,
        vegetation_maxx,
        vegetation_maxy,
    ) = vegetation_bbox

    minx = min(dtm_minx, vegetation_minx)
    maxy = max(dtm_maxy, vegetation_maxy)

    profile = {
        "driver": "GTiff",
        "dtype": chm_data.dtype,
        "nodata": dtm_nodata,
        "width": chm_data.shape[1],
        "height": chm_data.shape[0],
        "count": 1,
        "crs": dtm_crs,
        "transform": rasterio.transform.from_origin(minx, maxy, cell_size, -cell_size),
    }

    with rasterio.open(output_filepath, "w", **profile) as dst:
        dst.write(chm_data, 1)


if __name__ == "__main__":
    processed_file = preprocess(cfg.INPUT_LAS)
    if not os.path.isfile(cfg.STEP3_OUTPUT):
        step3.create_dtm(processed_file, cfg.STEP3_OUTPUT)
    if not os.path.isfile(cfg.STEP4_OUTPUT):
        step4.extract_vegetation(processed_file, cfg.STEP4_OUTPUT)

    create_chm(
        cfg.STEP3_OUTPUT,
        cfg.STEP4_OUTPUT,
        cfg.STEP5_OUTPUT,
    )
