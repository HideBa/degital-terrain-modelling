# Cell size and extent for our study area. Use this config for the final submission.
# GFTIN_CELL_SIZE = 90  # meters
# EXTENT = [
#     188250.01,
#     313992.0,
#     145.82,
#     188750.0,
#     314492.0,
#     196.6,
# ]  # [minx, miny, minz, maxx, maxy, maxz]

# Cell size and extent for the tiny dataset. Use this config for debugging and testing.
GFTIN_CELL_SIZE = 30  # meters
EXTENT = [
    188357.16128481762,
    314305.9965786306,
    145.82,
    188457.16128481762,
    314405.9965786306,
    196.6,
]


INPUT_LAS = "./data/input/69BZ2_19.LAZ"
STEP3_OUTPUT = "./data/tiny_dtm.tiff"
# STEP3_OUTPUT = "./data/dtm.tiff"
# STEP4_OUTPUT = "./data/step4.tiff"
# STEP5_OUTPUT = "./data/chm.tiff"
BENCHMARK_OUT_DIR = "./data/figure"
DEBUG_DATA_DIR = "./data/debug"
