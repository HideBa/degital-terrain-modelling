import numpy as np
import rasterio


# TODO: debug why DTM and vegetation have different shape
def create_cms(dtm_filepath, vegetation_filepath, output_filepath, cell_size=0.5):
    # it expects dtm and vegetation file has same crs and resolution
    with rasterio.open(dtm_filepath) as dtm:
        dtm_data = dtm.read(1)
        dtm_nodata = dtm.nodata
        dtm_transform = dtm.transform
        dtm_bbox = dtm.bounds
        dtm_crs = dtm.crs
    with rasterio.open(vegetation_filepath) as vegetation:
        vegetation_data = vegetation.read(1)
        vegetation_nodata = vegetation.nodata
        vegetation_transform = vegetation.transform
        vegetation_bbox = vegetation.bounds
        vegetation_crs = vegetation.crs

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
                if chm < 0:
                    chm = 0
                chm_data[i][j] = chm

    # chm_data = dtm_data - vegetation_data
    # nodata value should be replaced with 0
    # chm_data[chm_data == dtm_nodata] = 0

    dtm_minx, dtm_miny, dtm_maxx, dtm_maxy = dtm_bbox
    (
        vegetation_minx,
        vegetation_miny,
        vegetation_maxx,
        vegetation_maxy,
    ) = vegetation_bbox

    minx = min(dtm_minx, vegetation_minx)
    miny = min(dtm_miny, vegetation_miny)
    maxx = max(dtm_maxx, vegetation_maxx)
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
    create_cms(
        "./py/data/out/dtm.tiff",
        "./py/data/out/vegetation.tiff",
        "./py/data/out/chm.tiff",
    )
