from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

MIN_TARGET_DISTANCE_METERS = 1_000.0
MAX_TARGET_DISTANCE_METERS = 25_000.0
DISTANCE_TOLERANCE_PERCENT = 5.0


class RouteShape(StrEnum):
    SQUARE = "square"
    EQUILATERAL_TRIANGLE = "equilateral-triangle"
    RIGHT_TRIANGLE = "right-triangle"


@dataclass(frozen=True)
class Coordinate:
    lat: float
    lon: float


@dataclass(frozen=True)
class RouteRequest:
    start: Coordinate
    target_distance_meters: float
    shape: RouteShape


@dataclass(frozen=True)
class RouteResult:
    coordinates: list[Coordinate]
    requested_shape: RouteShape
    target_distance_meters: float
    actual_distance_meters: float
    distance_delta_percent: float
    start: Coordinate
    met_distance_tolerance: bool


class RouteGenerationError(Exception):
    """Raised when a matching route cannot be generated."""
