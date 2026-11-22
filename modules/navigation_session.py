"""Interactive navigation session state model and real-time wayfinding session controller.

Manages the lifecycle of a campus navigation session:
IDLE -> ROUTE_PREVIEW -> NAVIGATING -> PAUSED / FLOOR_TRANSITION -> ARRIVED
with automated obstacle detection and dynamic rerouting.
"""

from __future__ import annotations

import enum
import time
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

from modules.campus_map import CampusMap
from modules.navigation_instructions import NavigationInstruction, generate_turn_by_turn_instructions
from modules.route_finder import RouteFinder, RouteResult


class NavigationState(str, enum.Enum):
    """Enumeration of active navigation session states."""

    IDLE = "IDLE"
    ROUTE_PREVIEW = "ROUTE_PREVIEW"
    NAVIGATING = "NAVIGATING"
    PAUSED = "PAUSED"
    FLOOR_TRANSITION = "FLOOR_TRANSITION"
    ARRIVED = "ARRIVED"
    REROUTING = "REROUTING"
    NO_ACCESSIBLE_ROUTE = "NO_ACCESSIBLE_ROUTE"


class NavigationSession:
    """Stateful real-time campus navigation session manager."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        origin_id: Optional[str] = None,
        destination_id: Optional[str] = None,
        algorithm: str = "dijkstra",
        wheelchair_mode: bool = True,
    ) -> None:
        self.session_id: str = session_id or str(uuid.uuid4())[:8]
        self.state: NavigationState = NavigationState.IDLE
        self.origin_id: Optional[str] = origin_id
        self.destination_id: Optional[str] = destination_id
        self.algorithm: str = algorithm.lower()
        self.wheelchair_mode: bool = wheelchair_mode

        # Route data
        self.route: Optional[RouteResult] = None
        self.path: List[str] = []
        self.instructions: List[NavigationInstruction] = []

        # Real-time navigation progress
        self.current_step_index: int = 0
        self.current_node_id: Optional[str] = origin_id
        self.current_floor: int = 0
        self.progress_percentage: float = 0.0
        self.completed_distance: float = 0.0
        self.remaining_distance: float = 0.0
        self.total_distance: float = 0.0
        self.total_time: float = 0.0
        self.remaining_time: float = 0.0
        self.completed_steps: int = 0
        self.total_steps: int = 0
        self.floor_transitions_count: int = 0

        # Obstacle detection & dynamic rerouting state
        self.is_rerouted: bool = False
        self.reroute_reason: Optional[str] = None
        self.blocked_edge: Optional[Tuple[str, str]] = None
        self.error_message: Optional[str] = None

        # Timestamps
        self.created_at: float = time.time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None

    def start_preview(
        self,
        origin_id: str,
        destination_id: str,
        campus_map: CampusMap,
        route_finder: RouteFinder,
        algorithm: str = "dijkstra",
        wheelchair_mode: bool = True,
    ) -> bool:
        """Calculate and preview a route before initiating navigation."""
        self.origin_id = origin_id
        self.destination_id = destination_id
        self.algorithm = algorithm.lower()
        self.wheelchair_mode = wheelchair_mode
        self.current_step_index = 0
        self.current_node_id = origin_id
        self.is_rerouted = False
        self.reroute_reason = None
        self.blocked_edge = None
        self.error_message = None

        orig_loc = campus_map.get_location(origin_id) or {}
        self.current_floor = int(orig_loc.get("floor", 0))

        route_res = route_finder.find_route(
            source=origin_id,
            destination=destination_id,
            algorithm=self.algorithm,
            wheelchair_accessible=self.wheelchair_mode,
        )

        if not route_res or not route_res.success:
            self.state = NavigationState.NO_ACCESSIBLE_ROUTE
            self.route = route_res
            self.path = []
            self.instructions = []
            self.error_message = (
                route_res.error_message
                if route_res and route_res.error_message
                else f"No accessible route between '{origin_id}' and '{destination_id}'."
            )
            return False

        self.route = route_res
        self.path = list(route_res.path)
        self.total_distance = route_res.total_distance
        self.remaining_distance = route_res.total_distance
        self.completed_distance = 0.0
        self.total_time = route_res.total_time
        self.remaining_time = route_res.total_time
        self.total_steps = max(0, len(self.path) - 1)
        self.completed_steps = 0
        self.progress_percentage = 0.0

        # Floor transitions count
        trans_count = sum(1 for s in route_res.steps if s.from_floor != s.to_floor)
        self.floor_transitions_count = trans_count

        # Build turn-by-turn instructions
        locs_dict = {loc["id"]: loc for loc in campus_map.get_all_locations()}
        edges_dict = {
            (u, v): campus_map.graph[u][v]
            for u, v in campus_map.graph.edges()
        }
        self.instructions = generate_turn_by_turn_instructions(
            path_nodes=self.path,
            locations_map=locs_dict,
            graph_edges=edges_dict,
        )

        self.state = NavigationState.ROUTE_PREVIEW
        return True

    def start_navigation(self) -> bool:
        """Start active navigation along the calculated route."""
        if self.state not in (NavigationState.ROUTE_PREVIEW, NavigationState.PAUSED):
            return False
        if not self.path or len(self.path) < 2:
            return False

        self.state = NavigationState.NAVIGATING
        if not self.started_at:
            self.started_at = time.time()
        return True

    def pause_navigation(self) -> bool:
        """Pause active navigation."""
        if self.state != NavigationState.NAVIGATING:
            return False
        self.state = NavigationState.PAUSED
        return True

    def resume_navigation(self) -> bool:
        """Resume paused navigation."""
        if self.state != NavigationState.PAUSED:
            return False
        self.state = NavigationState.NAVIGATING
        return True

    def restart_navigation(self) -> bool:
        """Reset navigation progress back to the starting node."""
        if not self.path or len(self.path) < 2:
            return False

        self.current_step_index = 0
        self.current_node_id = self.path[0]
        self.completed_distance = 0.0
        self.remaining_distance = self.total_distance
        self.completed_steps = 0
        self.remaining_time = self.total_time
        self.progress_percentage = 0.0
        self.started_at = time.time()
        self.completed_at = None
        self.state = NavigationState.NAVIGATING
        return True

    def cancel_navigation(self) -> bool:
        """Cancel the active navigation session and return to IDLE."""
        self.state = NavigationState.IDLE
        self.current_step_index = 0
        self.progress_percentage = 0.0
        self.completed_distance = 0.0
        self.completed_steps = 0
        return True

    def step_forward(self, campus_map: CampusMap) -> bool:
        """Advance navigation progress by one step/segment."""
        if self.state not in (NavigationState.NAVIGATING, NavigationState.FLOOR_TRANSITION):
            return False

        if self.current_step_index >= len(self.path) - 1:
            self._trigger_arrival()
            return True

        # Complete current step
        curr_u = self.path[self.current_step_index]
        curr_v = self.path[self.current_step_index + 1]

        edge_data = campus_map.graph.get_edge_data(curr_u, curr_v) or {}
        step_dist = float(edge_data.get("distance", 15.0))
        step_time = float(edge_data.get("estimated_time", step_dist / 1.2))

        self.completed_distance = min(self.total_distance, self.completed_distance + step_dist)
        self.remaining_distance = max(0.0, self.total_distance - self.completed_distance)
        self.remaining_time = max(0.0, self.remaining_time - step_time)
        self.completed_steps += 1
        self.current_step_index += 1
        self.current_node_id = curr_v

        v_loc = campus_map.get_location(curr_v) or {}
        old_floor = self.current_floor
        new_floor = int(v_loc.get("floor", 0))
        self.current_floor = new_floor

        # Progress calculation
        if self.total_distance > 0:
            self.progress_percentage = min(100.0, (self.completed_distance / self.total_distance) * 100.0)
        else:
            self.progress_percentage = 100.0

        # Check if floor transition
        if old_floor != new_floor and self.current_step_index < len(self.path) - 1:
            self.state = NavigationState.FLOOR_TRANSITION
        else:
            self.state = NavigationState.NAVIGATING

        # Check if arrived at destination
        if self.current_step_index >= len(self.path) - 1:
            self._trigger_arrival()

        return True

    def _trigger_arrival(self) -> None:
        """Handle arrival at destination."""
        self.state = NavigationState.ARRIVED
        self.progress_percentage = 100.0
        self.remaining_distance = 0.0
        self.remaining_time = 0.0
        self.completed_steps = self.total_steps
        self.completed_at = time.time()

    def detect_and_handle_obstacles(
        self,
        obstacle_manager: Any,
        campus_map: CampusMap,
        route_finder: RouteFinder,
    ) -> bool:
        """Scan upcoming pathway segments for verified obstacles and dynamically reroute.

        Returns:
            True if an obstacle was detected and rerouting occurred, False otherwise.
        """
        if self.state not in (NavigationState.NAVIGATING, NavigationState.PAUSED, NavigationState.ROUTE_PREVIEW):
            return False

        if not self.path or self.current_step_index >= len(self.path) - 1:
            return False

        # Query all active verified obstacles from obstacle manager
        active_hazards = obstacle_manager.get_active_obstacles()
        blocked_edges: Set[Tuple[str, str]] = set()
        for haz in active_hazards:
            if haz.get("status") == "Verified":
                u = haz.get("source_location_id")
                v = haz.get("destination_location_id")
                if u and v:
                    blocked_edges.add((u, v))
                    blocked_edges.add((v, u))

        if not blocked_edges:
            return False

        # Check if any UPCOMING step in the remaining path intersects a blocked edge
        remaining_blocked_step: Optional[Tuple[str, str]] = None
        for i in range(self.current_step_index, len(self.path) - 1):
            seg = (self.path[i], self.path[i + 1])
            if seg in blocked_edges:
                remaining_blocked_step = seg
                break

        if not remaining_blocked_step:
            return False

        # Obstacle detected on active route!
        self.state = NavigationState.REROUTING
        self.blocked_edge = remaining_blocked_step
        self.reroute_reason = (
            f"Active verified obstacle detected on pathway between "
            f"'{remaining_blocked_step[0]}' and '{remaining_blocked_step[1]}'."
        )

        # Attempt dynamic recalculation starting from the CURRENT node to destination
        current_source = self.current_node_id or self.path[self.current_step_index]
        alt_route = route_finder.find_route(
            source=current_source,
            destination=self.destination_id or "",
            algorithm=self.algorithm,
            wheelchair_accessible=self.wheelchair_mode,
        )

        if not alt_route or not alt_route.success:
            self.state = NavigationState.NO_ACCESSIBLE_ROUTE
            self.error_message = (
                f"Upcoming pathway {remaining_blocked_step[0]} ➔ {remaining_blocked_step[1]} is blocked by a verified obstacle, "
                f"and no alternative accessible route exists to '{self.destination_id}' under current wheelchair constraints."
            )
            return True

        # Splice completed path with the new alternative path
        completed_path_segment = self.path[: self.current_step_index]
        new_full_path = completed_path_segment + alt_route.path

        self.path = new_full_path
        self.route = alt_route
        self.is_rerouted = True

        # Recompute totals and instructions
        locs_dict = {loc["id"]: loc for loc in campus_map.get_all_locations()}
        edges_dict = {
            (u, v): campus_map.graph[u][v]
            for u, v in campus_map.graph.edges()
        }
        self.instructions = generate_turn_by_turn_instructions(
            path_nodes=self.path,
            locations_map=locs_dict,
            graph_edges=edges_dict,
        )

        # Recompute metrics
        new_remaining_dist = alt_route.total_distance
        self.total_distance = self.completed_distance + new_remaining_dist
        self.remaining_distance = new_remaining_dist
        self.remaining_time = alt_route.total_time
        self.total_steps = max(0, len(self.path) - 1)
        self.floor_transitions_count = sum(1 for s in alt_route.steps if s.from_floor != s.to_floor)

        if self.total_distance > 0:
            self.progress_percentage = min(100.0, (self.completed_distance / self.total_distance) * 100.0)

        # Resume in PAUSED state so user observes the rerouting alert, or keep NAVIGATING
        self.state = NavigationState.PAUSED
        return True

    def get_current_instruction(self) -> Optional[NavigationInstruction]:
        """Return the active navigation instruction for the current step."""
        if not self.instructions:
            return None
        idx = min(self.current_step_index, len(self.instructions) - 1)
        return self.instructions[idx]

    def get_next_instruction(self) -> Optional[NavigationInstruction]:
        """Return the upcoming navigation instruction."""
        if not self.instructions:
            return None
        next_idx = self.current_step_index + 1
        if next_idx < len(self.instructions):
            return self.instructions[next_idx]
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert navigation session to a JSON-serializable dictionary."""
        curr_instr = self.get_current_instruction()
        next_instr = self.get_next_instruction()
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "origin_id": self.origin_id,
            "destination_id": self.destination_id,
            "algorithm": self.algorithm,
            "wheelchair_mode": self.wheelchair_mode,
            "current_step_index": self.current_step_index,
            "current_node_id": self.current_node_id,
            "current_floor": self.current_floor,
            "progress_percentage": round(self.progress_percentage, 1),
            "completed_distance": round(self.completed_distance, 1),
            "remaining_distance": round(self.remaining_distance, 1),
            "total_distance": round(self.total_distance, 1),
            "total_time": round(self.total_time, 1),
            "remaining_time": round(self.remaining_time, 1),
            "completed_steps": self.completed_steps,
            "total_steps": self.total_steps,
            "floor_transitions_count": self.floor_transitions_count,
            "path": self.path,
            "current_instruction": curr_instr.to_dict() if curr_instr else None,
            "next_instruction": next_instr.to_dict() if next_instr else None,
            "is_rerouted": self.is_rerouted,
            "reroute_reason": self.reroute_reason,
            "blocked_edge": list(self.blocked_edge) if self.blocked_edge else None,
            "error_message": self.error_message,
        }
