from __future__ import annotations

import argparse
import sys
from pathlib import Path

from routegen.graph.loader import load_walk_run_graph
from routegen.io.geojson import write_geojson_file
from routegen.models import (
    MAX_TARGET_DISTANCE_METERS,
    MIN_TARGET_DISTANCE_METERS,
    Coordinate,
    RouteGenerationError,
    RouteRequest,
    RouteShape,
)
from routegen.routing.loop import generate_route


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="routegen")
    parser.add_argument(
        "--start",
        required=True,
        help="Start location as latitude,longitude.",
    )
    parser.add_argument(
        "--distance",
        required=True,
        type=float,
        help="Target distance in meters.",
    )
    parser.add_argument(
        "--shape",
        required=True,
        choices=[shape.value for shape in RouteShape],
        help="Route shape.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output GeoJSON path.",
    )
    return parser


def parse_start(value: str) -> Coordinate:
    try:
        lat_text, lon_text = value.split(",", maxsplit=1)
        lat = float(lat_text)
        lon = float(lon_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("start must be latitude,longitude") from exc

    if not -90 <= lat <= 90:
        raise argparse.ArgumentTypeError("latitude must be between -90 and 90")
    if not -180 <= lon <= 180:
        raise argparse.ArgumentTypeError("longitude must be between -180 and 180")
    return Coordinate(lat=lat, lon=lon)


def route_request_from_args(args: argparse.Namespace) -> RouteRequest:
    if not (MIN_TARGET_DISTANCE_METERS <= args.distance <= MAX_TARGET_DISTANCE_METERS):
        raise argparse.ArgumentTypeError(
            "distance must be between 1000 and 25000 meters"
        )

    return RouteRequest(
        start=parse_start(args.start),
        target_distance_meters=args.distance,
        shape=RouteShape(args.shape),
    )


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        request = route_request_from_args(args)
        result = generate_route(request, graph_provider=load_walk_run_graph)
        write_geojson_file(result, args.output)
    except (RouteGenerationError, OSError, argparse.ArgumentTypeError) as exc:
        parser.exit(2, f"routegen: error: {exc}\n")

    return 0


def main() -> None:
    raise SystemExit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
