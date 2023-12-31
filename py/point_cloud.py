class PointCloud:
    def __init__(self, points):
        self.points = points

    def first_returns(self):
        """
        Returns the first returns of the point cloud as numpy array
        """
        return self.points[self.points["return_num"] == 1]
