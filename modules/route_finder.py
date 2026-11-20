"""Route planning engine integrating BFS and Dijkstra pathfinding with accessibility constraints."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import networkx as nx

from algorithms.bfs import BFSResult, bfs_shortest_path
from algorithms.dijkstra import DijkstraResult, dijkstra_shortest_path
from modules.campus_map import CampusMap


@dataclass
class RouteStep:
    """Detailed information for a single segment along a planned route."""

    step_number: int
    from_id: str
    to_id: str
    from_name: str
    to_name: str
    from_floor: int
    to_floor: int
    distance: float
    estimated_time: float
    wheelchair_accessible: bool
    has_stairs: bool
    has_ramp: bool
    has_elevator: bool
    instruction: str


@dataclass
class RouteResult:
    """Consolidated result of a route search query."""

    path: List[str] = field(default_factory=list)
    total_distance: float = 0.0
    total_time: float = 0.0
    edge_count: int = 0
    is_accessible: bool = False
    algorithm_used: str = "dijkstra"
    optimization_metric: str = "distance"
    steps: List[RouteStep] = field(default_factory=list)
    success: bool = False
    error_message: Optional[str] = None

    def __bool__(self) -> bool:
        return self.success


class RouteFinder:
    """Comprehensive route planning engine for college campus pedestrian navigation."""

    def __init__(self, campus_map: Union[CampusMap, nx.Graph]) -> None:
        """Initialize RouteFinder with a CampusMap or NetworkX graph.

        Args:
            campus_map: CampusMap instance or NetworkX Graph object.
        """
        if isinstance(campus_map, CampusMap):
            self.campus_map: Optional[CampusMap] = campus_map
            self.graph: nx.Graph = campus_map.graph
        elif isinstance(campus_map, nx.Graph):
            self.campus_map = None
            self.graph = campus_map
        else:
            raise TypeError("campus_map must be an instance of CampusMap or nx.Graph.")

    def _get_location_info(self, location_id: str) -> Dict[str, Any]:
        """Fetch location node attributes safely."""
        if self.campus_map:
            loc = self.campus_map.get_location(location_id)
            if loc:
                return loc
        return dict(self.graph.nodes.get(location_id, {}))

    def _generate_step_instruction(
        self,
        from_id: str,
        to_id: str,
        from_info: Dict[str, Any],
        to_info: Dict[str, Any],
        edge_data: Dict[str, Any],
    ) -> str:
        """Generate human-readable navigational direction for a single path segment."""
        from_name = from_info.get("name", from_id)
        to_name = to_info.get("name", to_id)
        from_floor = from_info.get("floor", 0)
        to_floor = to_info.get("floor", 0)
        dist = edge_data.get("distance", 0.0)

        if edge_data.get("has_elevator", False):
            return f"Take the elevator from {from_name} (Floor {from_floor}) to {to_name} (Floor {to_floor})."

        if edge_data.get("has_stairs", False):
            direction = "up" if to_floor > from_floor else "down" if to_floor < from_floor else ""
            floor_str = f" {direction} to Floor {to_floor}" if direction else ""
            return f"Use the staircase from {from_name}{floor_str} toward {to_name} ({dist:.1f} m)."

        if edge_data.get("has_ramp", False):
            return f"Follow the accessible ramp from {from_name} to {to_name} ({dist:.1f} m)."

        if from_floor != to_floor:
            return f"Transition between floors from {from_name} (Floor {from_floor}) to {to_name} (Floor {to_floor}) ({dist:.1f} m)."

        return f"Walk along the corridor from {from_name} to {to_name} ({dist:.1f} m)."

    def _build_route_steps(self, path: List[str]) -> List[RouteStep]:
        """Assemble structured navigational steps with instructions along a path."""
        steps: List[RouteStep] = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            u_info = self._get_location_info(u)
            v_info = self._get_location_info(v)
            edge_data = self.graph.get_edge_data(u, v) or {}

            instruction = self._generate_step_instruction(u, v, u_info, v_info, edge_data)

            step = RouteStep(
                step_number=i + 1,
                from_id=u,
                to_id=v,
                from_name=u_info.get("name", u),
                to_name=v_info.get("name", v),
                from_floor=int(u_info.get("floor", 0)),
                to_floor=int(v_info.get("floor", 0)),
                distance=float(edge_data.get("distance", 0.0)),
                estimated_time=float(edge_data.get("estimated_time", 0.0)),
                wheelchair_accessible=bool(edge_data.get("wheelchair_accessible", True)),
                has_stairs=bool(edge_data.get("has_stairs", False)),
                has_ramp=bool(edge_data.get("has_ramp", False)),
                has_elevator=bool(edge_data.get("has_elevator", False)),
                instruction=instruction,
            )
            steps.append(step)
        return steps

    def find_route(
        self,
        source: str,
        destination: str,
        algorithm: str = "dijkstra",
        optimize_for: str = "distance",
        wheelchair_accessible: bool = False,
        blocked_edges: Optional[Set[Tuple[str, str]]] = None,
        blocked_nodes: Optional[Set[str]] = None,
    ) -> RouteResult:
        """Calculate a route based on specified algorithm and operational constraints.

        Args:
            source: Unique ID of the starting location.
            destination: Unique ID of the destination location.
            algorithm: Algorithm to employ ('dijkstra' or 'bfs').
            optimize_for: Metric to minimize in Dijkstra ('distance' or 'time'/'estimated_time').
            wheelchair_accessible: Restrict traversal to step-free, wheelchair-friendly paths.
            blocked_edges: Set of unavailable (u, v) edge pairs.
            blocked_nodes: Set of unavailable node IDs.

        Returns:
            RouteResult with turn-by-turn guidance, distance, time, and status.
        """
        algo_choice = algorithm.lower().strip()
        opt_metric = "estimated_time" if optimize_for in ("time", "fastest") else "distance"

        if algo_choice == "bfs":
            bfs_res = bfs_shortest_path(
                graph=self.graph,
                source=source,
                destination=destination,
                wheelchair_accessible=wheelchair_accessible,
                blocked_edges=blocked_edges,
                blocked_nodes=blocked_nodes,
                raise_on_error=False,
            )
            if not bfs_res.success:
                return RouteResult(
                    path=[],
                    algorithm_used="bfs",
                    optimization_metric="hops",
                    is_accessible=wheelchair_accessible,
                    success=False,
                    error_message=bfs_res.error_message,
                )

            steps = self._build_route_steps(bfs_res.path)
            return RouteResult(
                path=bfs_res.path,
                total_distance=bfs_res.total_distance,
                total_time=bfs_res.total_time,
                edge_count=bfs_res.edge_count,
                is_accessible=wheelchair_accessible,
                algorithm_used="bfs",
                optimization_metric="hops",
                steps=steps,
                success=True,
            )

        if algo_choice == "dijkstra":
            dijkstra_res = dijkstra_shortest_path(
                graph=self.graph,
                source=source,
                destination=destination,
                weight=opt_metric,
                wheelchair_accessible=wheelchair_accessible,
                blocked_edges=blocked_edges,
                blocked_nodes=blocked_nodes,
                raise_on_error=False,
            )
            if not dijkstra_res.success:
                return RouteResult(
                    path=[],
                    algorithm_used="dijkstra",
                    optimization_metric=opt_metric,
                    is_accessible=wheelchair_accessible,
                    success=False,
                    error_message=dijkstra_res.error_message,
                )

            steps = self._build_route_steps(dijkstra_res.path)
            return RouteResult(
                path=dijkstra_res.path,
                total_distance=dijkstra_res.total_distance,
                total_time=dijkstra_res.total_time,
                edge_count=max(0, len(dijkstra_res.path) - 1),
                is_accessible=wheelchair_accessible,
                algorithm_used="dijkstra",
                optimization_metric=opt_metric,
                steps=steps,
                success=True,
            )

        return RouteResult(
            path=[],
            success=False,
            error_message=f"Unsupported algorithm '{algorithm}'. Choose 'dijkstra' or 'bfs'.",
        )

    def find_shortest_distance(
        self,
        source: str,
        destination: str,
        wheelchair_accessible: bool = False,
        blocked_edges: Optional[Set[Tuple[str, str]]] = None,
        blocked_nodes: Optional[Set[str]] = None,
    ) -> RouteResult:
        """Find the shortest distance route between two locations."""
        return self.find_route(
            source=source,
            destination=destination,
            algorithm="dijkstra",
            optimize_for="distance",
            wheelchair_accessible=wheelchair_accessible,
            blocked_edges=blocked_edges,
            blocked_nodes=blocked_nodes,
        )

    def find_fastest_time(
        self,
        source: str,
        destination: str,
        wheelchair_accessible: bool = False,
        blocked_edges: Optional[Set[Tuple[str, str]]] = None,
        blocked_nodes: Optional[Set[str]] = None,
    ) -> RouteResult:
        """Find the fastest travel-time route between two locations."""
        return self.find_route(
            source=source,
            destination=destination,
            algorithm="dijkstra",
            optimize_for="time",
            wheelchair_accessible=wheelchair_accessible,
            blocked_edges=blocked_edges,
            blocked_nodes=blocked_nodes,
        )

    def find_wheelchair_route(
        self,
        source: str,
        destination: str,
        optimize_for: str = "distance",
        blocked_edges: Optional[Set[Tuple[str, str]]] = None,
        blocked_nodes: Optional[Set[str]] = None,
    ) -> RouteResult:
        """Find an exclusively step-free, wheelchair-accessible route."""
        return self.find_route(
            source=source,
            destination=destination,
            algorithm="dijkstra",
            optimize_for=optimize_for,
            wheelchair_accessible=True,
            blocked_edges=blocked_edges,
            blocked_nodes=blocked_nodes,
        )

    def find_bfs_route(
        self,
        source: str,
        destination: str,
        wheelchair_accessible: bool = False,
        blocked_edges: Optional[Set[Tuple[str, str]]] = None,
        blocked_nodes: Optional[Set[str]] = None,
    ) -> RouteResult:
        """Find a route with the minimum number of transitions (hops)."""
        return self.find_route(
            source=source,
            destination=destination,
            algorithm="bfs",
            wheelchair_accessible=wheelchair_accessible,
            blocked_edges=blocked_edges,
            blocked_nodes=blocked_nodes,
        )

    def find_alternative_routes(
        self,
        source: str,
        destination: str,
        max_alternatives: int = 2,
        optimize_for: str = "distance",
        wheelchair_accessible: bool = False,
        blocked_edges: Optional[Set[Tuple[str, str]]] = None,
        blocked_nodes: Optional[Set[str]] = None,
    ) -> List[RouteResult]:
        """Compute distinct alternative routes by selectively excluding segments from the primary path.

        Args:
            source: Source location ID.
            destination: Destination location ID.
            max_alternatives: Maximum number of alternative routes to return.
            optimize_for: Metric ('distance' or 'time').
            wheelchair_accessible: Accessibility constraint flag.
            blocked_edges: Existing blocked edges to respect.
            blocked_nodes: Existing blocked nodes to respect.

        Returns:
            List of distinct RouteResult objects representing alternative routes.
        """
        primary = self.find_route(
            source=source,
            destination=destination,
            algorithm="dijkstra",
            optimize_for=optimize_for,
            wheelchair_accessible=wheelchair_accessible,
            blocked_edges=blocked_edges,
            blocked_nodes=blocked_nodes,
        )

        if not primary.success or len(primary.path) < 2:
            return []

        alternatives: List[RouteResult] = []
        seen_paths: Set[Tuple[str, ...]] = {tuple(primary.path)}
        base_blocked_edges = set(blocked_edges or [])

        # Iterate over each edge in primary route and remove it to find distinct detour paths
        for i in range(len(primary.path) - 1):
            u, v = primary.path[i], primary.path[i + 1]
            trial_blocked_edges = set(base_blocked_edges)
            trial_blocked_edges.add((u, v))
            trial_blocked_edges.add((v, u))

            alt = self.find_route(
                source=source,
                destination=destination,
                algorithm="dijkstra",
                optimize_for=optimize_for,
                wheelchair_accessible=wheelchair_accessible,
                blocked_edges=trial_blocked_edges,
                blocked_nodes=blocked_nodes,
            )

            if alt.success and tuple(alt.path) not in seen_paths:
                seen_paths.add(tuple(alt.path))
                alternatives.append(alt)

        # Sort alternatives by cost (total_distance or total_time)
        metric_key = (
            (lambda r: r.total_time)
            if optimize_for in ("time", "fastest")
            else (lambda r: r.total_distance)
        )
        alternatives.sort(key=metric_key)

        return alternatives[:max_alternatives]
