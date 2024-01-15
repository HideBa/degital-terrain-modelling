import json

import numpy as np
from pyproj import Proj, Transformer


def write_geojson(filepath, points, src_crs=None, target_crs=None):
    """
    points: [[x, y, z], ...]
    """
    points = transform_points(points, src_crs, target_crs)
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": (point[0], point[1])},
                "properties": {
                    "z": point[2] if len(point) == 3 else None,
                },
            }
            for point in points
        ],
    }
    with open(filepath, "w") as f:
        json.dump(geojson, f)


def transform_points(points, src_crs=None, target_crs=None):
    if src_crs is None or target_crs is None:
        return []
    source_crs = Proj(init=src_crs)
    destination_crs = Proj(init=target_crs)
    transformer = Transformer.from_proj(source_crs, destination_crs)
    pts = np.array(list(transformer.itransform(points)), dtype=np.float64)
    return pts


def transform_triangles(triangles, src_crs=None, target_crs=None):
    if src_crs is not None and target_crs is not None:
        source_crs = Proj(init=src_crs)
        destination_crs = Proj(init=target_crs)
        transformer = Transformer.from_proj(source_crs, destination_crs)
        triangles = np.array(list(transformer.itransform(triangles)), dtype=np.float64)
