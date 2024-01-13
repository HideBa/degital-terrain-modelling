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

INPUT_LAS = "./py/data/69BZ2_19.las"
STEP3_OUTPUT = "./py/data/out/dtm.tiff"
STEP4_OUTPUT = "./py/data/out/step4.tiff"
STEP5_OUTPUT = "./py/data/out/chm.tiff"
