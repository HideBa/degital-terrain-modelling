import numpy as np
import laspy


with laspy.open("./py/data/thinned.las") as f:
    las = f.read()
    bbox = [188250.0, 313992.0, 188350.0, 314092.0]
    X_invalid = (bbox[0] <= las.x) & (bbox[2] >= las.x)
    Y_invalid = (bbox[1] <= las.y) & (bbox[3] >= las.y)
    cond = X_invalid & Y_invalid
    print("--------")
    print("cond:", cond)
    good_indices = np.where(cond)[0]
    print("good_indices:", good_indices)
    good_points = las.points[good_indices].copy()

    print("good_points:", len(good_points))
    print("good point 1:", good_points[0])
