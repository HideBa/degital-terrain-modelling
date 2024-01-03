import json


def write_geojson(filepath, points):
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": (point[0], point[1])},
                "properties": {
                    "z": point[2],
                },
            }
            for point in points
        ],
    }
    with open(filepath, "w") as f:
        json.dump(geojson, f)
