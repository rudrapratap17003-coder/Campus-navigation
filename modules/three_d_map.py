"""Three.js 3D Campus Navigation Engine & Scene Data Serializer.

Transforms 2D schematic campus graphs into an interactive 3D multi-floor
architectural visualization with real-time route pathfinding, vertical connector
modeling (elevators and stairs), dynamic obstacle avoidance, and camera controls.

DISCLAIMER:
Coordinates and node positions are schematic graph-layout coordinates designed
strictly for connectivity visualization and pathfinding demonstration. They do
not represent surveyed architectural CAD blueprints or surveyed physical dimensions.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import networkx as nx

from modules.campus_map import CampusMap
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder, RouteResult


# 3D Spatial Normalization Constants
SCHEMATIC_CENTER_X: float = 30.0
SCHEMATIC_CENTER_Z: float = 27.5
SCHEMATIC_SCALE: float = 0.85

# Floor Heights
GROUND_FLOOR_Y: float = 0.0
FIRST_FLOOR_Y: float = 8.0
EXPLODED_FLOOR_Y: float = 16.0

# Visual Palette
PALETTE = {
    "primary_bg": "#07130F",
    "secondary_bg": "#0D1F18",
    "card_bg": "#122820",
    "slab_ground": "#0B1D15",
    "slab_first": "#122820",
    "room_default": "#163327",
    "room_border": "#35D99A",
    "accessible_green": "#16A36A",
    "accent_mint": "#35D99A",
    "elevator_blue": "#60A5FA",
    "stairs_amber": "#F5B942",
    "blocked_red": "#F87171",
    "unknown_grey": "#9CAFA5",
    "route_glow": "#F59E0B",
    "white_text": "#F8FAFC",
}

# Category Styling & Dimensions
CATEGORY_CONFIG: Dict[str, Dict[str, Any]] = {
    "entrance": {
        "color": "#16A36A",
        "label": "Campus Entrance",
        "width": 6.0,
        "height": 2.2,
        "depth": 5.0,
        "icon": "🚪",
    },
    "lobby": {
        "color": "#10B981",
        "label": "Reception & Info",
        "width": 7.0,
        "height": 2.5,
        "depth": 6.0,
        "icon": "ℹ️",
    },
    "restroom": {
        "color": "#06B6D4",
        "label": "Restroom",
        "width": 5.0,
        "height": 2.2,
        "depth": 5.0,
        "icon": "🚻",
    },
    "elevator": {
        "color": "#60A5FA",
        "label": "Elevator Lobby",
        "width": 5.5,
        "height": 2.8,
        "depth": 5.5,
        "icon": "🛗",
    },
    "stairs": {
        "color": "#F5B942",
        "label": "Central Staircase",
        "width": 5.5,
        "height": 2.8,
        "depth": 5.5,
        "icon": "🪜",
    },
    "classroom": {
        "color": "#3B82F6",
        "label": "Lecture Hall",
        "width": 8.0,
        "height": 2.5,
        "depth": 7.0,
        "icon": "🎓",
    },
    "auditorium": {
        "color": "#8B5CF6",
        "label": "Auditorium",
        "width": 9.0,
        "height": 3.0,
        "depth": 8.0,
        "icon": "🎭",
    },
    "cafeteria": {
        "color": "#EC4899",
        "label": "Cafeteria",
        "width": 8.5,
        "height": 2.5,
        "depth": 7.5,
        "icon": "☕",
    },
    "lab": {
        "color": "#14B8A6",
        "label": "CS Laboratory",
        "width": 8.0,
        "height": 2.5,
        "depth": 7.0,
        "icon": "💻",
    },
    "library": {
        "color": "#F97316",
        "label": "Library",
        "width": 8.5,
        "height": 2.5,
        "depth": 7.5,
        "icon": "📚",
    },
    "office": {
        "color": "#6366F1",
        "label": "Faculty Offices",
        "width": 8.0,
        "height": 2.5,
        "depth": 6.5,
        "icon": "🏢",
    },
}

# Amenities Dictionary for existing locations
LOCATION_AMENITIES: Dict[str, List[str]] = {
    "LOC_01": ["Automatic Sliding Doors", "Step-Free Level Threshold", "Wayfinding Signage"],
    "LOC_02": ["Low-Height Accessible Counter", "Audio Assistance", "Braille Information Guide"],
    "LOC_03": ["Roll-in Wheelchair Turning Space", "Emergency Call Cord", "Support Grab Bars", "Accessible Washbasin"],
    "LOC_04": ["Braille Tactile Call Buttons", "Voice Floor Announcement", "Wide Doorway (95 cm)", "Emergency Intercom"],
    "LOC_05": ["Continuous Dual Handrails", "High-Contrast Step Edges", "Non-Slip Tread Surfaces"],
    "LOC_06": ["Designated Wheelchair Seating Tier", "Assistive Listening Hearing Loop", "Ramped Hall Aisle"],
    "LOC_07": ["Wheelchair Spaces in Front Row", "Ramped Stage Access", "Companion Seating"],
    "LOC_08": ["Wide Aisles (1.8 m)", "Moveable Seating", "Step-Free Serving Counter", "Outdoor Terrace"],
    "LOC_09": ["Gentle 1:12 Incline Ramp", "Continuous Side Rails", "Textured Tactile Ground Surface"],
    "LOC_10": ["Braille Tactile Call Buttons", "Voice Floor Announcement", "Wide Doorway (95 cm)", "Floor 1 Landing"],
    "LOC_11": ["Continuous Dual Handrails", "High-Contrast Step Edges", "Upper Floor Landing"],
    "LOC_12": ["Adjustable Height Desks", "Screen Reader Software Installed", "Wide Row Spacing"],
    "LOC_13": ["Low-Height Research Desks", "Braille Catalog Access", "Quiet Study Pods"],
    "LOC_14": ["Staff Consultation Area", "Step-Free Office Entry", "Wide Corridors"],
    "LOC_15": ["Standard Restroom Cubicles", "Upper Level Facility"],
}


def normalize_3d_coordinates(
    campus_map: CampusMap,
    scale: float = SCHEMATIC_SCALE,
    center_x: float = SCHEMATIC_CENTER_X,
    center_z: float = SCHEMATIC_CENTER_Z,
) -> Dict[str, Dict[str, float]]:
    """Transform 2D schematic graph coordinates into a normalized 3D coordinate system.

    In the 3D coordinate system:
    - X axis: Horizontal position (left to right, centered on center_x).
    - Y axis: Vertical elevation (height above ground: 0 for Ground Floor, 8.0 for First Floor).
    - Z axis: Depth position (front to back, centered on center_z).

    Missing or invalid coordinates are assigned deterministic fallback positions
    to ensure 3D visualization stability without crashes.

    Args:
        campus_map: CampusMap instance.
        scale: Coordinate scaling factor.
        center_x: Center X offset.
        center_z: Center Z offset.

    Returns:
        Mapping of location_id -> {"x": float, "y": float, "z": float, "floor": int}.
    """
    coords_3d: Dict[str, Dict[str, float]] = {}
    fallback_index = 0

    for loc in campus_map.get_all_locations():
        loc_id = loc["id"]
        raw_x = loc.get("x")
        raw_y = loc.get("y")
        floor = int(loc.get("floor", 0))

        if raw_x is None or raw_y is None:
            norm_x = (10.0 + (fallback_index % 4) * 15.0 - center_x) * scale
            norm_z = (10.0 + (fallback_index // 4) * 15.0 - center_z) * scale
            fallback_index += 1
        else:
            try:
                norm_x = (float(raw_x) - center_x) * scale
                norm_z = (float(raw_y) - center_z) * scale
            except (ValueError, TypeError):
                norm_x = (10.0 + (fallback_index % 4) * 15.0 - center_x) * scale
                norm_z = (10.0 + (fallback_index // 4) * 15.0 - center_z) * scale
                fallback_index += 1

        elevation_y = GROUND_FLOOR_Y if floor == 0 else FIRST_FLOOR_Y

        coords_3d[loc_id] = {
            "x": round(norm_x, 2),
            "y": round(elevation_y, 2),
            "z": round(norm_z, 2),
            "floor": floor,
        }

    return coords_3d


def get_3d_locations_data(
    campus_map: CampusMap,
    coords_3d: Optional[Dict[str, Dict[str, float]]] = None,
) -> List[Dict[str, Any]]:
    """Assemble structured 3D spatial metadata for all campus locations.

    Args:
        campus_map: CampusMap instance.
        coords_3d: Optional precomputed 3D coordinate mapping.

    Returns:
        List of dictionaries with location metadata, 3D bounds, and amenities.
    """
    if coords_3d is None:
        coords_3d = normalize_3d_coordinates(campus_map)

    locations_data: List[Dict[str, Any]] = []

    for loc in campus_map.get_all_locations():
        loc_id = loc["id"]
        pos = coords_3d.get(loc_id, {"x": 0.0, "y": 0.0, "z": 0.0, "floor": 0})
        cat = loc.get("category", "office").lower()
        cfg = CATEGORY_CONFIG.get(cat, CATEGORY_CONFIG["office"])

        # Determine connected neighbors
        neighbors: List[Dict[str, str]] = []
        if loc_id in campus_map.graph:
            for neighbor_id in campus_map.graph.neighbors(loc_id):
                neighbor_loc = campus_map.get_location(neighbor_id) or {}
                neighbors.append(
                    {
                        "id": neighbor_id,
                        "name": neighbor_loc.get("name", neighbor_id),
                        "floor": neighbor_loc.get("floor", 0),
                    }
                )

        amenities = LOCATION_AMENITIES.get(loc_id, ["Standard Academic Facility"])

        loc_entry = {
            "id": loc_id,
            "name": loc.get("name", loc_id),
            "floor": int(loc.get("floor", 0)),
            "building": loc.get("building", "Academic Complex"),
            "category": cat,
            "category_label": cfg["label"],
            "icon": cfg["icon"],
            "pos": pos,
            "dimensions": {
                "width": cfg["width"],
                "height": cfg["height"],
                "depth": cfg["depth"],
            },
            "color": cfg["color"],
            "amenities": amenities,
            "connected_locations": neighbors,
            "wheelchair_accessible": loc_id != "LOC_11",  # Stairs landing has barrier
        }
        locations_data.append(loc_entry)

    return locations_data


def get_3d_pathways_data(
    campus_map: CampusMap,
    coords_3d: Optional[Dict[str, Dict[str, float]]] = None,
    obstacle_manager: Optional[ObstacleManager] = None,
) -> List[Dict[str, Any]]:
    """Assemble structured 3D spatial connections for all 17 campus pathways.

    Identifies intra-floor corridors, ramps, elevator vertical shafts, and staircase flights.
    Synchronizes operational status with ObstacleManager (blocked vs open vs pending).

    Args:
        campus_map: CampusMap instance.
        coords_3d: Optional precomputed 3D coordinate mapping.
        obstacle_manager: Optional ObstacleManager for dynamic barrier status.

    Returns:
        List of dictionaries detailing each pathway's 3D geometry and operational attributes.
    """
    if coords_3d is None:
        coords_3d = normalize_3d_coordinates(campus_map)

    pathways: List[Dict[str, Any]] = []
    seen_edges: Set[Tuple[str, str]] = set()

    # Query pending reports if obstacle_manager is available
    pending_edges: Set[Tuple[str, str]] = set()
    if obstacle_manager:
        try:
            pending_reports = obstacle_manager.get_reports_by_status("Pending")
            for rep in pending_reports:
                if rep.get("target_type") == "pathway":
                    u, v = rep.get("source_location_id"), rep.get("destination_location_id")
                    if u and v:
                        pending_edges.add(tuple(sorted([u, v])))
        except Exception:
            pass

    for u, v, data in campus_map.graph.edges(data=True):
        edge_key = tuple(sorted([u, v]))
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)

        u_pos = coords_3d.get(u, {"x": 0.0, "y": 0.0, "z": 0.0, "floor": 0})
        v_pos = coords_3d.get(v, {"x": 0.0, "y": 0.0, "z": 0.0, "floor": 0})

        is_cross = u_pos["floor"] != v_pos["floor"]
        has_elevator = bool(data.get("has_elevator", False))
        has_stairs = bool(data.get("has_stairs", False))
        has_ramp = bool(data.get("has_ramp", False))
        wheelchair_accessible = bool(data.get("wheelchair_accessible", True))

        # Check if actively blocked
        is_blocked = False
        if obstacle_manager:
            blocked_edges = obstacle_manager.get_active_blocked_edges()
            is_blocked = (u, v) in blocked_edges or (v, u) in blocked_edges or data.get("status") == "blocked"
        else:
            is_blocked = data.get("status") == "blocked"

        is_pending = edge_key in pending_edges

        # Determine pathway type and color
        if is_blocked:
            pathway_type = "blocked"
            color = PALETTE["blocked_red"]
        elif has_elevator:
            pathway_type = "elevator"
            color = PALETTE["elevator_blue"]
        elif has_stairs:
            pathway_type = "stairs"
            color = PALETTE["stairs_amber"]
        elif has_ramp:
            pathway_type = "ramp"
            color = PALETTE["accent_mint"]
        elif wheelchair_accessible:
            pathway_type = "accessible_corridor"
            color = PALETTE["accessible_green"]
        else:
            pathway_type = "corridor"
            color = PALETTE["unknown_grey"]

        u_loc = campus_map.get_location(u) or {}
        v_loc = campus_map.get_location(v) or {}

        pathway_entry = {
            "id": f"{u}__{v}",
            "source": u,
            "destination": v,
            "source_name": u_loc.get("name", u),
            "destination_name": v_loc.get("name", v),
            "source_pos": u_pos,
            "dest_pos": v_pos,
            "source_floor": u_pos["floor"],
            "dest_floor": v_pos["floor"],
            "is_cross_floor": is_cross,
            "pathway_type": pathway_type,
            "has_elevator": has_elevator,
            "has_stairs": has_stairs,
            "has_ramp": has_ramp,
            "wheelchair_accessible": wheelchair_accessible,
            "is_blocked": is_blocked,
            "is_pending": is_pending,
            "color": color,
            "distance": float(data.get("distance", 0.0)),
            "estimated_time": float(data.get("estimated_time", 0.0)),
        }
        pathways.append(pathway_entry)

    return pathways


def get_3d_route_data(
    campus_map: CampusMap,
    route_finder: RouteFinder,
    start_id: str,
    dest_id: str,
    algorithm: str = "dijkstra",
    wheelchair_accessible: bool = False,
    coords_3d: Optional[Dict[str, Dict[str, float]]] = None,
) -> Dict[str, Any]:
    """Execute authoritative Python route calculation and assemble 3D spline waypoints.

    When routes cross floors via elevator or stairs, generates vertical intermediate
    waypoints so that the 3D camera and route tube transition vertically through
    the elevator shaft or staircase.

    Args:
        campus_map: CampusMap instance.
        route_finder: RouteFinder instance.
        start_id: Origin location ID.
        dest_id: Destination location ID.
        algorithm: Pathfinding algorithm ('dijkstra' or 'bfs').
        wheelchair_accessible: Whether to constrain search to wheelchair accessible pathways.
        coords_3d: Optional precomputed 3D coordinate mapping.

    Returns:
        Structured dictionary containing path list, waypoints, steps, and metrics.
    """
    if coords_3d is None:
        coords_3d = normalize_3d_coordinates(campus_map)

    route_res: RouteResult = route_finder.find_route(
        source=start_id,
        destination=dest_id,
        algorithm=algorithm,
        wheelchair_accessible=wheelchair_accessible,
        optimize_for="distance",
    )

    if not route_res or not route_res.success:
        return {
            "success": False,
            "error_message": route_res.error_message or "No accessible route found between selected points.",
            "path": [],
            "waypoints": [],
            "steps": [],
            "cross_floor_transitions": [],
            "total_distance": 0.0,
            "total_time": 0.0,
            "edge_count": 0,
            "is_accessible": False,
            "algorithm_used": algorithm,
        }

    path_nodes = route_res.path
    waypoints: List[Dict[str, Any]] = []

    for i, loc_id in enumerate(path_nodes):
        loc_pos = coords_3d.get(loc_id, {"x": 0.0, "y": 0.0, "z": 0.0, "floor": 0})
        loc_info = campus_map.get_location(loc_id) or {}

        # Add waypoint at location center (elevated slightly above floor for visual clearance)
        # Ground floor: Y = 0.5; First floor: Y = 8.5
        wp_y = (loc_pos["y"] + 0.5)

        waypoint_data = {
            "id": loc_id,
            "name": loc_info.get("name", loc_id),
            "floor": loc_pos["floor"],
            "x": loc_pos["x"],
            "y": round(wp_y, 2),
            "z": loc_pos["z"],
            "step_index": i,
        }
        waypoints.append(waypoint_data)

        # If next node is a vertical connector (e.g. Elevator or Stairs), insert intermediate vertical waypoints
        if i < len(path_nodes) - 1:
            next_id = path_nodes[i + 1]
            next_pos = coords_3d.get(next_id, {"x": 0.0, "y": 0.0, "z": 0.0, "floor": 0})
            if loc_pos["floor"] != next_pos["floor"]:
                # Intermediate point at mid-height of elevator / stair shaft
                mid_y = (loc_pos["y"] + next_pos["y"]) / 2.0 + 0.5
                waypoints.append(
                    {
                        "id": f"{loc_id}_TRANSITION_{next_id}",
                        "name": f"Vertical Transition ({loc_info.get('name', loc_id)} -> {next_id})",
                        "floor": -1,
                        "x": round((loc_pos["x"] + next_pos["x"]) / 2.0, 2),
                        "y": round(mid_y, 2),
                        "z": round((loc_pos["z"] + next_pos["z"]) / 2.0, 2),
                        "step_index": i + 0.5,
                        "is_transition": True,
                    }
                )

    # Convert RouteSteps to serializable dicts
    steps_data: List[Dict[str, Any]] = []
    for step in route_res.steps:
        steps_data.append(
            {
                "step_number": step.step_number,
                "from_id": step.from_id,
                "to_id": step.to_id,
                "from_name": step.from_name,
                "to_name": step.to_name,
                "from_floor": step.from_floor,
                "to_floor": step.to_floor,
                "distance": round(step.distance, 1),
                "estimated_time": round(step.estimated_time, 1),
                "wheelchair_accessible": step.wheelchair_accessible,
                "has_stairs": step.has_stairs,
                "has_ramp": step.has_ramp,
                "has_elevator": step.has_elevator,
                "instruction": step.instruction,
            }
        )

    # Detect cross-floor transitions
    transitions: List[Dict[str, Any]] = []
    for step in route_res.steps:
        if step.from_floor != step.to_floor:
            conn_type = "Elevator" if step.has_elevator else "Stairs" if step.has_stairs else "Connector"
            transitions.append(
                {
                    "from_floor": step.from_floor,
                    "to_floor": step.to_floor,
                    "connector_type": conn_type,
                    "from_name": step.from_name,
                    "to_name": step.to_name,
                    "wheelchair_accessible": step.wheelchair_accessible,
                    "instruction": step.instruction,
                }
            )

    return {
        "success": True,
        "error_message": None,
        "path": path_nodes,
        "waypoints": waypoints,
        "steps": steps_data,
        "cross_floor_transitions": transitions,
        "total_distance": round(route_res.total_distance, 1),
        "total_time": round(route_res.total_time, 1),
        "edge_count": route_res.edge_count,
        "is_accessible": route_res.is_accessible,
        "algorithm_used": route_res.algorithm_used.upper(),
    }


def build_3d_scene_payload(
    campus_map: CampusMap,
    route_finder: Optional[RouteFinder] = None,
    obstacle_manager: Optional[ObstacleManager] = None,
    start_id: Optional[str] = None,
    dest_id: Optional[str] = None,
    algorithm: str = "dijkstra",
    wheelchair_accessible: bool = False,
    selected_location_id: Optional[str] = None,
    view_mode: str = "combined",
) -> Dict[str, Any]:
    """Construct complete, validated JSON-serializable payload for the Three.js 3D viewport.

    Args:
        campus_map: CampusMap instance.
        route_finder: Optional RouteFinder instance.
        obstacle_manager: Optional ObstacleManager for dynamic barrier status.
        start_id: Optional origin location ID.
        dest_id: Optional destination location ID.
        algorithm: 'dijkstra' or 'bfs'.
        wheelchair_accessible: Whether wheelchair constraints apply.
        selected_location_id: Optional location to highlight.
        view_mode: Initial view mode ('combined', 'exploded', 'ground_only', 'first_only').

    Returns:
        Consolidated dictionary ready for json.dumps().
    """
    coords_3d = normalize_3d_coordinates(campus_map)
    locations = get_3d_locations_data(campus_map, coords_3d)
    pathways = get_3d_pathways_data(campus_map, coords_3d, obstacle_manager)

    active_route: Optional[Dict[str, Any]] = None
    if route_finder and start_id and dest_id and start_id != dest_id:
        active_route = get_3d_route_data(
            campus_map=campus_map,
            route_finder=route_finder,
            start_id=start_id,
            dest_id=dest_id,
            algorithm=algorithm,
            wheelchair_accessible=wheelchair_accessible,
            coords_3d=coords_3d,
        )

    # Active obstacles list for HUD
    active_obstacles: List[Dict[str, Any]] = []
    if obstacle_manager:
        try:
            active_obstacles = obstacle_manager.get_active_obstacles()
        except Exception:
            active_obstacles = []

    payload = {
        "metadata": {
            "app_name": "Accessible Campus Navigator 3D",
            "version": "1.0-3D",
            "disclaimer": (
                "Schematic 3D representation based on illustrative layout coordinates; "
                "not architectural blueprints or surveyed physical dimensions."
            ),
            "floor_count": 2,
            "floors": [
                {"level": 0, "name": "Ground Floor", "height": GROUND_FLOOR_Y},
                {"level": 1, "name": "First Floor", "height": FIRST_FLOOR_Y},
            ],
            "exploded_height": EXPLODED_FLOOR_Y,
            "palette": PALETTE,
        },
        "config": {
            "initial_view_mode": view_mode,
            "selected_location_id": selected_location_id,
            "has_active_route": bool(active_route and active_route.get("success")),
        },
        "locations": locations,
        "pathways": pathways,
        "active_route": active_route,
        "active_obstacles": active_obstacles,
    }

    return payload


def render_three_d_scene_html(scene_data: Dict[str, Any], height: int = 700) -> str:
    """Generate self-contained Three.js HTML/CSS/JS application embedding the 3D scene.

    Includes:
    - Three.js r128 & OrbitControls via CDN with fallback graceful handling.
    - Responsive WebGL canvas with antialiasing and tone mapping.
    - Ground and First floor platforms with stylish semi-translucent glass slabs and gridlines.
    - 15 3D Room volumes customized by architectural category.
    - 17 Corridors with color-coded operational state (green, blue, amber, red).
    - Transparent glass Elevator shaft tower connecting Ground and First floor elevator lobbies.
    - 3D Central staircase connecting Ground and First floor stair landings.
    - High-contrast 2D Canvas text sprites for all location names (crisp at any camera angle).
    - Glowing 3D Tube route overlay with animated traversal orb when a route is planned.
    - Glassmorphic on-screen HUD buttons:
        - View Presets: Isometric, Top-Down, Front, Reset Camera
        - Floor Mode: Combined, Exploded View, Ground Floor Only, First Floor Only
        - Route Animation: Play / Pause
    - Raycaster click interaction: Clicking any room displays its details in an interactive HUD drawer.
    - WebGL capability detection with clear fallback message if WebGL is unavailable.

    Args:
        scene_data: JSON-serializable scene payload from build_3d_scene_payload.
        height: Height in pixels for the container iframe.

    Returns:
        Complete HTML string ready for streamlit.components.v1.html.
    """
    serialized_data = json.dumps(scene_data, ensure_ascii=False)

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Accessible Campus Navigator 3D</title>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
    }}
    body, html {{
      width: 100%;
      height: 100%;
      overflow: hidden;
      background-color: #07130F;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #F8FAFC;
    }}
    #viewport-container {{
      position: relative;
      width: 100%;
      height: 100%;
      background: radial-gradient(circle at 50% 30%, #0d261e 0%, #07130F 100%);
    }}
    canvas#webgl-canvas {{
      display: block;
      width: 100%;
      height: 100%;
      outline: none;
    }}
    /* Top HUD Navigation Bar */
    .hud-bar-top {{
      position: absolute;
      top: 14px;
      left: 14px;
      right: 14px;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      pointer-events: none;
      z-index: 10;
    }}
    .hud-group {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: rgba(13, 31, 24, 0.85);
      border: 1px solid rgba(53, 217, 154, 0.25);
      border-radius: 12px;
      padding: 6px 10px;
      backdrop-filter: blur(10px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
      pointer-events: auto;
    }}
    .hud-title {{
      font-size: 13px;
      font-weight: 700;
      color: #35D99A;
      margin-right: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .hud-btn {{
      background: rgba(22, 163, 106, 0.15);
      border: 1px solid rgba(53, 217, 154, 0.3);
      color: #F8FAFC;
      border-radius: 8px;
      padding: 5px 10px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }}
    .hud-btn:hover {{
      background: rgba(53, 217, 154, 0.35);
      border-color: #35D99A;
      transform: translateY(-1px);
    }}
    .hud-btn.active {{
      background: #16A36A;
      color: #FFFFFF;
      border-color: #35D99A;
      box-shadow: 0 0 10px rgba(53, 217, 154, 0.4);
    }}
    /* Location Inspector Card */
    #location-card {{
      position: absolute;
      bottom: 18px;
      left: 18px;
      width: 320px;
      max-width: calc(100% - 36px);
      background: rgba(13, 31, 24, 0.92);
      border: 1px solid rgba(53, 217, 154, 0.35);
      border-radius: 14px;
      padding: 14px 16px;
      backdrop-filter: blur(12px);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
      z-index: 10;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      transform: translateY(0);
      opacity: 1;
    }}
    #location-card.hidden {{
      transform: translateY(20px);
      opacity: 0;
      pointer-events: none;
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 8px;
      border-bottom: 1px solid rgba(53, 217, 154, 0.2);
      padding-bottom: 6px;
    }}
    .card-title {{
      font-size: 14px;
      font-weight: 700;
      color: #F8FAFC;
      line-height: 1.3;
    }}
    .card-badge {{
      display: inline-block;
      font-size: 10px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 6px;
      text-transform: uppercase;
      background: rgba(53, 217, 154, 0.2);
      color: #35D99A;
      border: 1px solid rgba(53, 217, 154, 0.4);
    }}
    .card-close {{
      background: transparent;
      border: none;
      color: #9CAFA5;
      font-size: 16px;
      cursor: pointer;
      padding: 0 4px;
      line-height: 1;
    }}
    .card-close:hover {{
      color: #F8FAFC;
    }}
    .card-row {{
      font-size: 11px;
      color: #9CAFA5;
      margin-bottom: 4px;
      display: flex;
      justify-content: space-between;
    }}
    .card-row span.val {{
      color: #F8FAFC;
      font-weight: 600;
    }}
    .amenities-list {{
      margin-top: 8px;
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }}
    .amenity-tag {{
      font-size: 10px;
      background: rgba(22, 163, 106, 0.2);
      border: 1px solid rgba(53, 217, 154, 0.25);
      color: #A7F3D0;
      border-radius: 4px;
      padding: 2px 6px;
    }}
    /* Quick Legend HUD */
    .hud-legend {{
      position: absolute;
      bottom: 18px;
      right: 18px;
      background: rgba(13, 31, 24, 0.85);
      border: 1px solid rgba(53, 217, 154, 0.25);
      border-radius: 12px;
      padding: 8px 12px;
      backdrop-filter: blur(10px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
      z-index: 10;
      display: flex;
      flex-direction: column;
      gap: 5px;
      font-size: 11px;
      color: #9CAFA5;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 7px;
    }}
    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 3px;
    }}
    /* Hover Tooltip */
    #hover-tooltip {{
      position: absolute;
      display: none;
      background: rgba(7, 19, 15, 0.95);
      border: 1px solid #35D99A;
      color: #F8FAFC;
      padding: 4px 8px;
      font-size: 11px;
      font-weight: 600;
      border-radius: 6px;
      pointer-events: none;
      z-index: 20;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
      transform: translate(-50%, -120%);
      white-space: nowrap;
    }}
    /* Fallback Banner */
    #webgl-fallback {{
      display: none;
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: #122820;
      border: 1px solid #F87171;
      border-radius: 14px;
      padding: 24px;
      text-align: center;
      max-width: 420px;
      color: #F8FAFC;
      z-index: 100;
    }}
    #webgl-fallback h3 {{
      color: #F87171;
      margin-bottom: 8px;
    }}
    #webgl-fallback p {{
      font-size: 13px;
      color: #9CAFA5;
      line-height: 1.5;
    }}
  </style>
</head>
<body>
  <div id="viewport-container">
    <canvas id="webgl-canvas"></canvas>

    <!-- Top HUD Controls -->
    <div class="hud-bar-top">
      <!-- Camera Presets -->
      <div class="hud-group">
        <span class="hud-title">📐 Camera:</span>
        <button class="hud-btn active" id="btn-iso" title="Isometric 3D Perspective">Isometric</button>
        <button class="hud-btn" id="btn-top" title="Top-Down Overhead View">Top View</button>
        <button class="hud-btn" id="btn-front" title="Front Elevation View">Front</button>
        <button class="hud-btn" id="btn-reset" title="Reset Camera Position">🔄 Reset</button>
      </div>

      <!-- Floor Controls -->
      <div class="hud-group">
        <span class="hud-title">🏢 Floors:</span>
        <button class="hud-btn active" id="btn-floor-combined" title="Combined Multi-Floor View">Combined</button>
        <button class="hud-btn" id="btn-floor-exploded" title="Exploded Multi-Floor View">💥 Exploded</button>
        <button class="hud-btn" id="btn-floor-0" title="Ground Floor Only">Level 0</button>
        <button class="hud-btn" id="btn-floor-1" title="First Floor Only">Level 1</button>
      </div>

      <!-- Animation / Labels -->
      <div class="hud-group">
        <button class="hud-btn" id="btn-anim-toggle" title="Pause / Resume Route Pulse Animation">⏯️ Animation</button>
        <button class="hud-btn active" id="btn-labels-toggle" title="Toggle 3D Room Name Badges">🏷️ Labels</button>
      </div>
    </div>

    <!-- Location Inspector Drawer -->
    <div id="location-card" class="hidden">
      <div class="card-header">
        <div>
          <span class="card-badge" id="card-badge">Level 0</span>
          <div class="card-title" id="card-title">Location Name</div>
        </div>
        <button class="card-close" id="card-close" title="Close Panel">✕</button>
      </div>
      <div class="card-row">
        <span>Facility ID:</span>
        <span class="val" id="card-id">LOC_01</span>
      </div>
      <div class="card-row">
        <span>Category:</span>
        <span class="val" id="card-category">Entrance</span>
      </div>
      <div class="card-row">
        <span>Wheelchair Access:</span>
        <span class="val" id="card-access" style="color: #35D99A;">Step-Free Accessible</span>
      </div>
      <div class="card-row">
        <span>Connected Paths:</span>
        <span class="val" id="card-connections">3 connections</span>
      </div>
      <div style="margin-top: 6px; font-size: 11px; color: #9CAFA5; font-weight: 600;">Available Amenities:</div>
      <div class="amenities-list" id="card-amenities">
        <!-- Rendered dynamically -->
      </div>
    </div>

    <!-- 3D Legend -->
    <div class="hud-legend">
      <div style="font-weight: 700; color: #35D99A; margin-bottom: 2px;">Campus Pathways:</div>
      <div class="legend-item"><div class="legend-dot" style="background: #16A36A;"></div><span>Accessible Corridor</span></div>
      <div class="legend-item"><div class="legend-dot" style="background: #35D99A;"></div><span>Step-Free Ramp</span></div>
      <div class="legend-item"><div class="legend-dot" style="background: #60A5FA;"></div><span>Elevator Shaft</span></div>
      <div class="legend-item"><div class="legend-dot" style="background: #F5B942;"></div><span>Central Staircase</span></div>
      <div class="legend-item"><div class="legend-dot" style="background: #F87171;"></div><span>Verified Blocked Path</span></div>
      <div class="legend-item" id="legend-route" style="display: none;"><div class="legend-dot" style="background: #F59E0B;"></div><span>Active Calculated Route</span></div>
    </div>

    <!-- Hover Tooltip -->
    <div id="hover-tooltip"></div>

    <!-- WebGL Fallback Notification -->
    <div id="webgl-fallback">
      <h3>⚠️ WebGL Acceleration Unavailable</h3>
      <p>Your browser or display environment could not initialize hardware-accelerated WebGL. Please ensure hardware acceleration is enabled, or switch to the 2D schematic Campus Map in the sidebar.</p>
    </div>
  </div>

  <!-- Three.js r128 and OrbitControls CDN -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

  <script>
    (function() {{
      // Injected Scene Payload
      const DATA = {serialized_data};

      // Verify WebGL availability
      function isWebGLAvailable() {{
        try {{
          const canvas = document.createElement('canvas');
          return !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
        }} catch (e) {{
          return false;
        }}
      }}

      if (!isWebGLAvailable() || typeof THREE === 'undefined') {{
        document.getElementById('webgl-fallback').style.display = 'block';
        return;
      }}

      const container = document.getElementById('viewport-container');
      const canvas = document.getElementById('webgl-canvas');

      // 1. Scene, Camera, and Renderer Setup
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x07130F);
      scene.fog = new THREE.FogExp2(0x07130F, 0.007);

      const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
      camera.position.set(34, 30, 36);

      const renderer = new THREE.WebGLRenderer({{
        canvas: canvas,
        antialias: true,
        alpha: false,
        powerPreference: 'high-performance'
      }});
      renderer.setSize(container.clientWidth, container.clientHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.1;
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;

      const controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.06;
      controls.maxPolarAngle = Math.PI / 2 - 0.04; // Prevent going underground
      controls.minDistance = 10;
      controls.maxDistance = 120;
      controls.target.set(0, 3.5, 0);

      // Lighting Rig
      const ambientLight = new THREE.AmbientLight(0x133829, 0.85);
      scene.add(ambientLight);

      const mainLight = new THREE.DirectionalLight(0xFFFFFF, 1.0);
      mainLight.position.set(30, 45, 25);
      mainLight.castShadow = true;
      mainLight.shadow.mapSize.width = 1024;
      mainLight.shadow.mapSize.height = 1024;
      mainLight.shadow.camera.near = 5;
      mainLight.shadow.camera.far = 120;
      mainLight.shadow.camera.left = -35;
      mainLight.shadow.camera.right = 35;
      mainLight.shadow.camera.top = 35;
      mainLight.shadow.camera.bottom = -35;
      scene.add(mainLight);

      const fillLight = new THREE.DirectionalLight(0x60A5FA, 0.45);
      fillLight.position.set(-25, 25, -25);
      scene.add(fillLight);

      // Hierarchical Floor Groups for Exploded / Filtering support
      const floor0Group = new THREE.Group();
      const floor1Group = new THREE.Group();
      const connectorsGroup = new THREE.Group();
      const labelsGroup = new THREE.Group();
      const routeGroup = new THREE.Group();

      scene.add(floor0Group);
      scene.add(floor1Group);
      scene.add(connectorsGroup);
      scene.add(labelsGroup);
      scene.add(routeGroup);

      // Materials Cache
      const materials = {{
        slab0: new THREE.MeshStandardMaterial({{
          color: 0x0B1D15,
          roughness: 0.65,
          metalness: 0.2
        }}),
        slab1: new THREE.MeshStandardMaterial({{
          color: 0x0D241A,
          roughness: 0.5,
          metalness: 0.25,
          transparent: true,
          opacity: 0.85
        }}),
        glassShaft: new THREE.MeshStandardMaterial({{
          color: 0x60A5FA,
          transparent: true,
          opacity: 0.35,
          roughness: 0.1,
          metalness: 0.8
        }}),
        elevatorCab: new THREE.MeshStandardMaterial({{
          color: 0x3B82F6,
          emissive: 0x1D4ED8,
          emissiveIntensity: 0.6,
          roughness: 0.3
        }}),
        stairsMaterial: new THREE.MeshStandardMaterial({{
          color: 0xF5B942,
          roughness: 0.6
        }}),
        wireframeBorder: new THREE.LineBasicMaterial({{
          color: 0x35D99A,
          linewidth: 1.5
        }}),
        selectedGlow: new THREE.MeshBasicMaterial({{
          color: 0xF59E0B,
          wireframe: true
        }})
      }};

      // 2. Build Floor Slabs
      // Ground Floor Slab (52 x 0.4 x 42)
      const slab0Geo = new THREE.BoxGeometry(52, 0.4, 42);
      const slab0 = new THREE.Mesh(slab0Geo, materials.slab0);
      slab0.position.set(0, -0.2, 0);
      slab0.receiveShadow = true;
      floor0Group.add(slab0);

      // Ground Floor Grid Accent
      const grid0 = new THREE.GridHelper(50, 25, 0x16A36A, 0x122820);
      grid0.position.set(0, 0.01, 0);
      floor0Group.add(grid0);

      // First Floor Slab
      const slab1Geo = new THREE.BoxGeometry(52, 0.4, 42);
      const slab1 = new THREE.Mesh(slab1Geo, materials.slab1);
      slab1.position.set(0, 7.8, 0);
      slab1.receiveShadow = true;
      floor1Group.add(slab1);

      const grid1 = new THREE.GridHelper(50, 25, 0x35D99A, 0x163327);
      grid1.position.set(0, 8.01, 0);
      floor1Group.add(grid1);

      // Floor Floating Badges
      function createFloorLabelBadge(text, colorHex, posY) {{
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 128;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'rgba(13, 31, 24, 0.85)';
        ctx.roundRect ? ctx.roundRect(10, 10, 492, 108, 20) : ctx.rect(10, 10, 492, 108);
        ctx.fill();
        ctx.strokeStyle = colorHex;
        ctx.lineWidth = 6;
        ctx.stroke();

        ctx.font = 'bold 44px sans-serif';
        ctx.fillStyle = colorHex;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, 256, 64);

        const tex = new THREE.CanvasTexture(canvas);
        const mat = new THREE.SpriteMaterial({{ map: tex, depthTest: false }});
        const sprite = new THREE.Sprite(mat);
        sprite.scale.set(12, 3, 1);
        sprite.position.set(-20, posY, -18);
        return sprite;
      }}

      const badge0 = createFloorLabelBadge('GROUND FLOOR (LEVEL 0)', '#35D99A', 1.5);
      floor0Group.add(badge0);

      const badge1 = createFloorLabelBadge('FIRST FLOOR (LEVEL 1)', '#60A5FA', 9.5);
      floor1Group.add(badge1);

      // 3. Render 15 Campus Rooms & Locations
      const interactiveRoomMeshes = [];
      const roomById = {{}};

      function createTextSprite(text, categoryColor) {{
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 64;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'rgba(7, 19, 15, 0.88)';
        ctx.roundRect ? ctx.roundRect(4, 4, 248, 56, 10) : ctx.rect(4, 4, 248, 56);
        ctx.fill();
        ctx.strokeStyle = categoryColor || '#35D99A';
        ctx.lineWidth = 3;
        ctx.stroke();

        ctx.font = 'bold 24px sans-serif';
        ctx.fillStyle = '#F8FAFC';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text.length > 18 ? text.substring(0, 17) + '...' : text, 128, 32);

        const tex = new THREE.CanvasTexture(canvas);
        const mat = new THREE.SpriteMaterial({{ map: tex, depthTest: false }});
        const sprite = new THREE.Sprite(mat);
        sprite.scale.set(5.5, 1.4, 1);
        return sprite;
      }}

      DATA.locations.forEach(loc => {{
        const floorGroup = loc.floor === 0 ? floor0Group : floor1Group;
        const dim = loc.dimensions;
        const baseGeo = new THREE.BoxGeometry(dim.width, dim.height, dim.depth);
        const color = new THREE.Color(loc.color);

        const roomMat = new THREE.MeshStandardMaterial({{
          color: color.clone().multiplyScalar(0.7),
          roughness: 0.4,
          metalness: 0.3,
          transparent: true,
          opacity: 0.85
        }});

        const roomMesh = new THREE.Mesh(baseGeo, roomMat);
        const roomY = loc.pos.y + dim.height / 2;
        roomMesh.position.set(loc.pos.x, roomY, loc.pos.z);
        roomMesh.castShadow = true;
        roomMesh.receiveShadow = true;

        // Wireframe edges for architectural definition
        const edges = new THREE.EdgesGeometry(baseGeo);
        const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({{
          color: color.clone().multiplyScalar(1.2),
          linewidth: 1.5
        }}));
        roomMesh.add(line);

        // Floating Node Gem / Marker
        const gemGeo = new THREE.OctahedronGeometry(0.5, 0);
        const gemMat = new THREE.MeshStandardMaterial({{
          color: color,
          emissive: color,
          emissiveIntensity: 0.6,
          roughness: 0.2
        }});
        const gem = new THREE.Mesh(gemGeo, gemMat);
        gem.position.set(0, dim.height / 2 + 0.8, 0);
        roomMesh.add(gem);

        // Floating text label sprite
        const sprite = createTextSprite(loc.name, loc.color);
        sprite.position.set(loc.pos.x, roomY + dim.height / 2 + 1.8, loc.pos.z);
        labelsGroup.add(sprite);

        // Store reference
        roomMesh.userData = {{
          locationId: loc.id,
          locationData: loc,
          sprite: sprite,
          gem: gem,
          originalColor: color.clone().multiplyScalar(0.7),
          hoverColor: color.clone().multiplyScalar(1.2)
        }};

        floorGroup.add(roomMesh);
        interactiveRoomMeshes.push(roomMesh);
        roomById[loc.id] = roomMesh;
      }});

      // 4. Render 17 Campus Pathways (Corridors, Ramps, Vertical Elevator, and Stairs)
      DATA.pathways.forEach(edge => {{
        const uPos = edge.source_pos;
        const vPos = edge.dest_pos;

        if (edge.is_cross_floor) {{
          // Vertical Connector (Elevator or Staircase)
          if (edge.has_elevator) {{
            // Elevator Glass Shaft Tower (LOC_04 <-> LOC_10)
            const shaftHeight = 8.4;
            const shaftGeo = new THREE.BoxGeometry(4.2, shaftHeight, 4.2);
            const shaft = new THREE.Mesh(shaftGeo, materials.glassShaft);
            shaft.position.set(uPos.x, shaftHeight / 2, uPos.z);
            connectorsGroup.add(shaft);

            const shaftEdges = new THREE.EdgesGeometry(shaftGeo);
            const shaftLine = new THREE.LineSegments(shaftEdges, new THREE.LineBasicMaterial({{
              color: 0x60A5FA,
              linewidth: 2
            }}));
            shaft.add(shaftLine);

            // Glowing Elevator Cab
            const cabGeo = new THREE.BoxGeometry(3.2, 2.4, 3.2);
            const cab = new THREE.Mesh(cabGeo, materials.elevatorCab);
            cab.position.set(uPos.x, 2.0, uPos.z);
            connectorsGroup.add(cab);
            cab.userData.isElevatorCab = true;
          }} else if (edge.has_stairs) {{
            // Central Staircase Flight (LOC_05 <-> LOC_11)
            const stairSteps = 12;
            const stepWidth = 3.6;
            const stepDepth = 0.8;
            const stepHeight = 8.0 / stairSteps;

            for (let s = 0; s < stairSteps; s++) {{
              const stepGeo = new THREE.BoxGeometry(stepWidth, stepHeight, stepDepth);
              const stepMesh = new THREE.Mesh(stepGeo, materials.stairsMaterial);
              const sY = s * stepHeight + stepHeight / 2;
              const sZ = uPos.z + (s - stairSteps / 2) * 0.45;
              stepMesh.position.set(uPos.x, sY, sZ);
              stepMesh.receiveShadow = true;
              connectorsGroup.add(stepMesh);
            }}
          }}
        }} else {{
          // Intra-floor horizontal corridor
          const floorGroup = edge.source_floor === 0 ? floor0Group : floor1Group;
          const yLevel = edge.source_floor === 0 ? 0.08 : 8.08;

          const p1 = new THREE.Vector3(uPos.x, yLevel, uPos.z);
          const p2 = new THREE.Vector3(vPos.x, yLevel, vPos.z);

          const distance = p1.distanceTo(p2);
          const corridorWidth = 1.4;

          const corridorGeo = new THREE.PlaneGeometry(corridorWidth, distance);
          const corridorMat = new THREE.MeshStandardMaterial({{
            color: new THREE.Color(edge.color),
            roughness: 0.6,
            metalness: 0.2,
            side: THREE.DoubleSide
          }});

          const corridorMesh = new THREE.Mesh(corridorGeo, corridorMat);
          const midX = (p1.x + p2.x) / 2;
          const midZ = (p1.z + p2.z) / 2;
          corridorMesh.position.set(midX, yLevel, midZ);
          corridorMesh.rotation.x = -Math.PI / 2;

          // Rotate plane to align between p1 and p2
          const angle = Math.atan2(p2.x - p1.x, p2.z - p1.z);
          corridorMesh.rotation.z = -angle;
          corridorMesh.receiveShadow = true;

          floorGroup.add(corridorMesh);

          // If blocked, add red hazard barrier markers along the corridor
          if (edge.is_blocked) {{
            const barrierGeo = new THREE.BoxGeometry(1.6, 0.8, 0.4);
            const barrierMat = new THREE.MeshStandardMaterial({{
              color: 0xF87171,
              emissive: 0xDC2626,
              emissiveIntensity: 0.8,
              roughness: 0.3
            }});
            const barrier = new THREE.Mesh(barrierGeo, barrierMat);
            barrier.position.set(midX, yLevel + 0.4, midZ);
            barrier.rotation.y = angle;
            floorGroup.add(barrier);
          }}
        }}
      }});

      // 5. Active Route Visualization
      let routeCurve = null;
      let traversalSphere = null;
      let routeAnimTime = 0;
      let isRouteAnimating = true;

      if (DATA.active_route && DATA.active_route.success && DATA.active_route.waypoints.length > 1) {{
        document.getElementById('legend-route').style.display = 'flex';

        const waypoints = DATA.active_route.waypoints;
        const curvePoints = waypoints.map(wp => new THREE.Vector3(wp.x, wp.y, wp.z));
        routeCurve = new THREE.CatmullRomCurve3(curvePoints, false, 'catmullrom', 0.2);

        // Glowing 3D Tube
        const tubeGeo = new THREE.TubeGeometry(routeCurve, Math.max(40, waypoints.length * 15), 0.35, 12, false);
        const tubeMat = new THREE.MeshStandardMaterial({{
          color: 0xF59E0B,
          emissive: 0xF59E0B,
          emissiveIntensity: 1.2,
          roughness: 0.1,
          metalness: 0.8
        }});
        const routeTube = new THREE.Mesh(tubeGeo, tubeMat);
        routeGroup.add(routeTube);

        // Origin Start Beacon
        const startPt = curvePoints[0];
        const startBeaconGeo = new THREE.CylinderGeometry(0.2, 0.8, 2.5, 16);
        const startBeaconMat = new THREE.MeshStandardMaterial({{
          color: 0x35D99A,
          emissive: 0x16A36A,
          emissiveIntensity: 1.0
        }});
        const startBeacon = new THREE.Mesh(startBeaconGeo, startBeaconMat);
        startBeacon.position.set(startPt.x, startPt.y + 1.25, startPt.z);
        routeGroup.add(startBeacon);

        // Destination Pin Beacon
        const destPt = curvePoints[curvePoints.length - 1];
        const destBeaconGeo = new THREE.SphereGeometry(0.8, 16, 16);
        const destBeaconMat = new THREE.MeshStandardMaterial({{
          color: 0xEF4444,
          emissive: 0xDC2626,
          emissiveIntensity: 1.2
        }});
        const destBeacon = new THREE.Mesh(destBeaconGeo, destBeaconMat);
        destBeacon.position.set(destPt.x, destPt.y + 1.2, destPt.z);
        routeGroup.add(destBeacon);

        // Animated Traversal Sphere
        const sphereGeo = new THREE.SphereGeometry(0.55, 16, 16);
        const sphereMat = new THREE.MeshBasicMaterial({{ color: 0xFFFFFF }});
        traversalSphere = new THREE.Mesh(sphereGeo, sphereMat);
        traversalSphere.position.copy(startPt);
        routeGroup.add(traversalSphere);

        // Point light on traveling orb
        const orbLight = new THREE.PointLight(0xF59E0B, 2.0, 15);
        traversalSphere.add(orbLight);
      }}

      // 6. Raycasting & Location Interaction
      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();
      let hoveredMesh = null;
      let selectedMesh = null;

      const locationCard = document.getElementById('location-card');
      const cardTitle = document.getElementById('card-title');
      const cardBadge = document.getElementById('card-badge');
      const cardId = document.getElementById('card-id');
      const cardCategory = document.getElementById('card-category');
      const cardAccess = document.getElementById('card-access');
      const cardConnections = document.getElementById('card-connections');
      const cardAmenities = document.getElementById('card-amenities');
      const cardClose = document.getElementById('card-close');
      const hoverTooltip = document.getElementById('hover-tooltip');

      cardClose.addEventListener('click', () => {{
        locationCard.classList.add('hidden');
        if (selectedMesh) {{
          selectedMesh.remove(materials.selectedGlowMesh);
          selectedMesh = null;
        }}
      }});

      function showLocationDetails(mesh) {{
        if (!mesh) return;
        const loc = mesh.userData.locationData;
        cardBadge.innerText = 'Level ' + loc.floor;
        cardBadge.style.color = loc.floor === 0 ? '#35D99A' : '#60A5FA';
        cardTitle.innerText = loc.name;
        cardId.innerText = loc.id;
        cardCategory.innerText = loc.category_label;
        cardAccess.innerText = loc.wheelchair_accessible ? 'Step-Free Accessible' : 'Stair Access Required';
        cardAccess.style.color = loc.wheelchair_accessible ? '#35D99A' : '#F5B942';
        cardConnections.innerText = loc.connected_locations.length + ' connected pathways';

        cardAmenities.innerHTML = '';
        (loc.amenities || []).forEach(am => {{
          const span = document.createElement('span');
          span.className = 'amenity-tag';
          span.innerText = am;
          cardAmenities.appendChild(span);
        }});

        locationCard.classList.remove('hidden');

        // Highlight with pulsing bounding frame
        if (selectedMesh && materials.selectedGlowMesh) {{
          selectedMesh.remove(materials.selectedGlowMesh);
        }}
        selectedMesh = mesh;
        if (!materials.selectedGlowMesh) {{
          const haloGeo = new THREE.BoxGeometry(loc.dimensions.width + 0.4, loc.dimensions.height + 0.4, loc.dimensions.depth + 0.4);
          materials.selectedGlowMesh = new THREE.Mesh(haloGeo, materials.selectedGlow);
        }}
        selectedMesh.add(materials.selectedGlowMesh);
      }}

      // Check initial selection
      if (DATA.config.selected_location_id && roomById[DATA.config.selected_location_id]) {{
        showLocationDetails(roomById[DATA.config.selected_location_id]);
      }}

      window.addEventListener('mousemove', (e) => {{
        const rect = canvas.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(interactiveRoomMeshes, false);

        if (intersects.length > 0) {{
          const hit = intersects[0].object;
          canvas.style.cursor = 'pointer';

          if (hoveredMesh !== hit) {{
            if (hoveredMesh) {{
              hoveredMesh.material.color.copy(hoveredMesh.userData.originalColor);
            }}
            hoveredMesh = hit;
            hoveredMesh.material.color.copy(hoveredMesh.userData.hoverColor);
          }}

          hoverTooltip.style.display = 'block';
          hoverTooltip.style.left = e.clientX + 'px';
          hoverTooltip.style.top = e.clientY + 'px';
          hoverTooltip.innerText = hit.userData.locationData.name;
        }} else {{
          canvas.style.cursor = 'default';
          if (hoveredMesh) {{
            hoveredMesh.material.color.copy(hoveredMesh.userData.originalColor);
            hoveredMesh = null;
          }}
          hoverTooltip.style.display = 'none';
        }}
      }});

      window.addEventListener('click', (e) => {{
        if (e.target !== canvas) return;
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(interactiveRoomMeshes, false);
        if (intersects.length > 0) {{
          showLocationDetails(intersects[0].object);
        }}
      }});

      // 7. HUD Camera View Presets
      function tweenCamera(targetPos, targetLookAt, duration = 600) {{
        const startPos = camera.position.clone();
        const startTarget = controls.target.clone();
        const startTime = performance.now();

        function animateCam(now) {{
          const elapsed = now - startTime;
          const progress = Math.min(elapsed / duration, 1.0);
          const ease = 0.5 - Math.cos(progress * Math.PI) / 2;

          camera.position.lerpVectors(startPos, targetPos, ease);
          controls.target.lerpVectors(startTarget, targetLookAt, ease);
          controls.update();

          if (progress < 1.0) {{
            requestAnimationFrame(animateCam);
          }}
        }}
        requestAnimationFrame(animateCam);
      }}

      function clearActiveViewButtons() {{
        ['btn-iso', 'btn-top', 'btn-front'].forEach(id => document.getElementById(id).classList.remove('active'));
      }}

      document.getElementById('btn-iso').addEventListener('click', (e) => {{
        clearActiveViewButtons();
        e.target.classList.add('active');
        tweenCamera(new THREE.Vector3(34, 30, 36), new THREE.Vector3(0, 3.5, 0));
      }});

      document.getElementById('btn-top').addEventListener('click', (e) => {{
        clearActiveViewButtons();
        e.target.classList.add('active');
        tweenCamera(new THREE.Vector3(0, 65, 0.1), new THREE.Vector3(0, 0, 0));
      }});

      document.getElementById('btn-front').addEventListener('click', (e) => {{
        clearActiveViewButtons();
        e.target.classList.add('active');
        tweenCamera(new THREE.Vector3(0, 10, 55), new THREE.Vector3(0, 4, 0));
      }});

      document.getElementById('btn-reset').addEventListener('click', () => {{
        clearActiveViewButtons();
        document.getElementById('btn-iso').classList.add('active');
        tweenCamera(new THREE.Vector3(34, 30, 36), new THREE.Vector3(0, 3.5, 0));
      }});

      // 8. Floor View Modes (Combined, Exploded, Ground Only, First Only)
      let currentFloorMode = 'combined';

      function setFloorMode(mode) {{
        currentFloorMode = mode;
        ['btn-floor-combined', 'btn-floor-exploded', 'btn-floor-0', 'btn-floor-1'].forEach(id => {{
          document.getElementById(id).classList.remove('active');
        }});

        if (mode === 'combined') {{
          document.getElementById('btn-floor-combined').classList.add('active');
          floor0Group.visible = true;
          floor1Group.visible = true;
          connectorsGroup.visible = true;
          floor1Group.position.y = 0;
        }} else if (mode === 'exploded') {{
          document.getElementById('btn-floor-exploded').classList.add('active');
          floor0Group.visible = true;
          floor1Group.visible = true;
          connectorsGroup.visible = true;
          floor1Group.position.y = 8.0; // Elevate Floor 1 by 8 units higher
        }} else if (mode === 'floor0') {{
          document.getElementById('btn-floor-0').classList.add('active');
          floor0Group.visible = true;
          floor1Group.visible = false;
          connectorsGroup.visible = false;
        }} else if (mode === 'floor1') {{
          document.getElementById('btn-floor-1').classList.add('active');
          floor0Group.visible = false;
          floor1Group.visible = true;
          connectorsGroup.visible = false;
          floor1Group.position.y = 0;
        }}
      }}

      document.getElementById('btn-floor-combined').addEventListener('click', () => setFloorMode('combined'));
      document.getElementById('btn-floor-exploded').addEventListener('click', () => setFloorMode('exploded'));
      document.getElementById('btn-floor-0').addEventListener('click', () => setFloorMode('floor0'));
      document.getElementById('btn-floor-1').addEventListener('click', () => setFloorMode('floor1'));

      // Check initial view mode
      if (DATA.config.initial_view_mode === 'exploded') {{
        setFloorMode('exploded');
      }} else if (DATA.config.initial_view_mode === 'ground_only') {{
        setFloorMode('floor0');
      }} else if (DATA.config.initial_view_mode === 'first_only') {{
        setFloorMode('floor1');
      }}

      // 9. Traversal Animation & Labels Toggle
      document.getElementById('btn-anim-toggle').addEventListener('click', (e) => {{
        isRouteAnimating = !isRouteAnimating;
        e.target.classList.toggle('active', isRouteAnimating);
      }});

      let areLabelsVisible = true;
      document.getElementById('btn-labels-toggle').addEventListener('click', (e) => {{
        areLabelsVisible = !areLabelsVisible;
        labelsGroup.visible = areLabelsVisible;
        e.target.classList.toggle('active', areLabelsVisible);
      }});

      // 10. Animation Loop & Resize
      function onWindowResize() {{
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
      }}
      window.addEventListener('resize', onWindowResize);

      const clock = new THREE.Clock();

      function animate() {{
        requestAnimationFrame(animate);

        const delta = clock.getDelta();
        controls.update();

        // Animate floating gems over room markers
        const time = clock.getElapsedTime();
        interactiveRoomMeshes.forEach(mesh => {{
          if (mesh.userData.gem) {{
            mesh.userData.gem.rotation.y += delta * 1.5;
            mesh.userData.gem.position.y = (mesh.userData.locationData.dimensions.height / 2 + 0.8) + Math.sin(time * 2 + mesh.userData.locationData.pos.x) * 0.1;
          }}
        }});

        // Animate Route Traversal Orb
        if (routeCurve && traversalSphere && isRouteAnimating) {{
          routeAnimTime = (routeAnimTime + delta * 0.18) % 1.0;
          const pt = routeCurve.getPoint(routeAnimTime);
          traversalSphere.position.copy(pt);
        }}

        renderer.render(scene, camera);
      }}

      animate();
    }})();
  </script>
</body>
</html>"""

    return html_template
