GFTIN_CELL_SIZE = 90  # meters

EXTENT = [
    188250.01,
    313992.0,
    145.82,
    188750.0,
    314492.0,
    196.6,
]  # [minx, miny, minz, maxx, maxy, maxz]
# xmin, xmax = np.min(xyz[:, 0]), np.max(xyz[:, 0]) to get extent
# ymin, ymax = np.min(xyz[:, 1]), np.max(xyz[:, 1])
# zmin, zmax = np.min(xyz[:, 2]), np.max(xyz[:, 2])

INPUT_LAS = "./data/input/69BZ2_19.las"
STEP3_OUTPUT = "./data/dtm.tiff"
STEP4_OUTPUT = "./data/step4.tiff"
STEP5_OUTPUT = "./data/chm.tiff"
BENCHMARK_OUT_DIR = "./data/figure"
DEBUG_DATA_DIR = "./data/debug"
