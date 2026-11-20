"""Dijkstra shortest-path algorithm implementation.

Supports:
- Distance-based optimization.
- Travel-time-based optimization.
- Wheelchair accessibility constraints.
- Dynamic obstacle and hazard exclusion.
- Complete route reconstruction with total distance and travel time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import heapq
import itertools
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx


@dataclass
class DijkstraResult:
    """Encapsulates the outcome of a Dijkstra path search."""

    path: List[str] = field(default_factory=list)
    total_distance: float = 0.0
    total_time: float = 0.0
    cost: float = 0.0
    optimization_metric: str = "distance"
    success: bool = False
    error_message: Optional[str] = None

    def __bool__(self) -> bool:
        return self.success


def dijkstra_shortest_path(
    graph: nx.Graph,
    source: str,
    destination: str,
    weight: str = "distance",
    wheelchair_accessible: bool = False,
    blocked_edges: Optional[Set[Tuple[str, str]]] = None,
    blocked_nodes: Optional[Set[str]] = None,
    raise_on_error: bool = False,
) -> DijkstraResult:
    """Find the optimal path between source and destination using Dijkstra's algorithm.

    Args:
        graph: NetworkX graph representing the campus network.
        source: Unique ID of the starting location.
        destination: Unique ID of the destination location.
        weight: Optimization metric ('distance' or 'estimated_time').
        wheelchair_accessible: If True, restricts traversal to wheelchair-friendly edges without stairs.
        blocked_edges: Optional set of (u, v) pairs to exclude.
        blocked_nodes: Optional set of node IDs to exclude.
        raise_on_error: If True, raises ValueError on invalid inputs; otherwise returns failed DijkstraResult.

    Returns:
        DijkstraResult containing optimal path, total distance, total travel time, and cost.

    Raises:
        ValueError: If raise_on_error is True and inputs are invalid.
    """
    valid_metrics = {"distance", "estimated_time", "time"}
    if weight == "time":
        weight = "estimated_time"

    if weight not in valid_metrics:
        err = f"Invalid optimization metric '{weight}'. Must be 'distance' or 'estimated_time'."
        if raise_on_error:
            raise ValueError(err)
        return DijkstraResult(success=False, error_message=err, optimization_metric=weight)

    blocked_nodes_set = set(blocked_nodes or [])

    normalized_blocked_edges: Set[Tuple[str, str]] = set()
    if blocked_edges:
        for u, v in blocked_edges:
            normalized_blocked_edges.add((u, v))
            normalized_blocked_edges.add((v, u))

    # Validate locations
    if source not in graph:
        err = f"Starting location '{source}' was not found in the campus graph."
        if raise_on_error:
            raise ValueError(err)
        return DijkstraResult(success=False, error_message=err, optimization_metric=weight)

    if destination not in graph:
        err = f"Destination location '{destination}' was not found in the campus graph."
        if raise_on_error:
            raise ValueError(err)
        return DijkstraResult(success=False, error_message=err, optimization_metric=weight)

    if source in blocked_nodes_set:
        err = f"Starting location '{source}' is currently blocked or unavailable."
        if raise_on_error:
            raise ValueError(err)
        return DijkstraResult(success=False, error_message=err, optimization_metric=weight)

    if destination in blocked_nodes_set:
        err = f"Destination location '{destination}' is currently blocked or unavailable."
        if raise_on_error:
            raise ValueError(err)
        return DijkstraResult(success=False, error_message=err, optimization_metric=weight)

    # Trivial case: source is destination
    if source == destination:
        return DijkstraResult(
            path=[source],
            total_distance=0.0,
            total_time=0.0,
            cost=0.0,
            optimization_metric=weight,
            success=True,
        )

    # Priority queue: stores (cost, sequence_counter, node_id)
    counter = itertools.count()
    pq: List[Tuple[float, int, str]] = [(0.0, next(counter), source)]

    # Best-known costs from source
    costs: Dict[str, float] = {source: 0.0}
    parent: Dict[str, Optional[str]] = {source: None}
    settled: Set[str] = set()

    # Track metrics separately for exact reporting
    dist_accum: Dict[str, float] = {source: 0.0}
    time_accum: Dict[str, float] = {source: 0.0}

    reached = False

    while pq:
        current_cost, _, current = heapq.heappop(pq)

        if current in settled:
            continue
        settled.add(current)

        if current == destination:
            reached = True
            break

        for neighbor in graph.neighbors(current):
            if neighbor in settled:
                continue

            if neighbor in blocked_nodes_set:
                continue

            if (current, neighbor) in normalized_blocked_edges:
                continue

            edge_data = graph.get_edge_data(current, neighbor) or {}

            # Check edge status
            status = edge_data.get("status", "open")
            if status in ("blocked", "closed"):
                continue

            # Accessibility check
            if wheelchair_accessible:
                if not edge_data.get("wheelchair_accessible", True):
                    continue
                if edge_data.get("has_stairs", False):
                    continue

            # Compute edge traversal cost
            edge_dist = float(edge_data.get("distance", 1.0))
            edge_time = float(edge_data.get("estimated_time", edge_dist * 0.8))
            edge_weight = edge_time if weight == "estimated_time" else edge_dist

            new_cost = current_cost + edge_weight

            if neighbor not in costs or new_cost < costs[neighbor]:
                costs[neighbor] = new_cost
                parent[neighbor] = current
                dist_accum[neighbor] = dist_accum[current] + edge_dist
                time_accum[neighbor] = time_accum[current] + edge_time
                heapq.heappush(pq, (new_cost, next(counter), neighbor))

    if not reached or parent.get(destination) is None:
        return DijkstraResult(
            path=[],
            total_distance=0.0,
            total_time=0.0,
            cost=0.0,
            optimization_metric=weight,
            success=False,
            error_message=f"No accessible route found between '{source}' and '{destination}'.",
        )

    # Reconstruct route
    path: List[str] = []
    curr: Optional[str] = destination
    while curr is not None:
        path.append(curr)
        curr = parent.get(curr)
    path.reverse()

    final_distance = dist_accum.get(destination, 0.0)
    final_time = time_accum.get(destination, 0.0)
    final_cost = costs.get(destination, 0.0)

    return DijkstraResult(
        path=path,
        total_distance=round(final_distance, 2),
        total_time=round(final_time, 2),
        cost=round(final_cost, 2),
        optimization_metric=weight,
        success=True,
    )
