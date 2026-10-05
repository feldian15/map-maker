from __future__ import annotations

from itertools import pairwise

import pytest

from routegen.models import Coordinate, RouteRequest, RouteShape
from routegen.routing.geo import distance_meters
from routegen.routing.shapes import generate_shape_samples


@pytest.mark.parametrize(
    "shape",
    [
        RouteShape.SQUARE,
        RouteShape.EQUILATERAL_TRIANGLE,
        RouteShape.RIGHT_TRIANGLE,
    ],
)
def test_shape_samples_start_and_end_at_start_location(shape: RouteShape) -> None:
    start = Coordinate(lat=41.0, lon=-87.0)
    request = RouteRequest(
        start=start,
        target_distance_meters=1200,
        shape=shape,
    )

    samples = generate_shape_samples(request)

    assert samples[0] == start
    assert samples[-1] == start


def test_square_samples_scale_from_target_distance() -> None:
    request = RouteRequest(
        start=Coordinate(lat=41.0, lon=-87.0),
        target_distance_meters=4000,
        shape=RouteShape.SQUARE,
    )

    samples = generate_shape_samples(request)

    sides = [distance_meters(a, b) for a, b in pairwise(samples)]
    assert sum(sides) == pytest.approx(4000, rel=0.01)


def test_equilateral_triangle_samples_scale_from_target_distance() -> None:
    request = RouteRequest(
        start=Coordinate(lat=41.0, lon=-87.0),
        target_distance_meters=3000,
        shape=RouteShape.EQUILATERAL_TRIANGLE,
    )

    samples = generate_shape_samples(request)

    sides = [distance_meters(a, b) for a, b in pairwise(samples)]
    assert sum(sides) == pytest.approx(3000, rel=0.01)


def test_right_triangle_samples_form_45_45_90_triangle() -> None:
    request = RouteRequest(
        start=Coordinate(lat=41.0, lon=-87.0),
        target_distance_meters=3414.21356,
        shape=RouteShape.RIGHT_TRIANGLE,
    )

    samples = generate_shape_samples(request)

    sides = [distance_meters(a, b) for a, b in pairwise(samples)]
    assert sum(sides) == pytest.approx(3414.21356, rel=0.01)


def test_longer_routes_include_intermediate_shape_samples() -> None:
    request = RouteRequest(
        start=Coordinate(lat=41.0, lon=-87.0),
        target_distance_meters=4000,
        shape=RouteShape.SQUARE,
    )

    samples = generate_shape_samples(request)

    assert len(samples) > 5
