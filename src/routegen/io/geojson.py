from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from routegen.models import RouteResult


def route_result_to_geojson(result: RouteResult) -> dict[str, Any]:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [coordinate.lon, coordinate.lat]
                        for coordinate in result.coordinates
                    ],
                },
                "properties": {
                    "requested_shape": result.requested_shape.value,
                    "target_distance_meters": result.target_distance_meters,
                    "actual_distance_meters": result.actual_distance_meters,
                    "distance_delta_percent": result.distance_delta_percent,
                    "start_location": [result.start.lat, result.start.lon],
                    "met_distance_tolerance": result.met_distance_tolerance,
                },
            }
        ],
    }


def write_geojson_file(result: RouteResult, output_path: Path) -> None:
    output_path.write_text(
        json.dumps(route_result_to_geojson(result), indent=2) + "\n",
        encoding="utf-8",
    )
