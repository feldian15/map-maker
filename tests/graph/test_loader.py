from __future__ import annotations

import types

import networkx as nx

from routegen.graph.loader import (
    filter_unsafe_highways,
    load_walk_run_graph,
    map_search_radius_meters,
)
from routegen.models import Coordinate


def test_map_search_area_is_derived_from_target_distance_and_bounded() -> None:
    assert map_search_radius_meters(1000) == 1000
    assert map_search_radius_meters(10_000) == 5000
    assert map_search_radius_meters(25_000) == 12_500


def test_load_walk_run_graph_uses_osmnx_walk_network_without_custom_filter(
    monkeypatch,
) -> None:
    captured_kwargs = {}
    graph = nx.MultiDiGraph()

    def fake_graph_from_point(*args, **kwargs):
        captured_kwargs.update(kwargs)
        return graph

    monkeypatch.setitem(
        __import__("sys").modules,
        "osmnx",
        types.SimpleNamespace(graph_from_point=fake_graph_from_point),
    )

    result = load_walk_run_graph(Coordinate(lat=41.0, lon=-87.0), 10_000)

    assert list(result.graph.edges) == list(graph.edges)
    assert result.map_search_radius_meters == 5000
    assert captured_kwargs["network_type"] == "walk"
    assert "custom_filter" not in captured_kwargs


def test_filter_unsafe_highways_removes_major_road_edges() -> None:
    graph = nx.MultiDiGraph()
    graph.add_edge("a", "b", key=0, highway="residential", length=10)
    graph.add_edge("b", "c", key=0, highway="motorway", length=10)
    graph.add_edge("c", "d", key=0, highway=["footway", "primary"], length=10)

    filtered = filter_unsafe_highways(graph)

    assert filtered.has_edge("a", "b")
    assert not filtered.has_edge("b", "c")
    assert not filtered.has_edge("c", "d")
