from __future__ import annotations

from routegen.io.geojson import route_result_to_geojson
from routegen.models import Coordinate, RouteResult, RouteShape


def test_geojson_feature_collection_contract() -> None:
    result = RouteResult(
        coordinates=[
            Coordinate(lat=41.0, lon=-87.0),
            Coordinate(lat=41.01, lon=-86.99),
            Coordinate(lat=41.0, lon=-87.0),
        ],
        requested_shape=RouteShape.SQUARE,
        target_distance_meters=1000,
        actual_distance_meters=990,
        distance_delta_percent=-1.0,
        start=Coordinate(lat=41.0, lon=-87.0),
        met_distance_tolerance=True,
    )

    geojson = route_result_to_geojson(result)

    assert geojson == {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-87.0, 41.0], [-86.99, 41.01], [-87.0, 41.0]],
                },
                "properties": {
                    "requested_shape": "square",
                    "target_distance_meters": 1000,
                    "actual_distance_meters": 990,
                    "distance_delta_percent": -1.0,
                    "start_location": [41.0, -87.0],
                    "met_distance_tolerance": True,
                },
            }
        ],
    }
