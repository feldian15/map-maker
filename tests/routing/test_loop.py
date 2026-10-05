from __future__ import annotations

import networkx as nx
import pytest

from routegen.graph.models import LoadedGraph
from routegen.models import Coordinate, RouteGenerationError, RouteRequest, RouteShape
from routegen.routing.geo import distance_meters, offset_coordinate
from routegen.routing.loop import generate_route
from routegen.routing.shapes import generate_shape_samples


def add_node_at(graph: nx.Graph, node: str, coordinate: Coordinate) -> None:
    graph.add_node(node, y=coordinate.lat, x=coordinate.lon)


def square_graph(start: Coordinate, side_meters: float, edge_length: float) -> nx.Graph:
    east = offset_coordinate(start, side_meters, 0)
    north_east = offset_coordinate(start, side_meters, side_meters)
    north = offset_coordinate(start, 0, side_meters)
    graph = nx.Graph()
    add_node_at(graph, "start", start)
    add_node_at(graph, "east", east)
    add_node_at(graph, "north_east", north_east)
    add_node_at(graph, "north", north)
    graph.add_edge("start", "east", length=edge_length)
    graph.add_edge("east", "north_east", length=edge_length)
    graph.add_edge("north_east", "north", length=edge_length)
    graph.add_edge("north", "start", length=edge_length)
    return graph


def test_route_engine_connects_shape_samples_in_order_and_returns_loop() -> None:
    start = Coordinate(lat=0.0, lon=0.0)
    graph = square_graph(start, side_meters=250, edge_length=250)
    request = RouteRequest(
        start=start,
        target_distance_meters=1000,
        shape=RouteShape.SQUARE,
    )

    result = generate_route(request, graph_provider=lambda start, distance: graph)

    assert result.coordinates[0] == Coordinate(lat=0.0, lon=0.0)
    assert result.coordinates[-1] == Coordinate(lat=0.0, lon=0.0)
    assert result.actual_distance_meters == 1000
    assert result.met_distance_tolerance is True


def test_route_engine_allows_repeated_segments_to_complete_loop() -> None:
    start = Coordinate(lat=0.0, lon=0.0)
    middle = offset_coordinate(start, 293, 0)
    far = offset_coordinate(start, 293, 293)
    graph = nx.Graph()
    add_node_at(graph, "start", start)
    add_node_at(graph, "middle", middle)
    add_node_at(graph, "far", far)
    graph.add_edge("start", "middle", length=293)
    graph.add_edge("middle", "far", length=293)
    request = RouteRequest(
        start=start,
        target_distance_meters=1000,
        shape=RouteShape.RIGHT_TRIANGLE,
    )

    result = generate_route(request, graph_provider=lambda start, distance: graph)

    assert result.coordinates.count(middle) > 1
    assert result.coordinates[-1] == start


def test_route_engine_prefers_distance_matched_candidate() -> None:
    start = Coordinate(lat=0.0, lon=0.0)
    east = offset_coordinate(start, 500, 0)
    north_east = offset_coordinate(start, 500, 500)
    north = offset_coordinate(start, 0, 500)
    graph = nx.Graph()
    add_node_at(graph, "start", start)
    add_node_at(graph, "near", east)
    add_node_at(graph, "far", north_east)
    add_node_at(graph, "north", north)
    graph.add_edge("start", "near", length=500)
    graph.add_edge("near", "far", length=500)
    graph.add_edge("far", "north", length=500)
    graph.add_edge("north", "start", length=500)
    request = RouteRequest(
        start=start,
        target_distance_meters=2000,
        shape=RouteShape.SQUARE,
    )

    result = generate_route(request, graph_provider=lambda start, distance: graph)

    assert result.actual_distance_meters == 2000
    assert result.met_distance_tolerance is True


def test_route_engine_returns_shortest_matching_route_when_no_candidate_is_in_tolerance() -> (
    None
):
    start = Coordinate(lat=0.0, lon=0.0)
    graph = square_graph(start, side_meters=250, edge_length=100)
    request = RouteRequest(
        start=start,
        target_distance_meters=1000,
        shape=RouteShape.SQUARE,
    )

    result = generate_route(request, graph_provider=lambda start, distance: graph)

    assert result.actual_distance_meters == 400
    assert result.met_distance_tolerance is False


def test_route_engine_reports_clear_failure_when_samples_cannot_be_visited() -> None:
    start = Coordinate(lat=0.0, lon=0.0)
    east = offset_coordinate(start, 250, 0)
    graph = nx.Graph()
    add_node_at(graph, "start", start)
    add_node_at(graph, "east", east)
    request = RouteRequest(
        start=start,
        target_distance_meters=1000,
        shape=RouteShape.SQUARE,
    )

    with pytest.raises(RouteGenerationError, match="map_search_radius_meters=1000"):
        generate_route(
            request,
            graph_provider=lambda start, distance: LoadedGraph(
                graph=graph,
                map_search_radius_meters=1000,
            ),
        )


def test_route_engine_preserves_requested_start_when_it_is_not_a_graph_node() -> None:
    requested_start = Coordinate(lat=0.0, lon=0.0)
    snapped_start = offset_coordinate(requested_start, 8, 0)
    graph = square_graph(snapped_start, side_meters=250, edge_length=250)
    request = RouteRequest(
        start=requested_start,
        target_distance_meters=1000,
        shape=RouteShape.SQUARE,
    )

    result = generate_route(request, graph_provider=lambda start, distance: graph)

    assert result.coordinates[0] == requested_start
    assert result.coordinates[-1] == requested_start
    assert result.coordinates[1] == snapped_start
    assert result.actual_distance_meters == pytest.approx(
        1000 + (2 * distance_meters(requested_start, snapped_start))
    )


def test_route_engine_prefers_route_that_stays_near_sampled_outline() -> None:
    start = Coordinate(lat=0.0, lon=0.0)
    request = RouteRequest(
        start=start,
        target_distance_meters=1000,
        shape=RouteShape.SQUARE,
    )
    graph = nx.Graph()
    bad_samples = generate_shape_samples(request, orientation_degrees=0)
    good_samples = generate_shape_samples(request, orientation_degrees=45)

    add_node_at(graph, "start", start)
    for index, coordinate in enumerate(bad_samples[1:], start=1):
        add_node_at(graph, f"bad-{index}", coordinate)
    for index, coordinate in enumerate(good_samples[1:], start=1):
        add_node_at(graph, f"good-{index}", coordinate)

    for index in range(len(bad_samples) - 1):
        detour = offset_coordinate(bad_samples[index], 0, 300)
        add_node_at(graph, f"detour-{index}", detour)
        bad_start = "start" if index == 0 else f"bad-{index}"
        bad_end = "start" if index + 1 == len(bad_samples) - 1 else f"bad-{index + 1}"
        good_start = "start" if index == 0 else f"good-{index}"
        good_end = (
            "start" if index + 1 == len(good_samples) - 1 else f"good-{index + 1}"
        )
        graph.add_edge(bad_start, f"detour-{index}", length=62.5)
        graph.add_edge(f"detour-{index}", bad_end, length=62.5)
        graph.add_edge(good_start, good_end, length=125)

    result = generate_route(request, graph_provider=lambda start, distance: graph)

    assert result.coordinates[0] == start
    assert result.coordinates[1] == good_samples[1]
    assert all(
        coordinate not in result.coordinates
        for coordinate in (
            offset_coordinate(bad_samples[index], 0, 300)
            for index in range(len(bad_samples) - 1)
        )
    )
