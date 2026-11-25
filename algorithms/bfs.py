"""Breadth-First Search (BFS) algorithm implementation for unweighted/hop-count pathfinding.

Finds routes with the minimum number of edge transitions, supporting
accessibility constraints and dynamic obstacle avoidance.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx


@dataclass
class BFSResult:
    """Encapsulates the outcome of a BFS path search."""

    path: List[str] = field(default_factory=list)
    edge_count: int = 0
    total_distance: float = 0.0
    total_time: float = 0.0
    success: bool = False
    error_message: Optional[str] = None

    def __bool__(self) -> bool:
        return self.success


def bfs_shortest_path(
    graph: nx.Graph,
    source: str,
    destination: str,
    wheelchair_accessible: bool = False,
    blocked_edges: Optional[Set[Tuple[str, str]]] = None,
    blocked_nodes: Optional[Set[str]] = None,
    raise_on_error: bool = False,
) -> BFSResult:
    """Find a route with the minimum number of edges between source and destination using BFS.

    Args:
        graph: NetworkX graph representing the campus network.
        source: Unique ID of the starting location.
        destination: Unique ID of the destination location.
        wheelchair_accessible: If True, only traverse wheelchair-accessible edges without stairs.
        blocked_edges: Optional set of (u, v) tuples to treat as impassable.
        blocked_nodes: Optional set of node IDs to treat as impassable.
        raise_on_error: If True, raises ValueError on invalid inputs; otherwise returns failed BFSResult.

    Returns:
        BFSResult instance containing path, hop count, metric totals, and status.

    Raises:
        ValueError: If raise_on_error is True and source/destination is invalid.
    """
    blocked_nodes_set = set(blocked_nodes or [])

    # Normalize blocked edges symmetrically
    normalized_blocked_edges: Set[Tuple[str, str]] = set()
    if blocked_edges:
        for u, v in blocked_edges:
            normalized_blocked_edges.add((u, v))
            normalized_blocked_edges.add((v, u))

    # Validate input locations
    if source not in graph:
        err = f"Starting location '{source}' was not found in the campus graph."
        if raise_on_error:
            raise ValueError(err)
        return BFSResult(success=False, error_message=err)

    if destination not in graph:
        err = f"Destination location '{destination}' was not found in the campus graph."
        if raise_on_error:
            raise ValueError(err)
        return BFSResult(success=False, error_message=err)

    if source in blocked_nodes_set:
        err = f"Starting location '{source}' is currently blocked or unavailable."
        if raise_on_error:
            raise ValueError(err)
        return BFSResult(success=False, error_message=err)

    if destination in blocked_nodes_set:
        err = f"Destination location '{destination}' is currently blocked or unavailable."
        if raise_on_error:
            raise ValueError(err)
        return BFSResult(success=False, error_message=err)

    # Trivial case: source is destination
    if source == destination:
        return BFSResult(
            path=[source],
            edge_count=0,
            total_distance=0.0,
            total_time=0.0,
            success=True,
        )

    # Standard BFS queue and parent tracking for path reconstruction
    queue: deque[str] = deque([source])
    visited: Set[str] = {source}
    parent: Dict[str, Optional[str]] = {source: None}

    reached = False

    while queue:
        current = queue.popleft()

        if current == destination:
            reached = True
            break

        for neighbor in graph.neighbors(current):
            if neighbor in visited:
                continue

            if neighbor in blocked_nodes_set:
                continue

            if (current, neighbor) in normalized_blocked_edges:
                continue

            edge_data = graph.get_edge_data(current, neighbor) or {}

            # Check edge status
            status = str(edge_data.get("status", "open")).lower()
            if status in ("blocked", "closed", "maintenance", "under_maintenance"):
                continue

            # Accessibility filtering: conservative policy excludes stairs and unverified/unknown paths
            if wheelchair_accessible:
                if edge_data.get("wheelchair_accessible") is not True:
                    continue
                if edge_data.get("has_stairs", False):
                    continue

            visited.add(neighbor)
            parent[neighbor] = current
            queue.append(neighbor)

    if not reached and parent.get(destination) is None:
        return BFSResult(
            path=[],
            edge_count=0,
            total_distance=0.0,
            total_time=0.0,
            success=False,
            error_message=f"No accessible route found between '{source}' and '{destination}'.",
        )

    # Reconstruct path from destination to source
    path: List[str] = []
    curr: Optional[str] = destination
    while curr is not None:
        path.append(curr)
        curr = parent.get(curr)
    path.reverse()

    # Calculate metric totals along the path
    total_distance = 0.0
    total_time = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        ed = graph.get_edge_data(u, v) or {}
        total_distance += float(ed.get("distance", 0.0))
        total_time += float(ed.get("estimated_time", 0.0))

    return BFSResult(
        path=path,
        edge_count=len(path) - 1,
        total_distance=round(total_distance, 2),
        total_time=round(total_time, 2),
        success=True,
    )
