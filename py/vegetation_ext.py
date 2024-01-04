import numpy as np


class VegetationExtractor:
    def __init__(self, las, cluster_name="ClusterID"):
        self.las = las

    def find_trees(self, las):
        trees = []
        clusters = np.unique(las.ClusterID)
        for cluster in clusters:
            cluster_points = las.points[las.ClusterID == cluster]
            # count number of returns of points. If there is a point with more than 4 returns, it is a tree
            num_returns = np.unique(cluster_points["number_of_returns"])
            if np.any(num_returns > 3):
                trees.append(cluster)

    def extract_first_returns(self, las):
        first_returns = las.points[las.return_number == 1]
        return first_returns
