def las_info(las):
    print("=========LAS Info=========")
    print("las metadata:")
    print(las.header)

    print("las dims:")
    for i, dim in enumerate(las.point_format):
        print(i, ": ", dim.name)

    print("las points:")
    print(len(las.points), "points")
    print("==========================")
