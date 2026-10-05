from __future__ import annotations

import math
from itertools import pairwise

from routegen.models import Coordinate, RouteRequest, RouteShape
from routegen.routing.geo import offset_coordinate, rotate

MAX_SAMPLE_SPACING_METERS = 500.0


def generate_shape_samples(
    request: RouteRequest, orientation_degrees: float = 0.0
) -> list[Coordinate]:
    offsets = _shape_offsets(request.shape, request.target_distance_meters)
    sampled_offsets = _sample_offsets(offsets)
    return [
        offset_coordinate(request.start, *rotate(east, north, orientation_degrees))
        for east, north in sampled_offsets
    ]


def _sample_offsets(offsets: list[tuple[float, float]]) -> list[tuple[float, float]]:
    sampled = [offsets[0]]
    for start, end in pairwise(offsets):
        east_delta = end[0] - start[0]
        north_delta = end[1] - start[1]
        segment_length = math.hypot(east_delta, north_delta)
        segment_count = max(1, math.ceil(segment_length / MAX_SAMPLE_SPACING_METERS))
        for step in range(1, segment_count + 1):
            fraction = step / segment_count
            sampled.append(
                (
                    start[0] + (east_delta * fraction),
                    start[1] + (north_delta * fraction),
                )
            )
    return sampled


def _shape_offsets(
    shape: RouteShape, perimeter_meters: float
) -> list[tuple[float, float]]:
    if shape is RouteShape.SQUARE:
        side = perimeter_meters / 4
        return [
            (0, 0),
            (side, 0),
            (side, side),
            (0, side),
            (0, 0),
        ]

    if shape is RouteShape.EQUILATERAL_TRIANGLE:
        side = perimeter_meters / 3
        height = side * math.sqrt(3) / 2
        return [
            (0, 0),
            (side, 0),
            (side / 2, height),
            (0, 0),
        ]

    if shape is RouteShape.RIGHT_TRIANGLE:
        leg = perimeter_meters / (2 + math.sqrt(2))
        return [
            (0, 0),
            (leg, 0),
            (leg, leg),
            (0, 0),
        ]

    raise ValueError(f"unsupported route shape: {shape}")
