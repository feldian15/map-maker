from __future__ import annotations

import math

from routegen.models import Coordinate

EARTH_RADIUS_METERS = 6_371_000.0


def offset_coordinate(
    origin: Coordinate, east_meters: float, north_meters: float
) -> Coordinate:
    lat_delta = math.degrees(north_meters / EARTH_RADIUS_METERS)
    lon_delta = math.degrees(
        east_meters / (EARTH_RADIUS_METERS * math.cos(math.radians(origin.lat)))
    )
    return Coordinate(lat=origin.lat + lat_delta, lon=origin.lon + lon_delta)


def planar_offset(origin: Coordinate, point: Coordinate) -> tuple[float, float]:
    north = math.radians(point.lat - origin.lat) * EARTH_RADIUS_METERS
    east = (
        math.radians(point.lon - origin.lon)
        * EARTH_RADIUS_METERS
        * math.cos(math.radians(origin.lat))
    )
    return east, north


def rotate(
    east_meters: float, north_meters: float, degrees: float
) -> tuple[float, float]:
    radians = math.radians(degrees)
    cos_theta = math.cos(radians)
    sin_theta = math.sin(radians)
    return (
        east_meters * cos_theta - north_meters * sin_theta,
        east_meters * sin_theta + north_meters * cos_theta,
    )


def distance_meters(first: Coordinate, second: Coordinate) -> float:
    origin = Coordinate(
        lat=(first.lat + second.lat) / 2, lon=(first.lon + second.lon) / 2
    )
    east_a, north_a = planar_offset(origin, first)
    east_b, north_b = planar_offset(origin, second)
    return math.hypot(east_a - east_b, north_a - north_b)
