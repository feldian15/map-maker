from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from itertools import pairwise
from typing import Any

import networkx as nx

from routegen.graph.models import LoadedGraph, node_coordinate
from routegen.models import (
    DISTANCE_TOLERANCE_PERCENT,
    Coordinate,
    RouteGenerationError,
    RouteRequest,
    RouteResult,
)
from routegen.routing.geo import distance_meters, planar_offset
from routegen.routing.shapes import generate_shape_samples

GraphProvider = Callable[[Coordinate, float], nx.Graph | LoadedGraph]

ORIENTATIONS_DEGREES = (0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0)


@dataclass(frozen=True)
class CandidateRoute:
    coordinates: list[Coordinate]
    actual_distance_meters: float
    shape_error_meters: float


def generate_route(request: RouteRequest, graph_provider: GraphProvider) -> RouteResult:
    loaded_graph = graph_provider(request.start, request.target_distance_meters)
    graph, map_search_radius = _unpack_loaded_graph(loaded_graph)
    candidates: list[CandidateRoute] = []

    for orientation in ORIENTATIONS_DEGREES:
        samples = generate_shape_samples(request, orientation_degrees=orientation)
        try:
            candidates.append(_route_through_samples(graph, samples, request.start))
        except (nx.NetworkXNoPath, nx.NodeNotFound, ValueError):
            continue

    if not candidates:
        radius = (
            f"{map_search_radius:g}" if map_search_radius is not None else "unknown"
        )
        raise RouteGenerationError(
            "could not generate matching route "
            f"for shape={request.shape.value}, "
            f"start=({request.start.lat},{request.start.lon}), "
            f"target_distance_meters={request.target_distance_meters:g}, "
            f"map_search_radius_meters={radius}"
        )

    best = _select_best_candidate(candidates, request.target_distance_meters)
    delta_percent = _distance_delta_percent(
        best.actual_distance_meters, request.target_distance_meters
    )
    return RouteResult(
        coordinates=best.coordinates,
        requested_shape=request.shape,
        target_distance_meters=request.target_distance_meters,
        actual_distance_meters=best.actual_distance_meters,
        distance_delta_percent=delta_percent,
        start=request.start,
        met_distance_tolerance=abs(delta_percent) <= DISTANCE_TOLERANCE_PERCENT,
    )


def _route_through_samples(
    graph: nx.Graph, samples: list[Coordinate], requested_start: Coordinate
) -> CandidateRoute:
    if len(samples) < 2:
        raise ValueError("at least two shape samples are required")

    sample_nodes = [_nearest_node(graph, sample) for sample in samples]
    route_nodes: list[Any] = []
    total_distance = 0.0

    for (start_sample, end_sample), (start_node, end_node) in zip(
        pairwise(samples), pairwise(sample_nodes), strict=True
    ):
        if start_node == end_node and start_sample != end_sample:
            raise nx.NetworkXNoPath("consecutive shape samples collapsed to one node")
        path = nx.shortest_path(graph, start_node, end_node, weight="length")
        if route_nodes:
            route_nodes.extend(path[1:])
        else:
            route_nodes.extend(path)
        total_distance += _path_length(graph, path)

    graph_coordinates = [node_coordinate(graph, node) for node in route_nodes]
    coordinates = _preserve_requested_start(graph_coordinates, requested_start)
    connector_distance = distance_meters(requested_start, graph_coordinates[0])
    if graph_coordinates[-1] != requested_start:
        connector_distance += distance_meters(requested_start, graph_coordinates[-1])
    shape_error = sum(
        distance_meters(sample, node_coordinate(graph, node))
        for sample, node in zip(samples, sample_nodes)
    )
    shape_error += _path_adherence_penalty(coordinates, samples)
    return CandidateRoute(
        coordinates=coordinates,
        actual_distance_meters=total_distance + connector_distance,
        shape_error_meters=shape_error,
    )


def _nearest_node(graph: nx.Graph, sample: Coordinate) -> Any:
    if not graph.nodes:
        raise ValueError("travel network is empty")

    return min(
        graph.nodes,
        key=lambda node: distance_meters(sample, node_coordinate(graph, node)),
    )


def _unpack_loaded_graph(
    loaded_graph: nx.Graph | LoadedGraph,
) -> tuple[nx.Graph, float | None]:
    if isinstance(loaded_graph, LoadedGraph):
        return loaded_graph.graph, loaded_graph.map_search_radius_meters
    return loaded_graph, None


def _preserve_requested_start(
    graph_coordinates: list[Coordinate], requested_start: Coordinate
) -> list[Coordinate]:
    if not graph_coordinates:
        return [requested_start]

    coordinates = list(graph_coordinates)
    if coordinates[0] != requested_start:
        coordinates.insert(0, requested_start)
    if coordinates[-1] != requested_start:
        coordinates.append(requested_start)
    return coordinates


def _path_adherence_penalty(
    coordinates: list[Coordinate], samples: list[Coordinate]
) -> float:
    return sum(
        min(
            _distance_to_sample_segment(coordinate, start, end)
            for start, end in pairwise(samples)
        )
        for coordinate in coordinates
    )


def _distance_to_sample_segment(
    point: Coordinate, start: Coordinate, end: Coordinate
) -> float:
    point_east, point_north = planar_offset(start, point)
    end_east, end_north = planar_offset(start, end)
    segment_length_squared = (end_east * end_east) + (end_north * end_north)
    if segment_length_squared == 0:
        return distance_meters(point, start)

    projection = (
        (point_east * end_east) + (point_north * end_north)
    ) / segment_length_squared
    clamped_projection = min(1.0, max(0.0, projection))
    closest_east = end_east * clamped_projection
    closest_north = end_north * clamped_projection
    return (
        (point_east - closest_east) ** 2 + (point_north - closest_north) ** 2
    ) ** 0.5


def _path_length(graph: nx.Graph, path: list[Any]) -> float:
    return sum(_edge_length(graph, start, end) for start, end in pairwise(path))


def _edge_length(graph: nx.Graph, start: Any, end: Any) -> float:
    data = graph.get_edge_data(start, end)
    if data is None:
        raise nx.NetworkXNoPath(f"missing edge from {start!r} to {end!r}")
    if "length" in data:
        return float(data["length"])
    if isinstance(data, dict):
        return min(float(edge.get("length", 0.0)) for edge in data.values())
    return 0.0


def _select_best_candidate(
    candidates: list[CandidateRoute], target_distance_meters: float
) -> CandidateRoute:
    within_tolerance = [
        candidate
        for candidate in candidates
        if abs(
            _distance_delta_percent(
                candidate.actual_distance_meters, target_distance_meters
            )
        )
        <= DISTANCE_TOLERANCE_PERCENT
    ]
    if within_tolerance:
        return min(
            within_tolerance,
            key=lambda candidate: (
                abs(candidate.actual_distance_meters - target_distance_meters),
                candidate.shape_error_meters,
            ),
        )
    return min(
        candidates,
        key=lambda candidate: (
            candidate.actual_distance_meters,
            candidate.shape_error_meters,
        ),
    )


def _distance_delta_percent(actual: float, target: float) -> float:
    return ((actual - target) / target) * 100
