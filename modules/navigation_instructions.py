"""Turn-by-turn navigation instruction generator with geometric turn approximation.

This module converts sequences of campus graph nodes into clear, human-readable
pedestrian wayfinding instructions. Turn directions (left, right, straight) and
compass bearings (North, East, South, West) are calculated using 2D horizontal
vector coordinates based on the campus layout coordinate system.

DISCLOSURE:
Direction and orientation are geometric approximations based on available campus
map coordinates, not live GPS positioning or physical compass hardware.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, List, Optional, Tuple


ORIENTATION_DISCLOSURE: str = (
    "Compass bearings (0°-360° clockwise from campus grid North) and cardinal orientations "
    "are calculated from schematic 3D coordinates relative to campus grid North (-Z axis) "
    "for spatial reference and assistive wayfinding. Direction is approximate based on the "
    "available campus map coordinates."
)


@dataclass
class NavigationInstruction:
    """Structured navigational instruction for a single segment of a route."""

    step_number: int
    from_id: str
    to_id: str
    from_name: str
    to_name: str
    from_floor: int
    to_floor: int
    distance: float
    estimated_time: float
    action_type: str  # 'start', 'straight', 'turn_left', 'turn_right', 'turn_around', 'enter_building', 'exit_building', 'elevator', 'stairs', 'ramp', 'arrive'
    text: str
    icon: str
    turn_angle_deg: float = 0.0
    wheelchair_accessible: bool = True
    has_elevator: bool = False
    has_stairs: bool = False
    has_ramp: bool = False
    heading_deg: float = 0.0
    cardinal_direction: str = ""
    orientation_reference: str = "NH-948 Kanakapura Road Axis"
    building_orientation: str = "FET Façade Facing South-East"
    directional_confidence: str = "APPROXIMATE"
    orientation_disclosure: str = ORIENTATION_DISCLOSURE

    def to_dict(self) -> Dict[str, Any]:
        """Convert instruction to JSON-serializable dictionary."""
        return {
            "step_number": self.step_number,
            "from_id": self.from_id,
            "to_id": self.to_id,
            "from_name": self.from_name,
            "to_name": self.to_name,
            "from_floor": self.from_floor,
            "to_floor": self.to_floor,
            "distance": round(self.distance, 1),
            "estimated_time": round(self.estimated_time, 1),
            "action_type": self.action_type,
            "text": self.text,
            "icon": self.icon,
            "turn_angle_deg": round(self.turn_angle_deg, 1),
            "wheelchair_accessible": self.wheelchair_accessible,
            "has_elevator": self.has_elevator,
            "has_stairs": self.has_stairs,
            "has_ramp": self.has_ramp,
            "heading_deg": round(self.heading_deg, 1),
            "cardinal_direction": self.cardinal_direction,
            "orientation_reference": self.orientation_reference,
            "building_orientation": self.building_orientation,
            "directional_confidence": self.directional_confidence,
            "orientation_disclosure": self.orientation_disclosure,
        }


CARDINAL_DIRECTIONS: List[str] = [
    "North (N)",
    "North-East (NE)",
    "East (E)",
    "South-East (SE)",
    "South (S)",
    "South-West (SW)",
    "West (W)",
    "North-West (NW)",
]


def compute_bearing_and_cardinal(
    p1: Any,
    p2: Any,
) -> Tuple[float, str]:
    """Calculate the compass bearing (0-360 deg) and cardinal direction.

    Three.js Cartesian Coordinate Conventions:
    - +X axis points East (90 deg).
    - -X axis points West (270 deg).
    - +Z axis points South (180 deg).
    - -Z axis points North (0 / 360 deg).

    Args:
        p1: Source coordinate tuple (x1, z1) or dict with 'x', 'y'/'z'.
        p2: Target coordinate tuple (x2, z2) or dict with 'x', 'y'/'z'.

    Returns:
        Tuple of (bearing_degrees, cardinal_direction_string).
    """
    if isinstance(p1, dict):
        x1 = float(p1.get("x", 0.0))
        z1 = float(p1.get("z", p1.get("y", 0.0)))
    else:
        x1, z1 = float(p1[0]), float(p1[1])

    if isinstance(p2, dict):
        x2 = float(p2.get("x", 0.0))
        z2 = float(p2.get("z", p2.get("y", 0.0)))
    else:
        x2, z2 = float(p2[0]), float(p2[1])

    dx = x2 - x1
    dz = z2 - z1

    if abs(dx) < 1e-4 and abs(dz) < 1e-4:
        return 0.0, "Stationary"

    # atan2(dx, -dz) computes angle clockwise from North (-Z)
    heading_rad = math.atan2(dx, -dz)
    heading_deg = math.degrees(heading_rad) % 360.0

    # Classify into 8 cardinal/intercardinal quadrants
    if heading_deg >= 337.5 or heading_deg < 22.5:
        cardinal = "North (N)"
    elif 22.5 <= heading_deg < 67.5:
        cardinal = "North-East (NE)"
    elif 67.5 <= heading_deg < 112.5:
        cardinal = "East (E)"
    elif 112.5 <= heading_deg < 157.5:
        cardinal = "South-East (SE)"
    elif 157.5 <= heading_deg < 202.5:
        cardinal = "South (S)"
    elif 202.5 <= heading_deg < 247.5:
        cardinal = "South-West (SW)"
    elif 247.5 <= heading_deg < 292.5:
        cardinal = "West (W)"
    else:
        cardinal = "North-West (NW)"

    return heading_deg, cardinal


def compute_turn_angle(
    p_prev: Tuple[float, float],
    p_curr: Tuple[float, float],
    p_next: Tuple[float, float],
) -> float:
    """Calculate the horizontal turn angle in degrees between two successive vectors.

    Uses Three.js coordinate convention where +X is East and +Z is South.
    Looking down from above (Y-axis):
    - Positive angle (+25 deg to +155 deg) indicates a Right Turn.
    - Negative angle (-155 deg to -25 deg) indicates a Left Turn.
    - Angle near 0 deg (|angle| < 25 deg) indicates Straight.
    - Angle near 180 deg (|angle| >= 155 deg) indicates Turn Around.

    Args:
        p_prev: (x, z) of previous waypoint.
        p_curr: (x, z) of current waypoint.
        p_next: (x, z) of next waypoint.

    Returns:
        Turn angle in degrees in range [-180, 180].
    """
    v1_x = p_curr[0] - p_prev[0]
    v1_z = p_curr[1] - p_prev[1]

    v2_x = p_next[0] - p_curr[0]
    v2_z = p_next[1] - p_curr[1]

    len_v1 = math.hypot(v1_x, v1_z)
    len_v2 = math.hypot(v2_x, v2_z)

    if len_v1 < 1e-4 or len_v2 < 1e-4:
        return 0.0

    # Normalize vectors
    u1_x, u1_z = v1_x / len_v1, v1_z / len_v1
    u2_x, u2_z = v2_x / len_v2, v2_z / len_v2

    # 2D cross product (u1_x * u2_z - u1_z * u2_x)
    cross = u1_x * u2_z - u1_z * u2_x
    # 2D dot product
    dot = u1_x * u2_x + u1_z * u2_z
    dot = max(-1.0, min(1.0, dot))

    angle_rad = math.atan2(cross, dot)
    return math.degrees(angle_rad)


def format_floor_name(floor_num: int) -> str:
    """Format numeric floor code into human-readable label."""
    if floor_num == -1:
        return "Outdoor Campus"
    if floor_num == 0:
        return "Ground Floor"
    if floor_num == 1:
        return "First Floor"
    if floor_num == 2:
        return "Second Floor"
    if floor_num == 3:
        return "Third Floor"
    if floor_num == 4:
        return "Fourth Floor"
    return f"Floor {floor_num}"


def generate_turn_by_turn_instructions(
    path_nodes: List[str],
    locations_map: Dict[str, Dict[str, Any]],
    graph_edges: Optional[Dict[Tuple[str, str], Dict[str, Any]]] = None,
) -> List[NavigationInstruction]:
    """Generate detailed turn-by-turn navigation instructions for a path.

    Args:
        path_nodes: List of node IDs along the path.
        locations_map: Dictionary mapping node_id to location metadata dict
            (must include 'name', 'floor', and 'coordinates' or 'x'/'z').
        graph_edges: Optional dictionary mapping (u, v) to edge attribute dict.

    Returns:
        List of NavigationInstruction instances.
    """
    if len(path_nodes) < 2:
        return []

    instructions: List[NavigationInstruction] = []

    def get_coords(node_id: str) -> Tuple[float, float]:
        loc = locations_map.get(node_id, {})
        if "coordinates" in loc and isinstance(loc["coordinates"], dict):
            c = loc["coordinates"]
            return float(c.get("x", 0.0)), float(c.get("z", c.get("y", 0.0)))
        return float(loc.get("x", 0.0)), float(loc.get("z", loc.get("y", 0.0)))

    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i + 1]

        u_loc = locations_map.get(u, {})
        v_loc = locations_map.get(v, {})

        u_name = u_loc.get("name", u)
        v_name = v_loc.get("name", v)
        u_floor = int(u_loc.get("floor", 0))
        v_floor = int(v_loc.get("floor", 0))

        p_u = get_coords(u)
        p_v = get_coords(v)
        heading_deg, cardinal_dir = compute_bearing_and_cardinal(p_u, p_v)

        edge_attrs: Dict[str, Any] = {}
        if graph_edges:
            edge_attrs = graph_edges.get((u, v)) or graph_edges.get((v, u)) or {}

        dist = float(edge_attrs.get("distance", 15.0))
        time_est = float(edge_attrs.get("estimated_time", dist / 1.2))
        has_elev = bool(edge_attrs.get("has_elevator", False)) or ("ELEVATOR" in u and "ELEVATOR" in v and u_floor != v_floor)
        has_stairs = bool(edge_attrs.get("has_stairs", False)) or ("STAIR" in u and "STAIR" in v and u_floor != v_floor)
        has_ramp = bool(edge_attrs.get("has_ramp", False)) or ("RAMP" in u or "RAMP" in v)
        wheelchair_acc = bool(edge_attrs.get("wheelchair_accessible", not has_stairs))

        u_fl_str = format_floor_name(u_floor)
        v_fl_str = format_floor_name(v_floor)

        # 1. Vertical Transition: Elevator
        if has_elev:
            action_type = "elevator"
            icon = "🛗"
            text = f"Take the central elevator from {u_name} ({u_fl_str}) to {v_name} ({v_fl_str})."
            turn_angle = 0.0

        # 2. Vertical Transition: Stairs
        elif has_stairs and u_floor != v_floor:
            action_type = "stairs"
            icon = "🪜"
            dir_str = "up" if v_floor > u_floor else "down"
            text = f"Use the staircase to walk {dir_str} from {u_name} to {v_name} ({v_fl_str}) ({dist:.1f} m)."
            turn_angle = 0.0

        # 3. Building Entrance (Outdoor -> Indoor)
        elif u_floor == -1 and v_floor >= 0:
            action_type = "enter_building"
            icon = "🏛️"
            if has_ramp:
                text = f"Follow the accessible entrance ramp into the FET Building at {v_name} ({v_fl_str}) ({dist:.1f} m)."
            else:
                text = f"Enter the FET Building at {v_name} ({v_fl_str}) ({dist:.1f} m)."
            turn_angle = 0.0

        # 4. Building Exit (Indoor -> Outdoor)
        elif u_floor >= 0 and v_floor == -1:
            action_type = "exit_building"
            icon = "🌳"
            text = f"Exit the building onto campus grounds toward {v_name} ({dist:.1f} m)."
            turn_angle = 0.0

        # 5. Accessible Ramp on same level
        elif has_ramp:
            action_type = "ramp"
            icon = "♿"
            text = f"Follow the accessible ramp from {u_name} toward {v_name} ({dist:.1f} m)."
            turn_angle = 0.0

        # 6. Same-floor corridor movement with geometric turn calculation
        else:
            if i == 0:
                action_type = "start"
                icon = "🚩"
                cardinal_cue = f" (heading {cardinal_dir})" if cardinal_dir and cardinal_dir != "Stationary" else ""
                text = f"Start at {u_name}. Head toward {v_name}{cardinal_cue} ({dist:.1f} m)."
                turn_angle = 0.0
            else:
                prev_node = path_nodes[i - 1]
                prev_floor = int(locations_map.get(prev_node, {}).get("floor", 0))

                if prev_floor == u_floor == v_floor:
                    p_prev = get_coords(prev_node)
                    p_curr = get_coords(u)
                    p_next = get_coords(v)
                    turn_angle = compute_turn_angle(p_prev, p_curr, p_next)

                    if turn_angle >= 25.0 and turn_angle < 155.0:
                        action_type = "turn_right"
                        icon = "↗️"
                        text = f"Turn right toward {v_name} and continue along the corridor ({dist:.1f} m)."
                    elif turn_angle <= -25.0 and turn_angle > -155.0:
                        action_type = "turn_left"
                        icon = "↖️"
                        text = f"Turn left toward {v_name} and continue along the corridor ({dist:.1f} m)."
                    elif abs(turn_angle) >= 155.0:
                        action_type = "turn_around"
                        icon = "↩️"
                        text = f"Turn around and proceed toward {v_name} ({dist:.1f} m)."
                    else:
                        action_type = "straight"
                        icon = "⬆️"
                        text = f"Continue straight along the corridor to {v_name} ({dist:.1f} m)."
                else:
                    action_type = "straight"
                    icon = "🚶"
                    text = f"Proceed from {u_name} along the corridor to {v_name} ({dist:.1f} m)."
                    turn_angle = 0.0

        instructions.append(
            NavigationInstruction(
                step_number=i + 1,
                from_id=u,
                to_id=v,
                from_name=u_name,
                to_name=v_name,
                from_floor=u_floor,
                to_floor=v_floor,
                distance=dist,
                estimated_time=time_est,
                action_type=action_type,
                text=text,
                icon=icon,
                turn_angle_deg=turn_angle,
                wheelchair_accessible=wheelchair_acc,
                has_elevator=has_elev,
                has_stairs=has_stairs,
                has_ramp=has_ramp,
                heading_deg=heading_deg,
                cardinal_direction=cardinal_dir,
            )
        )

    # Append final arrival instruction
    dest_id = path_nodes[-1]
    dest_loc = locations_map.get(dest_id, {})
    dest_name = dest_loc.get("name", dest_id)
    dest_floor = int(dest_loc.get("floor", 0))
    dest_fl_str = format_floor_name(dest_floor)

    instructions.append(
        NavigationInstruction(
            step_number=len(instructions) + 1,
            from_id=dest_id,
            to_id=dest_id,
            from_name=dest_name,
            to_name=dest_name,
            from_floor=dest_floor,
            to_floor=dest_floor,
            distance=0.0,
            estimated_time=0.0,
            action_type="arrive",
            text=f"Arrive at your destination: {dest_name} ({dest_fl_str}).",
            icon="🎯",
            turn_angle_deg=0.0,
            wheelchair_accessible=True,
            has_elevator=False,
            has_stairs=False,
            has_ramp=False,
            heading_deg=0.0,
            cardinal_direction="Arrived",
        )
    )

    return instructions
