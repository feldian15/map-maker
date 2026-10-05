from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import networkx as nx

from routegen.models import Coordinate


@dataclass(frozen=True)
class LoadedGraph:
    graph: nx.Graph
    map_search_radius_meters: float


def node_coordinate(graph: nx.Graph, node: Any) -> Coordinate:
    data = graph.nodes[node]
    return Coordinate(lat=float(data["y"]), lon=float(data["x"]))
