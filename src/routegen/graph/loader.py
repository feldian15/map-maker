from __future__ import annotations

import networkx as nx

from routegen.graph.models import LoadedGraph
from routegen.models import Coordinate

MAX_SEARCH_RADIUS_METERS = 12_500.0
MIN_SEARCH_RADIUS_METERS = 1_000.0
UNSAFE_HIGHWAY_CLASSES = frozenset(
    {
        "motorway",
        "motorway_link",
        "trunk",
        "trunk_link",
        "primary",
        "primary_link",
        "secondary",
        "secondary_link",
    }
)


def map_search_radius_meters(target_distance_meters: float) -> float:
    derived_radius = target_distance_meters / 2
    return min(MAX_SEARCH_RADIUS_METERS, max(MIN_SEARCH_RADIUS_METERS, derived_radius))


def load_walk_run_graph(
    start: Coordinate, target_distance_meters: float
) -> LoadedGraph:
    import osmnx as ox

    radius = map_search_radius_meters(target_distance_meters)
    graph = ox.graph_from_point(
        (start.lat, start.lon),
        dist=radius,
        network_type="walk",
        simplify=True,
    )
    return LoadedGraph(
        graph=filter_unsafe_highways(graph),
        map_search_radius_meters=radius,
    )


def filter_unsafe_highways(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    filtered = graph.copy()
    edges_to_remove = [
        (start, end, key)
        for start, end, key, data in filtered.edges(keys=True, data=True)
        if _has_unsafe_highway(data.get("highway"))
    ]
    filtered.remove_edges_from(edges_to_remove)
    return filtered


def _has_unsafe_highway(value: object) -> bool:
    if isinstance(value, str):
        return value in UNSAFE_HIGHWAY_CLASSES
    if isinstance(value, (list, tuple, set)):
        return any(item in UNSAFE_HIGHWAY_CLASSES for item in value)
    return False
