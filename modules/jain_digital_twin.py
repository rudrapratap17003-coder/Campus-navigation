"""Three.js 3D Digital Twin Engine for JAIN Global Campus & FET 5-Floor Building.

Phase 13 Architectural Visual Refinement:
1. FET Building Exterior Architecture:
   - Octagonal annular footprint with realistic structural mullions, curtain-wall glazing,
     spandrel panels, entrance portico canopy, and roof parapet walls.
   - Dedicated ADA-compliant West access ramp with handrails and south entrance colonnade.
   - Realistic multi-layered PBR materials: concrete, tinted glass, metal mullions, polished terrazzo.
2. Five-Floor Interior Detailing & Procedural Furnishings:
   - Ground to 4th Floor distinct architectural layouts.
   - Interior boundary wall partitions (1.8m height) defining real room volumes.
   - Procedural lightweight room furnishings:
     * Computer Labs: Workstation arrays with dual monitors and seating.
     * Research Labs: Heavy-duty workbenches, equipment racks, apparatus blocks.
     * Libraries: Bookshelf rows and central reading tables.
     * Smart Classrooms: Tiered student desks, podium, digital smart boards.
     * HPC Supercomputing Cluster: Server rack cabinets with glowing LED activity indicators.
     * Conference Halls & Dean/HOD Suites: Executive conference tables, chairs, display screens.
     * Amphitheater: 6-tier concentric stone seating steps and stage podium.
3. Realistic Outdoor JAIN Global Campus:
   - Kanakapura Road (NH-948) with lane markings and entrance zebra crosswalks.
   - Distinct architectural silhouettes for all major campus facilities:
     * Colosseum Arena (curved stadium bowl with classical colonnade pillars).
     * JIRS Aquatic Center (50m Olympic pool with lane floats, starting blocks, and glass pavilion).
     * Cricket Stadium (green turf oval, central clay pitch, boundary rope, 4-lane athletic track).
     * Dining Complex (2-story cafeteria with outdoor terrace and rooftop canopy).
     * Student Hostels (multi-block residential halls with balcony recesses).
     * Admin Block (corporate headquarters with entrance pediment and steps).
     * Aerospace Labs (barrel-vaulted testing hangar with tarmac apron).
   - Instanced 3D tree canopies, hedges, sidewalk curbs, and illuminated light bollards.
4. Advanced Exploration & Camera Controls:
   - OrbitControls with smooth damping.
   - Camera presets: Isometric, Top-Down, Front, Side (East), FET Close-up, Reset.
   - Modes: Exterior View, Cutaway/Interior View (translucent exterior walls), Floor Isolation, Exploded 5F View with guide rods.
   - Interactive Room Inspector with "🎯 Focus on Room" smooth camera lerp.
   - Traversal Animation Controls: Play, Pause, Speed (1x, 2x, 0.5x), Restart.
   - Accessibility Layer Toggles: Step-Free, Elevators, Stairs, Hazards.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from modules.campus_map import CampusMap
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder, RouteResult

JAIN_DATA_FILE: Path = Path(__file__).resolve().parent.parent / "data" / "jain_global_campus.json"

# Vertical Floor Elevation Configuration (Meters)
FLOOR_HEIGHT_STEP: float = 6.0
EXPLODED_HEIGHT_STEP: float = 14.0

FLOOR_ELEVATIONS: Dict[int, float] = {
    -1: 0.0,       # Outdoor Campus Ground Level
    0: 0.5,        # FET Ground Floor
    1: 6.5,        # FET First Floor
    2: 12.5,       # FET Second Floor
    3: 18.5,       # FET Third Floor
    4: 24.5,       # FET Fourth Floor
}

FLOOR_NAMES: Dict[int, str] = {
    -1: "Outdoor Campus",
    0: "Ground Floor",
    1: "First Floor",
    2: "Second Floor",
    3: "Third Floor",
    4: "Fourth Floor",
}

# Theme Palette & Architectural Colors
PALETTE = {
    "primary_bg": "#07130F",
    "secondary_bg": "#0D1F18",
    "card_bg": "#122820",
    "building_surface": "#1C382C",
    "building_roof": "#264D3D",
    "fet_slab": "#0F261D",
    "concrete": "#2A3B33",
    "mullion": "#1E293B",
    "glass": "#38BDF8",
    "primary_green": "#16A36A",
    "accent_mint": "#35D99A",
    "accessible_route": "#35D99A",
    "route_glow": "#F59E0B",
    "elevator_blue": "#60A5FA",
    "stairs_amber": "#F5B942",
    "blocked_red": "#F87171",
    "unknown_grey": "#9CAFA5",
    "road_color": "#1C2420",
    "grass_color": "#0B1D15",
    "track_red": "#8B3A2B",
    "pool_blue": "#0284C7",
    "text_white": "#F8FAFC",
}


def load_jain_campus_map(file_path: Optional[Path] = None) -> CampusMap:
    """Load the JAIN Global Campus and FET 5-Floor dataset into a CampusMap instance."""
    target_path = file_path if file_path is not None else JAIN_DATA_FILE
    return CampusMap(target_path)


def get_jain_3d_locations_data(campus_map: CampusMap) -> List[Dict[str, Any]]:
    """Assemble structured 3D coordinates, floor attributes, and metadata for all locations."""
    locations_data: List[Dict[str, Any]] = []

    for loc in campus_map.get_all_locations():
        loc_id = loc["id"]
        floor = int(loc.get("floor", 0))
        cat = str(loc.get("category", "office")).lower()
        elev_y = FLOOR_ELEVATIONS.get(floor, 0.5)

        x_val = float(loc.get("x", 0.0))
        z_val = float(loc.get("y", 0.0))

        neighbors: List[Dict[str, Any]] = []
        if loc_id in campus_map.graph:
            for neighbor_id in campus_map.graph.neighbors(loc_id):
                neighbor_loc = campus_map.get_location(neighbor_id) or {}
                neighbors.append({
                    "id": neighbor_id,
                    "name": neighbor_loc.get("name", neighbor_id),
                    "floor": int(neighbor_loc.get("floor", 0)),
                })

        entry = {
            "id": loc_id,
            "name": loc.get("name", loc_id),
            "floor": floor,
            "floor_name": FLOOR_NAMES.get(floor, f"Floor {floor}"),
            "building": loc.get("building", "FET Engineering"),
            "category": cat,
            "is_outdoor": floor == -1,
            "pos": {
                "x": round(x_val, 2),
                "y": round(elev_y, 2),
                "z": round(z_val, 2),
            },
            "wheelchair_accessible": bool(loc.get("wheelchair_accessible", True)),
            "amenities": loc.get("amenities", ["Standard Campus Facility"]),
            "connected_locations": neighbors,
        }
        locations_data.append(entry)

    return locations_data


def get_jain_3d_pathways_data(
    campus_map: CampusMap,
    obstacle_manager: Optional[ObstacleManager] = None,
) -> List[Dict[str, Any]]:
    """Assemble structured 3D spatial geometry and operational state for all pathways."""
    pathways: List[Dict[str, Any]] = []
    seen_edges: Set[Tuple[str, str]] = set()

    blocked_edges: Set[Tuple[str, str]] = set()
    if obstacle_manager:
        try:
            blocked_edges = obstacle_manager.get_active_blocked_edges()
        except Exception:
            blocked_edges = set()

    for u, v, data in campus_map.graph.edges(data=True):
        edge_key = tuple(sorted([u, v]))
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)

        u_loc = campus_map.get_location(u) or {}
        v_loc = campus_map.get_location(v) or {}

        u_floor = int(u_loc.get("floor", 0))
        v_floor = int(v_loc.get("floor", 0))

        u_pos = {
            "x": float(u_loc.get("x", 0.0)),
            "y": FLOOR_ELEVATIONS.get(u_floor, 0.5),
            "z": float(u_loc.get("y", 0.0)),
        }
        v_pos = {
            "x": float(v_loc.get("x", 0.0)),
            "y": FLOOR_ELEVATIONS.get(v_floor, 0.5),
            "z": float(v_loc.get("y", 0.0)),
        }

        is_cross_floor = u_floor != v_floor
        has_elevator = bool(data.get("has_elevator", False))
        has_stairs = bool(data.get("has_stairs", False))
        has_ramp = bool(data.get("has_ramp", False))
        wheelchair_accessible = bool(data.get("wheelchair_accessible", True))

        is_blocked = (u, v) in blocked_edges or (v, u) in blocked_edges or data.get("status") == "blocked"

        if is_blocked:
            color = PALETTE["blocked_red"]
            ptype = "blocked"
        elif has_elevator:
            color = PALETTE["elevator_blue"]
            ptype = "elevator"
        elif has_stairs:
            color = PALETTE["stairs_amber"]
            ptype = "stairs"
        elif has_ramp:
            color = PALETTE["accent_mint"]
            ptype = "ramp"
        elif u_floor == -1 and v_floor == -1:
            color = "#4ADE80"
            ptype = "outdoor_walkway"
        elif wheelchair_accessible:
            color = PALETTE["primary_green"]
            ptype = "accessible_corridor"
        else:
            color = PALETTE["unknown_grey"]
            ptype = "corridor"

        pathway_entry = {
            "id": f"{u}__{v}",
            "source": u,
            "destination": v,
            "source_name": u_loc.get("name", u),
            "destination_name": v_loc.get("name", v),
            "source_floor": u_floor,
            "dest_floor": v_floor,
            "source_pos": u_pos,
            "dest_pos": v_pos,
            "is_cross_floor": is_cross_floor,
            "has_elevator": has_elevator,
            "has_stairs": has_stairs,
            "has_ramp": has_ramp,
            "wheelchair_accessible": wheelchair_accessible,
            "is_blocked": is_blocked,
            "color": color,
            "pathway_type": ptype,
            "distance": float(data.get("distance", 0.0)),
            "estimated_time": float(data.get("estimated_time", 0.0)),
        }
        pathways.append(pathway_entry)

    return pathways


def get_jain_3d_route_data(
    campus_map: CampusMap,
    route_finder: RouteFinder,
    start_id: str,
    dest_id: str,
    algorithm: str = "dijkstra",
    wheelchair_accessible: bool = False,
) -> Dict[str, Any]:
    """Execute authoritative Python route calculation and assemble 3D multi-floor waypoints."""
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
            "algorithm_used": algorithm.upper(),
        }

    path_nodes = route_res.path
    waypoints: List[Dict[str, Any]] = []

    for idx, node_id in enumerate(path_nodes):
        loc = campus_map.get_location(node_id) or {}
        floor = int(loc.get("floor", 0))
        elev_y = FLOOR_ELEVATIONS.get(floor, 0.5)

        x_pos = float(loc.get("x", 0.0))
        z_pos = float(loc.get("y", 0.0))

        waypoints.append({
            "index": idx,
            "id": node_id,
            "name": loc.get("name", node_id),
            "floor": floor,
            "x": round(x_pos, 2),
            "y": round(elev_y + 0.35, 2),
            "z": round(z_pos, 2),
        })

    steps_data: List[Dict[str, Any]] = []
    for step in route_res.steps:
        steps_data.append({
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
        })

    transitions: List[Dict[str, Any]] = []
    for step in route_res.steps:
        if step.from_floor != step.to_floor:
            conn_type = "Elevator" if step.has_elevator else "Stairway" if step.has_stairs else "Vertical Ramp"
            transitions.append({
                "from_floor": step.from_floor,
                "to_floor": step.to_floor,
                "connector_type": conn_type,
                "from_name": step.from_name,
                "to_name": step.to_name,
                "wheelchair_accessible": step.wheelchair_accessible,
                "instruction": step.instruction,
            })

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
        "algorithm_used": algorithm.upper(),
    }


def get_jain_multi_route_comparison(
    campus_map: CampusMap,
    route_finder: RouteFinder,
    start_id: str,
    dest_id: str,
    wheelchair_accessible: bool = False,
) -> Dict[str, Any]:
    """Calculate and compare multiple route alternatives (Dijkstra, BFS, Alternative Detour) between two points."""
    routes: Dict[str, Any] = {}

    # 1. Primary Dijkstra Route (Shortest Distance)
    dijkstra_res = route_finder.find_route(
        source=start_id,
        destination=dest_id,
        algorithm="dijkstra",
        wheelchair_accessible=wheelchair_accessible,
        optimize_for="distance",
    )

    # 2. BFS Route (Fewest Steps/Hops)
    bfs_res = route_finder.find_route(
        source=start_id,
        destination=dest_id,
        algorithm="bfs",
        wheelchair_accessible=wheelchair_accessible,
    )

    # 3. Penalty Alternative Route (Detour)
    alternatives = route_finder.find_alternative_routes(
        source=start_id,
        destination=dest_id,
        max_alternatives=1,
        wheelchair_accessible=wheelchair_accessible,
    )
    alt_res = alternatives[0] if alternatives else None

    def package_summary(r: Optional[RouteResult], label: str, rationale: str) -> Optional[Dict[str, Any]]:
        if not r or not r.success:
            return None
        has_elev = any(s.has_elevator for s in r.steps)
        has_stairs = any(s.has_stairs for s in r.steps)
        trans_count = sum(1 for s in r.steps if s.from_floor != s.to_floor)
        return {
            "label": label,
            "rationale": rationale,
            "total_distance": round(r.total_distance, 1),
            "total_time": round(r.total_time, 1),
            "edge_count": r.edge_count,
            "floor_transitions": trans_count,
            "has_elevator": has_elev,
            "has_stairs": has_stairs,
            "is_accessible": r.is_accessible,
            "path": r.path,
        }

    routes["dijkstra"] = package_summary(
        dijkstra_res,
        "Dijkstra (Shortest Distance)",
        "Optimizes total physical pathway distance; best overall walking path.",
    )
    routes["bfs"] = package_summary(
        bfs_res,
        "BFS (Fewest Pathway Hops)",
        "Minimizes the number of corridor and facility transitions.",
    )
    if alt_res:
        routes["alternative"] = package_summary(
            alt_res,
            "Detour Alternative",
            "Alternative trajectory bypassing key segments of the primary path.",
        )

    return routes


def build_jain_digital_twin_payload(
    campus_map: CampusMap,
    route_finder: Optional[RouteFinder] = None,
    obstacle_manager: Optional[ObstacleManager] = None,
    start_id: Optional[str] = None,
    dest_id: Optional[str] = None,
    algorithm: str = "dijkstra",
    wheelchair_accessible: bool = False,
    selected_location_id: Optional[str] = None,
    view_mode: str = "all_floors",
    navigation_session: Optional[Any] = None,
) -> Dict[str, Any]:
    """Assemble complete consolidated JSON payload for JAIN Global Campus and FET 5-Floor Twin."""
    raw_json_data = {}
    if JAIN_DATA_FILE.exists():
        with open(JAIN_DATA_FILE, "r", encoding="utf-8") as f:
            raw_json_data = json.load(f)

    buildings = raw_json_data.get("buildings", [])
    locations = get_jain_3d_locations_data(campus_map)
    pathways = get_jain_3d_pathways_data(campus_map, obstacle_manager)

    active_route: Optional[Dict[str, Any]] = None
    route_comparison: Optional[Dict[str, Any]] = None
    if route_finder and start_id and dest_id and start_id != dest_id:
        active_route = get_jain_3d_route_data(
            campus_map=campus_map,
            route_finder=route_finder,
            start_id=start_id,
            dest_id=dest_id,
            algorithm=algorithm,
            wheelchair_accessible=wheelchair_accessible,
        )
        route_comparison = get_jain_multi_route_comparison(
            campus_map=campus_map,
            route_finder=route_finder,
            start_id=start_id,
            dest_id=dest_id,
            wheelchair_accessible=wheelchair_accessible,
        )

    active_obstacles: List[Dict[str, Any]] = []
    if obstacle_manager:
        try:
            active_obstacles = obstacle_manager.get_active_obstacles()
        except Exception:
            active_obstacles = []

    nav_session_dict = None
    if navigation_session and hasattr(navigation_session, "to_dict"):
        nav_session_dict = navigation_session.to_dict()

    payload = {
        "metadata": {
            "name": "JAIN Global Campus 3D Digital Twin",
            "institution": "JAIN (Deemed-to-be University) - Faculty of Engineering & Technology",
            "location": "Jakkasandra Post, Kanakapura Road, Ramanagara District, Karnataka, India - 562112",
            "floors_count": 5,
            "palette": PALETTE,
        },
        "config": {
            "initial_view_mode": view_mode,
            "selected_location_id": selected_location_id,
            "has_active_route": bool(active_route and active_route.get("success")),
        },
        "buildings": buildings,
        "locations": locations,
        "pathways": pathways,
        "active_route": active_route,
        "route_comparison": route_comparison,
        "active_obstacles": active_obstacles,
        "navigation_session": nav_session_dict,
    }

    return payload


def render_jain_digital_twin_html(payload: Dict[str, Any], height: int = 760) -> str:
    """Generate self-contained Three.js HTML/CSS/JS application embedding the JAIN Global Campus Digital Twin."""
    serialized_data = json.dumps(payload, ensure_ascii=False)

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JAIN Global Campus 3D Digital Twin</title>
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
      background: radial-gradient(circle at 50% 30%, #0e2a20 0%, #07130F 100%);
    }}
    canvas#webgl-canvas {{
      display: block;
      width: 100%;
      height: 100%;
      outline: none;
    }}
    /* Top HUD Controls */
    .hud-bar-top {{
      position: absolute;
      top: 12px;
      left: 12px;
      right: 12px;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      pointer-events: none;
      z-index: 10;
    }}
    .hud-group {{
      display: flex;
      align-items: center;
      gap: 5px;
      background: rgba(13, 31, 24, 0.92);
      border: 1px solid rgba(53, 217, 154, 0.3);
      border-radius: 10px;
      padding: 5px 8px;
      backdrop-filter: blur(10px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
      pointer-events: auto;
    }}
    .hud-title {{
      font-size: 11px;
      font-weight: 700;
      color: #35D99A;
      margin-right: 3px;
      display: flex;
      align-items: center;
      gap: 4px;
    }}
    .hud-btn {{
      background: rgba(22, 163, 106, 0.15);
      border: 1px solid rgba(53, 217, 154, 0.3);
      color: #F8FAFC;
      border-radius: 6px;
      padding: 4px 8px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      white-space: nowrap;
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
    /* Location Inspector Drawer */
    #location-card {{
      position: absolute;
      bottom: 16px;
      left: 16px;
      width: 320px;
      max-width: calc(100% - 32px);
      background: rgba(13, 31, 24, 0.95);
      border: 1px solid rgba(53, 217, 154, 0.4);
      border-radius: 12px;
      padding: 12px 14px;
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
      margin-bottom: 6px;
      border-bottom: 1px solid rgba(53, 217, 154, 0.2);
      padding-bottom: 5px;
    }}
    .card-title {{
      font-size: 13px;
      font-weight: 700;
      color: #F8FAFC;
      line-height: 1.3;
    }}
    .card-badge {{
      display: inline-block;
      font-size: 10px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      text-transform: uppercase;
      background: rgba(53, 217, 154, 0.2);
      color: #35D99A;
    }}
    .card-close {{
      background: none;
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
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      margin-bottom: 4px;
      color: #9CAFA5;
    }}
    .card-row .val {{
      font-weight: 600;
      color: #F8FAFC;
      text-align: right;
    }}
    .amenities-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin-top: 6px;
    }}
    .amenity-tag {{
      background: rgba(53, 217, 154, 0.15);
      border: 1px solid rgba(53, 217, 154, 0.3);
      color: #A7F3D0;
      font-size: 9px;
      padding: 2px 6px;
      border-radius: 4px;
    }}
    .card-action-btn {{
      width: 100%;
      margin-top: 8px;
      background: #16A36A;
      color: #FFFFFF;
      border: 1px solid #35D99A;
      border-radius: 6px;
      padding: 6px 0;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      transition: background 0.2s ease;
    }}
    .card-action-btn:hover {{
      background: #35D99A;
      color: #07130F;
    }}
    /* Legend */
    .hud-legend {{
      position: absolute;
      bottom: 16px;
      right: 16px;
      background: rgba(13, 31, 24, 0.9);
      border: 1px solid rgba(53, 217, 154, 0.25);
      border-radius: 10px;
      padding: 8px 12px;
      backdrop-filter: blur(10px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
      z-index: 10;
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 10px;
      color: #9CAFA5;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
    }}
    .legend-item:hover span {{
      color: #F8FAFC;
    }}
    .legend-dot {{
      width: 9px;
      height: 9px;
      border-radius: 2px;
      flex-shrink: 0;
    }}
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
    /* Phase 15: Real-Time Interactive Navigation HUD Panel */
    .nav-live-hud {{
      position: absolute;
      bottom: 24px;
      left: 20px;
      width: 340px;
      max-width: calc(100% - 40px);
      background: rgba(7, 19, 15, 0.94);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border: 1px solid #16A36A;
      box-shadow: 0 10px 32px rgba(0, 0, 0, 0.65), 0 0 16px rgba(53, 217, 154, 0.25);
      border-radius: 12px;
      padding: 14px 16px;
      z-index: 25;
      font-family: inherit;
      color: #F8FAFC;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .nav-live-hud.hidden {{
      display: none;
    }}
    .nav-hud-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}
    .nav-hud-badge {{
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 0.8px;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 6px;
      background: rgba(53, 217, 154, 0.2);
      color: #35D99A;
      border: 1px solid rgba(53, 217, 154, 0.4);
    }}
    .nav-hud-badge.arrived {{
      background: rgba(16, 185, 129, 0.3);
      color: #10B981;
      border-color: #10B981;
    }}
    .nav-hud-badge.rerouting {{
      background: rgba(248, 113, 113, 0.25);
      color: #F87171;
      border-color: #F87171;
    }}
    .nav-hud-metric {{
      font-size: 11px;
      color: #A7F3D0;
      font-weight: 600;
    }}
    .nav-hud-instruction {{
      display: flex;
      align-items: flex-start;
      gap: 10px;
      margin-bottom: 10px;
      line-height: 1.4;
    }}
    .nav-hud-icon {{
      font-size: 20px;
      line-height: 1;
    }}
    .nav-hud-text {{
      font-size: 12.5px;
      font-weight: 600;
      color: #F8FAFC;
    }}
    .nav-hud-progress-bg {{
      width: 100%;
      height: 5px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 3px;
      overflow: hidden;
      margin-bottom: 10px;
    }}
    .nav-hud-progress-fill {{
      height: 100%;
      background: linear-gradient(90deg, #16A36A, #35D99A);
      transition: width 0.3s ease;
    }}
    .nav-hud-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      color: #9CAFA5;
    }}
    .nav-hud-controls {{
      display: flex;
      gap: 6px;
    }}
    .nav-ctrl-btn {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #F8FAFC;
      border-radius: 6px;
      padding: 4px 8px;
      font-size: 12px;
      cursor: pointer;
      transition: background 0.2s;
    }}
    .nav-ctrl-btn:hover {{
      background: rgba(53, 217, 154, 0.3);
      border-color: #35D99A;
    }}
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
        <button class="hud-btn active" id="btn-cam-iso">Isometric</button>
        <button class="hud-btn" id="btn-cam-top">Top</button>
        <button class="hud-btn" id="btn-cam-front">Front</button>
        <button class="hud-btn" id="btn-cam-side">Side</button>
        <button class="hud-btn" id="btn-cam-fet">FET Close</button>
        <button class="hud-btn" id="btn-cam-reset">🔄</button>
      </div>

      <!-- Domain View Mode -->
      <div class="hud-group">
        <span class="hud-title">🌐 Domain:</span>
        <button class="hud-btn active" id="btn-mode-all">All Campus</button>
        <button class="hud-btn" id="btn-mode-outdoor">Outdoor</button>
        <button class="hud-btn" id="btn-mode-fet">FET Only</button>
      </div>

      <!-- View Style (Exterior vs Cutaway Interior) -->
      <div class="hud-group">
        <span class="hud-title">👁️ View:</span>
        <button class="hud-btn active" id="btn-view-exterior">Exterior</button>
        <button class="hud-btn" id="btn-view-cutaway">Cutaway</button>
      </div>

      <!-- FET 5-Floor Isolation & Exploded Controls -->
      <div class="hud-group" id="group-floors">
        <span class="hud-title">🏢 Floors:</span>
        <button class="hud-btn active" id="btn-fl-all">Stacked</button>
        <button class="hud-btn" id="btn-fl-exploded">💥 Exploded</button>
        <button class="hud-btn" id="btn-fl-0">G</button>
        <button class="hud-btn" id="btn-fl-1">1F</button>
        <button class="hud-btn" id="btn-fl-2">2F</button>
        <button class="hud-btn" id="btn-fl-3">3F</button>
        <button class="hud-btn" id="btn-fl-4">4F</button>
      </div>

      <!-- Route Animation & Accessibility Controls -->
      <div class="hud-group">
        <button class="hud-btn active" id="btn-anim-toggle" title="Play or Pause Traversal">⏯️ Route</button>
        <button class="hud-btn" id="btn-anim-speed" title="Adjust Traversal Speed">⚡ 1x</button>
        <button class="hud-btn active" id="btn-labels-toggle" title="Toggle Room Labels">🏷️</button>
      </div>
    </div>

    <!-- Location Inspector Drawer -->
    <div id="location-card" class="hidden">
      <div class="card-header">
        <div>
          <span class="card-badge" id="card-badge">Level 0</span>
          <div class="card-title" id="card-title">Facility Name</div>
        </div>
        <button class="card-close" id="card-close" title="Close Panel">✕</button>
      </div>
      <div class="card-row">
        <span>Location ID:</span>
        <span class="val" id="card-id">LOC_ID</span>
      </div>
      <div class="card-row">
        <span>Building:</span>
        <span class="val" id="card-building">FET Engineering</span>
      </div>
      <div class="card-row">
        <span>Category:</span>
        <span class="val" id="card-category">Research Lab</span>
      </div>
      <div class="card-row">
        <span>Wheelchair Access:</span>
        <span class="val" id="card-access" style="color: #35D99A;">Step-Free Accessible</span>
      </div>
      <div class="card-row">
        <span>Connected Paths:</span>
        <span class="val" id="card-connections">3 routes</span>
      </div>
      <div style="margin-top: 6px; font-size: 10px; color: #9CAFA5; font-weight: 600;">Verified Amenities:</div>
      <div class="amenities-list" id="card-amenities"></div>
      <button class="card-action-btn" id="btn-focus-room">🎯 Focus on Room</button>
    </div>

    <!-- 3D Legend & Layer Toggles -->
    <div class="hud-legend">
      <div style="font-weight: 700; color: #35D99A; margin-bottom: 2px;">Campus Layers:</div>
      <div class="legend-item" id="toggle-layer-stepfree"><div class="legend-dot" style="background: #16A36A;"></div><span>Step-Free Pathway</span></div>
      <div class="legend-item" id="toggle-layer-ramp"><div class="legend-dot" style="background: #35D99A;"></div><span>ADA Access Ramp</span></div>
      <div class="legend-item" id="toggle-layer-elevator"><div class="legend-dot" style="background: #60A5FA;"></div><span>Elevator Core (0F-4F)</span></div>
      <div class="legend-item" id="toggle-layer-stairs"><div class="legend-dot" style="background: #F5B942;"></div><span>Cardinal Stairwells</span></div>
      <div class="legend-item" id="toggle-layer-blocked"><div class="legend-dot" style="background: #F87171;"></div><span>Verified Barrier</span></div>
      <div class="legend-item" id="legend-route" style="display: none;"><div class="legend-dot" style="background: #F59E0B;"></div><span>Active Trajectory</span></div>
    </div>

    <!-- Real-Time Interactive Navigation HUD Panel -->
    <div id="nav-live-card" class="nav-live-hud hidden">
      <div class="nav-hud-header">
        <span class="nav-hud-badge" id="nav-hud-state">NAVIGATING</span>
        <span class="nav-hud-metric" id="nav-hud-dist">Remaining: 0 m</span>
      </div>
      <div class="nav-hud-instruction" id="nav-hud-instruction">
        <span class="nav-hud-icon" id="nav-hud-icon">🧭</span>
        <span class="nav-hud-text" id="nav-hud-text">Starting navigation...</span>
      </div>
      <div class="nav-hud-progress-bg">
        <div class="nav-hud-progress-fill" id="nav-hud-progress" style="width: 0%;"></div>
      </div>
      <div class="nav-hud-footer">
        <span id="nav-hud-step-count">Step 1 of 5</span>
        <div class="nav-hud-controls">
          <button class="nav-ctrl-btn" id="nav-btn-prev" title="Previous Step">⏮️</button>
          <button class="nav-ctrl-btn" id="nav-btn-playpause" title="Pause / Resume">⏸️</button>
          <button class="nav-ctrl-btn" id="nav-btn-next" title="Next Step">⏭️</button>
          <button class="nav-ctrl-btn" id="nav-btn-restart" title="Restart Navigation">🔄</button>
        </div>
      </div>
    </div>

    <div id="hover-tooltip"></div>

    <div id="webgl-fallback">
      <h3>⚠️ WebGL Hardware Acceleration Required</h3>
      <p>Your browser environment could not initialize 3D WebGL. Please ensure hardware acceleration is enabled or use the 2D Schematic Campus Map.</p>
    </div>
  </div>

  <!-- Three.js r128 & OrbitControls -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

  <script>
    (function() {{
      const DATA = {serialized_data};

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
      scene.fog = new THREE.FogExp2(0x07130F, 0.0032);

      const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.5, 2000);
      camera.position.set(110, 120, 140);

      const renderer = new THREE.WebGLRenderer({{
        canvas: canvas,
        antialias: true,
        alpha: false,
        powerPreference: 'high-performance'
      }});
      renderer.setSize(container.clientWidth, container.clientHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.18;
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;

      const controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.maxPolarAngle = Math.PI / 2 - 0.02;
      controls.minDistance = 10;
      controls.maxDistance = 550;
      controls.target.set(10, 8, 10);

      // Lighting Rig
      const ambientLight = new THREE.AmbientLight(0x133829, 0.95);
      scene.add(ambientLight);

      const sunLight = new THREE.DirectionalLight(0xFFFFFF, 1.25);
      sunLight.position.set(150, 240, 130);
      sunLight.castShadow = true;
      sunLight.shadow.mapSize.width = 2048;
      sunLight.shadow.mapSize.height = 2048;
      sunLight.shadow.camera.near = 10;
      sunLight.shadow.camera.far = 600;
      sunLight.shadow.camera.left = -190;
      sunLight.shadow.camera.right = 190;
      sunLight.shadow.camera.top = 190;
      sunLight.shadow.camera.bottom = -190;
      scene.add(sunLight);

      const blueFill = new THREE.DirectionalLight(0x60A5FA, 0.45);
      blueFill.position.set(-150, 100, -150);
      scene.add(blueFill);

      // Groups for Layer & View Control
      const outdoorGroup = new THREE.Group();
      const fetBuildingGroup = new THREE.Group();
      const fetFloorGroups = [new THREE.Group(), new THREE.Group(), new THREE.Group(), new THREE.Group(), new THREE.Group()];
      const exteriorCurtainWalls = []; // for cutaway mode
      const verticalConnectorsGroup = new THREE.Group();
      const labelsGroup = new THREE.Group();
      const routeGroup = new THREE.Group();
      const furnitureGroup = new THREE.Group();
      const guideRodsGroup = new THREE.Group();

      scene.add(outdoorGroup);
      scene.add(fetBuildingGroup);
      fetFloorGroups.forEach(fg => fetBuildingGroup.add(fg));
      fetBuildingGroup.add(verticalConnectorsGroup);
      fetBuildingGroup.add(furnitureGroup);
      fetBuildingGroup.add(guideRodsGroup);
      scene.add(labelsGroup);
      scene.add(routeGroup);

      // 2. Material Palette (PBR Quality)
      const concreteMat = new THREE.MeshStandardMaterial({{ color: 0x22362C, roughness: 0.8, metalness: 0.1 }});
      const slabMat = new THREE.MeshStandardMaterial({{ color: 0x0E261D, roughness: 0.45, metalness: 0.25 }});
      const glassCurtainMat = new THREE.MeshStandardMaterial({{ color: 0x38BDF8, roughness: 0.1, metalness: 0.85, transparent: true, opacity: 0.55 }});
      const mullionMat = new THREE.MeshStandardMaterial({{ color: 0x1E293B, roughness: 0.3, metalness: 0.9 }});
      const parapetMat = new THREE.MeshStandardMaterial({{ color: 0x162A20, roughness: 0.7 }});
      const waterMat = new THREE.MeshStandardMaterial({{ color: 0x0284C7, roughness: 0.1, metalness: 0.8, transparent: true, opacity: 0.85 }});
      const turfMat = new THREE.MeshStandardMaterial({{ color: 0x143D28, roughness: 0.95 }});
      const pitchMat = new THREE.MeshStandardMaterial({{ color: 0xA38054, roughness: 0.9 }});
      const trackMat = new THREE.MeshStandardMaterial({{ color: 0x8A2F24, roughness: 0.8 }});
      const woodMat = new THREE.MeshStandardMaterial({{ color: 0x78350F, roughness: 0.6 }});
      const metalTechMat = new THREE.MeshStandardMaterial({{ color: 0x0F172A, roughness: 0.35, metalness: 0.8 }});
      const deskMat = new THREE.MeshStandardMaterial({{ color: 0x475569, roughness: 0.5 }});
      const monitorMat = new THREE.MeshStandardMaterial({{ color: 0x0284C7, emissive: 0x0284C7, emissiveIntensity: 0.6 }});

      // 3. Outdoor Campus Landscape
      // Terrain plane
      const terrainGeo = new THREE.PlaneGeometry(500, 500);
      const terrainMat = new THREE.MeshStandardMaterial({{ color: 0x091A12, roughness: 0.95 }});
      const terrainMesh = new THREE.Mesh(terrainGeo, terrainMat);
      terrainMesh.rotation.x = -Math.PI / 2;
      terrainMesh.position.y = -0.15;
      terrainMesh.receiveShadow = true;
      outdoorGroup.add(terrainMesh);

      // Kanakapura Road (NH-948)
      const roadGeo = new THREE.PlaneGeometry(450, 22);
      const roadMat = new THREE.MeshStandardMaterial({{ color: 0x19211D, roughness: 0.85 }});
      const roadMesh = new THREE.Mesh(roadGeo, roadMat);
      roadMesh.rotation.x = -Math.PI / 2;
      roadMesh.position.set(0, 0.01, 155);
      roadMesh.receiveShadow = true;
      outdoorGroup.add(roadMesh);

      // Road Centerlines (Dashed White Lines)
      for (let rx = -200; rx <= 200; rx += 12) {{
        const dashGeo = new THREE.PlaneGeometry(6, 0.5);
        const dashMat = new THREE.MeshBasicMaterial({{ color: 0xF8FAFC }});
        const dash = new THREE.Mesh(dashGeo, dashMat);
        dash.rotation.x = -Math.PI / 2;
        dash.position.set(rx, 0.03, 155);
        outdoorGroup.add(dash);
      }}

      // Main Gate Entrance Arch & Zebra Crosswalk
      for (let zx = -6; zx <= 6; zx += 1.6) {{
        const zebraGeo = new THREE.PlaneGeometry(0.9, 12);
        const zebraMat = new THREE.MeshBasicMaterial({{ color: 0xF8FAFC }});
        const zebra = new THREE.Mesh(zebraGeo, zebraMat);
        zebra.rotation.x = -Math.PI / 2;
        zebra.position.set(zx, 0.03, 144);
        outdoorGroup.add(zebra);
      }}

      const gateArchMat = new THREE.MeshStandardMaterial({{ color: 0x1E3B2F, metalness: 0.6, roughness: 0.3 }});
      const p1 = new THREE.Mesh(new THREE.BoxGeometry(1.4, 7, 1.4), gateArchMat);
      p1.position.set(-8, 3.5, 140);
      const p2 = new THREE.Mesh(new THREE.BoxGeometry(1.4, 7, 1.4), gateArchMat);
      p2.position.set(8, 3.5, 140);
      const beam = new THREE.Mesh(new THREE.BoxGeometry(18, 1.2, 1.6), gateArchMat);
      beam.position.set(0, 7.5, 140);
      outdoorGroup.add(p1, p2, beam);

      // Paved Main Avenue Walkways with Curbs
      const aveGeo = new THREE.PlaneGeometry(16, 95);
      const aveMat = new THREE.MeshStandardMaterial({{ color: 0x1F2E27, roughness: 0.8 }});
      const aveMesh = new THREE.Mesh(aveGeo, aveMat);
      aveMesh.rotation.x = -Math.PI / 2;
      aveMesh.position.set(0, 0.02, 92);
      aveMesh.receiveShadow = true;
      outdoorGroup.add(aveMesh);

      // 4. Distinct Outdoor Campus Buildings
      const buildingMeshes = [];
      const interactiveLocations = [];
      const locationMeshMap = {{}};

      (DATA.buildings || []).forEach(bld => {{
        if (bld.id === 'BLD_FET') return;

        const bGroup = new THREE.Group();
        bGroup.position.set(bld.center_x, 0, bld.center_z);

        if (bld.id === 'BLD_COLOSSEUM') {{
          // Circular Colosseum Sports Arena
          const baseCyl = new THREE.Mesh(new THREE.CylinderGeometry(22, 22, 9, 32), concreteMat);
          baseCyl.position.y = 4.5;
          baseCyl.castShadow = true;
          bGroup.add(baseCyl);

          // Colonnade Pillars
          for (let i = 0; i < 16; i++) {{
            const angle = (i / 16) * Math.PI * 2;
            const pil = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 10, 12), mullionMat);
            pil.position.set(Math.cos(angle) * 22.8, 5, Math.sin(angle) * 22.8);
            bGroup.add(pil);
          }}
          // Domed Roof Ring
          const dome = new THREE.Mesh(new THREE.SphereGeometry(18, 24, 12, 0, Math.PI * 2, 0, Math.PI * 0.35), parapetMat);
          dome.position.y = 8.5;
          bGroup.add(dome);

        }} else if (bld.id === 'BLD_AQUATICS_POOL') {{
          // JIRS Aquatic Center: Glass Sports Pavilion + Olympic Pool
          const poolDeck = new THREE.Mesh(new THREE.BoxGeometry(40, 1.0, 24), concreteMat);
          poolDeck.position.y = 0.5;
          bGroup.add(poolDeck);

          const water = new THREE.Mesh(new THREE.PlaneGeometry(36, 18), waterMat);
          water.rotation.x = -Math.PI / 2;
          water.position.y = 1.02;
          bGroup.add(water);

          // Lane Lines on Water
          for (let lane = -7; lane <= 7; lane += 2) {{
            const lmesh = new THREE.Mesh(new THREE.PlaneGeometry(34, 0.15), new THREE.MeshBasicMaterial({{ color: 0xFFFFFF }}));
            lmesh.rotation.x = -Math.PI / 2;
            lmesh.position.set(0, 1.03, lane);
            bGroup.add(lmesh);
          }}

          // Starting Blocks
          for (let sb = -7; sb <= 7; sb += 2) {{
            const block = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.6, 0.8), mullionMat);
            block.position.set(-17.5, 1.3, sb);
            bGroup.add(block);
          }}

          // Enclosed Pavilion
          const pavilion = new THREE.Mesh(new THREE.BoxGeometry(16, 7, 24), glassCurtainMat);
          pavilion.position.set(24, 3.5, 0);
          bGroup.add(pavilion);

        }} else if (bld.id === 'BLD_CRICKET_STADIUM') {{
          // International Cricket Stadium: Oval Turf + Pitch + 4-lane Running Track
          const track = new THREE.Mesh(new THREE.CylinderGeometry(52, 52, 0.2, 36), trackMat);
          track.position.y = 0.1;
          bGroup.add(track);

          const turf = new THREE.Mesh(new THREE.CylinderGeometry(47, 47, 0.3, 36), turfMat);
          turf.position.y = 0.2;
          bGroup.add(turf);

          // Central Pitch
          const pitch = new THREE.Mesh(new THREE.PlaneGeometry(22, 3.2), pitchMat);
          pitch.rotation.x = -Math.PI / 2;
          pitch.position.y = 0.36;
          bGroup.add(pitch);

          // White Boundary Rope
          const ropeGeo = new THREE.TorusGeometry(45, 0.25, 8, 48);
          const rope = new THREE.Mesh(ropeGeo, new THREE.MeshBasicMaterial({{ color: 0xF8FAFC }}));
          rope.rotation.x = Math.PI / 2;
          rope.position.y = 0.4;
          bGroup.add(rope);

        }} else if (bld.id === 'BLD_DINING_COMPLEX') {{
          // 2-Story Dining Hall & Student Cafeteria
          const dBase = new THREE.Mesh(new THREE.BoxGeometry(34, 8, 22), concreteMat);
          dBase.position.y = 4;
          bGroup.add(dBase);

          const dGlass = new THREE.Mesh(new THREE.BoxGeometry(32, 6, 20), glassCurtainMat);
          dGlass.position.y = 4.2;
          bGroup.add(dGlass);

          // Rooftop Terrace & Canopy
          const terrace = new THREE.Mesh(new THREE.BoxGeometry(36, 0.8, 24), parapetMat);
          terrace.position.y = 8.4;
          bGroup.add(terrace);

        }} else if (bld.id === 'BLD_HOSTEL_BLOCKS') {{
          // Student Residential Dormitory Blocks
          [-14, 0, 14].forEach((offsetZ, idx) => {{
            const hBlock = new THREE.Mesh(new THREE.BoxGeometry(26, 12, 10), concreteMat);
            hBlock.position.set(0, 6, offsetZ);
            hBlock.castShadow = true;
            bGroup.add(hBlock);

            // Balcony Horizontal Recesses
            for (let fl = 1; fl <= 3; fl++) {{
              const balc = new THREE.Mesh(new THREE.BoxGeometry(25, 0.3, 1.2), mullionMat);
              balc.position.set(0, fl * 3.5, offsetZ + 5.2);
              bGroup.add(balc);
            }}
          }});

        }} else if (bld.id === 'BLD_ADMIN_BLOCK') {{
          // University Corporate Administration Headquarters
          const aBody = new THREE.Mesh(new THREE.BoxGeometry(32, 10, 20), concreteMat);
          aBody.position.y = 5;
          bGroup.add(aBody);

          // Classical Entrance Portico & Pillars
          const porticoRoof = new THREE.Mesh(new THREE.BoxGeometry(14, 1.2, 8), parapetMat);
          porticoRoof.position.set(0, 10.6, 12);
          bGroup.add(porticoRoof);

          [-5, -1.8, 1.8, 5].forEach(px => {{
            const col = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 10, 16), concreteMat);
            col.position.set(px, 5, 14.5);
            bGroup.add(col);
          }});

        }} else if (bld.id === 'BLD_AEROSPACE_LABS') {{
          // Aerospace Research Hangar (Barrel Vault)
          const hangarCyl = new THREE.Mesh(new THREE.CylinderGeometry(16, 16, 36, 24, 1, false, 0, Math.PI), concreteMat);
          hangarCyl.rotation.z = Math.PI / 2;
          hangarCyl.position.set(0, 0, 0);
          bGroup.add(hangarCyl);

          // Tarmac Apron
          const apron = new THREE.Mesh(new THREE.PlaneGeometry(36, 24), roadMat);
          apron.rotation.x = -Math.PI / 2;
          apron.position.set(0, 0.05, 20);
          bGroup.add(apron);

        }} else {{
          // Standard Academic Structure
          const generic = new THREE.Mesh(new THREE.BoxGeometry(bld.width, bld.height, bld.depth), concreteMat);
          generic.position.y = bld.height / 2;
          bGroup.add(generic);
        }}

        bGroup.userData = {{ buildingData: bld }};
        outdoorGroup.add(bGroup);
        buildingMeshes.push(bGroup);
      }});

      // Instanced Trees & Landscaping Vegetation
      const treeCount = 65;
      const trunkGeo = new THREE.CylinderGeometry(0.3, 0.45, 3.5, 8);
      const foliageGeo = new THREE.SphereGeometry(2.4, 10, 8);
      const trunkMat = new THREE.MeshStandardMaterial({{ color: 0x3E2723, roughness: 0.9 }});
      const foliageMat = new THREE.MeshStandardMaterial({{ color: 0x1E4620, roughness: 0.85 }});

      const trunkInst = new THREE.InstancedMesh(trunkGeo, trunkMat, treeCount);
      const folInst = new THREE.InstancedMesh(foliageGeo, foliageMat, treeCount);
      trunkInst.castShadow = true;
      folInst.castShadow = true;

      const dummy = new THREE.Object3D();
      let treeIdx = 0;

      // Tree locations around perimeter roads and quadrangle
      const treeCoords = [];
      for (let tx = -170; tx <= 170; tx += 28) {{
        treeCoords.push({{ x: tx, z: 135 }});
        treeCoords.push({{ x: tx, z: 175 }});
      }}
      for (let tz = 30; tz <= 120; tz += 22) {{
        treeCoords.push({{ x: -16, z: tz }});
        treeCoords.push({{ x: 16, z: tz }});
        treeCoords.push({{ x: -85, z: tz }});
        treeCoords.push({{ x: 85, z: tz }});
      }}

      treeCoords.slice(0, treeCount).forEach((c, i) => {{
        const scale = 0.85 + Math.random() * 0.4;
        dummy.position.set(c.x + (Math.random() - 0.5) * 4, 1.75 * scale, c.z + (Math.random() - 0.5) * 4);
        dummy.scale.set(scale, scale, scale);
        dummy.updateMatrix();
        trunkInst.setMatrixAt(i, dummy.matrix);

        dummy.position.y = 4.2 * scale;
        dummy.updateMatrix();
        folInst.setMatrixAt(i, dummy.matrix);
      }});
      outdoorGroup.add(trunkInst, folInst);

      // 5. Reconstruct FET 5-Floor Detailed Building
      function createOctagonalFloorSlab(radius, thickness) {{
        const shape = new THREE.Shape();
        const sides = 8;
        for (let i = 0; i < sides; i++) {{
          const angle = (i * 2 * Math.PI) / sides;
          const x = radius * Math.cos(angle);
          const y = radius * Math.sin(angle);
          if (i === 0) shape.moveTo(x, y);
          else shape.lineTo(x, y);
        }}
        shape.closePath();

        // Inner Amphitheater Courtyard Hole
        const hole = new THREE.Path();
        const innerRadius = radius * 0.45;
        for (let i = 0; i < sides; i++) {{
          const angle = (i * 2 * Math.PI) / sides;
          const x = innerRadius * Math.cos(angle);
          const y = innerRadius * Math.sin(angle);
          if (i === 0) hole.moveTo(x, y);
          else hole.lineTo(x, y);
        }}
        hole.closePath();
        shape.holes.push(hole);

        const extrudeSettings = {{ depth: thickness, bevelEnabled: true, bevelThickness: 0.25, bevelSize: 0.25, bevelSegments: 3 }};
        return new THREE.ExtrudeGeometry(shape, extrudeSettings);
      }}

      const slabThickness = 0.5;
      const floorElevations = [0.2, 6.2, 12.2, 18.2, 24.2];

      for (let fl = 0; fl < 5; fl++) {{
        const slabGeo = createOctagonalFloorSlab(40, slabThickness);
        const slabMesh = new THREE.Mesh(slabGeo, slabMat);
        slabMesh.rotation.x = -Math.PI / 2;
        slabMesh.position.set(0, floorElevations[fl], 0);
        slabMesh.receiveShadow = true;
        fetFloorGroups[fl].add(slabMesh);

        // Exterior Curtain Walls & Mullions (8 perimeter segments)
        const wallH = 5.2;
        const outerR = 39.8;
        for (let s = 0; s < 8; s++) {{
          const a1 = (s * 2 * Math.PI) / 8;
          const a2 = ((s + 1) * 2 * Math.PI) / 8;
          const x1 = outerR * Math.cos(a1), z1 = outerR * Math.sin(a1);
          const x2 = outerR * Math.cos(a2), z2 = outerR * Math.sin(a2);

          const midX = (x1 + x2) / 2;
          const midZ = (z1 + z2) / 2;
          const len = Math.hypot(x2 - x1, z2 - z1);
          const ang = Math.atan2(x2 - x1, z2 - z1);

          // Glass Curtain Wall
          const cWall = new THREE.Mesh(new THREE.BoxGeometry(0.3, wallH, len), glassCurtainMat);
          cWall.position.set(midX, floorElevations[fl] + wallH / 2, midZ);
          cWall.rotation.y = ang;
          cWall.userData = {{ isCurtainWall: true }};
          fetFloorGroups[fl].add(cWall);
          exteriorCurtainWalls.push(cWall);

          // Structural Corner Mullion Column
          const col = new THREE.Mesh(new THREE.BoxGeometry(0.8, wallH, 0.8), mullionMat);
          col.position.set(x1, floorElevations[fl] + wallH / 2, z1);
          fetFloorGroups[fl].add(col);
        }}

        // Ground Floor Entrance Portico & West Ramp
        if (fl === 0) {{
          // Grand Entrance Portico Canopy
          const portico = new THREE.Mesh(new THREE.BoxGeometry(16, 1.0, 10), concreteMat);
          portico.position.set(0, 5.5, 38);
          fetFloorGroups[0].add(portico);

          [-7, 7].forEach(cx => {{
            const col = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 5.5, 16), concreteMat);
            col.position.set(cx, 2.75, 42);
            fetFloorGroups[0].add(col);
          }});

          // Dedicated West Accessible Entrance Ramp
          const rampGeo = new THREE.BoxGeometry(4.0, 0.4, 26);
          const rampMat = new THREE.MeshStandardMaterial({{ color: 0x35D99A, roughness: 0.5 }});
          const rampMesh = new THREE.Mesh(rampGeo, rampMat);
          rampMesh.position.set(-28, 0.25, 24);
          rampMesh.rotation.x = 0.05; // Gentle 1:12 ADA slope
          fetFloorGroups[0].add(rampMesh);

          // Central Courtyard Concentric Amphitheater Steps
          for (let step = 1; step <= 6; step++) {{
            const stepGeo = new THREE.CylinderGeometry(step * 2.8, step * 2.8, 0.4, 32, 1, false, 0, Math.PI);
            const stepMat = new THREE.MeshStandardMaterial({{ color: 0x1B4332, roughness: 0.7 }});
            const stepMesh = new THREE.Mesh(stepGeo, stepMat);
            stepMesh.position.set(0, 0.2 + (6 - step) * 0.32, 0);
            stepMesh.rotation.y = Math.PI / 2;
            fetFloorGroups[0].add(stepMesh);
          }}
          // Amphitheater Stage
          const stage = new THREE.Mesh(new THREE.BoxGeometry(10, 0.6, 7), concreteMat);
          stage.position.set(0, 0.4, -4);
          fetFloorGroups[0].add(stage);
        }}

        // Top Roof Parapet Trim on 4th Floor
        if (fl === 4) {{
          const roofTrim = new THREE.Mesh(createOctagonalFloorSlab(40.4, 1.2), parapetMat);
          roofTrim.rotation.x = -Math.PI / 2;
          roofTrim.position.set(0, floorElevations[4] + wallH, 0);
          fetFloorGroups[4].add(roofTrim);
        }}
      }}

      // 6. Vertical Circulation (Elevator Glass Core & 4 Cardinal Stairwells)
      const elevatorHeight = 25.5;
      const elevShaft = new THREE.Mesh(new THREE.BoxGeometry(4.8, elevatorHeight, 4.8), new THREE.MeshStandardMaterial({{
        color: 0x60A5FA, transparent: true, opacity: 0.38, roughness: 0.1, metalness: 0.85
      }}));
      elevShaft.position.set(-6.0, elevatorHeight / 2, 18.0);
      verticalConnectorsGroup.add(elevShaft);

      // Steel Corner Columns for Elevator Core
      [-2.3, 2.3].forEach(ex => {{
        [-2.3, 2.3].forEach(ez => {{
          const col = new THREE.Mesh(new THREE.BoxGeometry(0.3, elevatorHeight, 0.3), mullionMat);
          col.position.set(-6.0 + ex, elevatorHeight / 2, 18.0 + ez);
          verticalConnectorsGroup.add(col);
        }});
      }});

      // Animated Glowing Elevator Cab
      const cabGeo = new THREE.BoxGeometry(3.6, 3.2, 3.6);
      const cabMat = new THREE.MeshStandardMaterial({{ color: 0x3B82F6, emissive: 0x1D4ED8, emissiveIntensity: 0.9 }});
      const elevatorCab = new THREE.Mesh(cabGeo, cabMat);
      elevatorCab.position.set(-6.0, 2.0, 18.0);
      verticalConnectorsGroup.add(elevatorCab);

      // Four Radial Stairwells
      const stairwellPositions = [
        {{ x: 6.0, z: 20.0 }},   // South
        {{ x: 0.0, z: -22.0 }},  // North
        {{ x: 22.0, z: 0.0 }},   // East
        {{ x: -22.0, z: 0.0 }}   // West
      ];

      stairwellPositions.forEach(pos => {{
        const stairShaft = new THREE.Mesh(new THREE.BoxGeometry(4.4, elevatorHeight, 4.4), new THREE.MeshStandardMaterial({{
          color: 0xF5B942, transparent: true, opacity: 0.45, roughness: 0.35
        }}));
        stairShaft.position.set(pos.x, elevatorHeight / 2, pos.z);
        verticalConnectorsGroup.add(stairShaft);
      }});

      // Vertical Guide Rods for Exploded View
      stairwellPositions.forEach(pos => {{
        const rod = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 80, 8), new THREE.MeshBasicMaterial({{
          color: 0x35D99A, transparent: true, opacity: 0.35
        }}));
        rod.position.set(pos.x, 40, pos.z);
        guideRodsGroup.add(rod);
      }});
      guideRodsGroup.visible = false;

      // 7. Procedural Interior Furnishings by Room Category
      function addRoomFurnishings(loc, floorGroup) {{
        const cat = loc.category;
        const pos = loc.pos;
        const fl = loc.floor;
        if (fl < 0) return;

        const fGroup = new THREE.Group();
        fGroup.position.set(pos.x, pos.y, pos.z);

        if (cat === 'lab') {{
          if (loc.id.includes('CS') || loc.id.includes('DATA')) {{
            // Computer Labs: Workstation Rows with Dual Monitors
            for (let row = -1.5; row <= 1.5; row += 1.5) {{
              const desk = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.7, 0.9), deskMat);
              desk.position.set(0, 0.35, row);
              const mon1 = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.45, 0.1), monitorMat);
              mon1.position.set(-0.6, 0.9, row);
              const mon2 = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.45, 0.1), monitorMat);
              mon2.position.set(0.6, 0.9, row);
              fGroup.add(desk, mon1, mon2);
            }}
          }} else if (loc.id.includes('HPC') || loc.id.includes('QUANTUM')) {{
            // Supercomputing Cluster: Server Racks with Blinking Cyan LED Activity
            [-1.2, 0, 1.2].forEach(rx => {{
              const rack = new THREE.Mesh(new THREE.BoxGeometry(0.9, 2.2, 1.2), metalTechMat);
              rack.position.set(rx, 1.1, 0);
              const led = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.1, 0.05), monitorMat);
              led.position.set(rx, 1.8, 0.61);
              fGroup.add(rack, led);
            }});
          }} else {{
            // Physics / Chem / Mech / ECE Labs: Workbenches & Apparatus
            const bench = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.85, 1.4), concreteMat);
            bench.position.set(0, 0.42, 0);
            const apparatus = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.6, 0.8), mullionMat);
            apparatus.position.set(0, 1.15, 0);
            fGroup.add(bench, apparatus);
          }}

        }} else if (cat === 'library') {{
          // Library: Bookshelves and Reading Table
          [-1.6, 1.6].forEach(bz => {{
            const shelf = new THREE.Mesh(new THREE.BoxGeometry(3.4, 2.0, 0.6), woodMat);
            shelf.position.set(0, 1.0, bz);
            fGroup.add(shelf);
          }});
          const table = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.7, 1.2), deskMat);
          table.position.set(0, 0.35, 0);
          fGroup.add(table);

        }} else if (cat === 'auditorium' || loc.id.includes('CONF') || loc.id.includes('DEAN') || loc.id.includes('HOD')) {{
          // Executive Conference Table with Seating
          const confTable = new THREE.Mesh(new THREE.CylinderGeometry(1.4, 1.4, 0.7, 16), woodMat);
          confTable.position.set(0, 0.35, 0);
          const screen = new THREE.Mesh(new THREE.BoxGeometry(2.8, 1.2, 0.1), monitorMat);
          screen.position.set(0, 1.8, -1.8);
          fGroup.add(confTable, screen);

        }} else if (cat === 'classroom' || loc.id.includes('SMART')) {{
          // Smart Classroom: Tiered Desks & Display Screen
          [-1.2, 0, 1.2].forEach(cz => {{
            const desk = new THREE.Mesh(new THREE.BoxGeometry(3.0, 0.7, 0.7), deskMat);
            desk.position.set(0, 0.35, cz);
            fGroup.add(desk);
          }});
          const board = new THREE.Mesh(new THREE.BoxGeometry(2.6, 1.1, 0.1), monitorMat);
          board.position.set(0, 1.6, -2.0);
          fGroup.add(board);
        }}

        floorGroup.add(fGroup);
      }}

      // 8. Render All Locations & 3D Spatial Nodes
      function createTextSprite(text, isOutdoor, floorNum) {{
        const canvas = document.createElement('canvas');
        canvas.width = 300;
        canvas.height = 70;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = isOutdoor ? 'rgba(10, 28, 20, 0.92)' : 'rgba(7, 19, 15, 0.92)';
        ctx.roundRect ? ctx.roundRect(4, 4, 292, 62, 10) : ctx.rect(4, 4, 292, 62);
        ctx.fill();
        ctx.strokeStyle = isOutdoor ? '#35D99A' : (floorNum === 0 ? '#10B981' : '#60A5FA');
        ctx.lineWidth = 2.5;
        ctx.stroke();

        ctx.font = 'bold 21px sans-serif';
        ctx.fillStyle = '#F8FAFC';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        const displayTxt = text.length > 21 ? text.substring(0, 20) + '...' : text;
        ctx.fillText(displayTxt, 150, 35);

        const tex = new THREE.CanvasTexture(canvas);
        const mat = new THREE.SpriteMaterial({{ map: tex, depthTest: false }});
        const sprite = new THREE.Sprite(mat);
        sprite.scale.set(6.2, 1.45, 1);
        return sprite;
      }}

      (DATA.locations || []).forEach(loc => {{
        const pos = loc.pos;
        const isOutdoor = loc.is_outdoor;
        const floor = loc.floor;

        let nodeColor = 0x16A36A;
        if (loc.category === 'elevator') nodeColor = 0x60A5FA;
        else if (loc.category === 'stairs') nodeColor = 0xF5B942;
        else if (loc.category === 'restroom') nodeColor = 0x06B6D4;
        else if (loc.category === 'lab') nodeColor = 0x14B8A6;
        else if (loc.category === 'library') nodeColor = 0xF97316;
        else if (loc.category === 'auditorium') nodeColor = 0x8B5CF6;
        else if (isOutdoor) nodeColor = 0x35D99A;

        // Room/Node 3D Volume
        const boxWidth = isOutdoor ? 5.5 : 4.5;
        const boxHeight = isOutdoor ? 2.5 : 2.0;
        const boxGeo = new THREE.BoxGeometry(boxWidth, boxHeight, boxWidth);
        const boxMat = new THREE.MeshStandardMaterial({{
          color: nodeColor,
          roughness: 0.4,
          metalness: 0.2,
          transparent: true,
          opacity: 0.85
        }});
        const nodeMesh = new THREE.Mesh(boxGeo, boxMat);
        nodeMesh.position.set(pos.x, pos.y + boxHeight / 2, pos.z);
        nodeMesh.castShadow = true;
        nodeMesh.receiveShadow = true;

        // Floating Gem
        const gemGeo = new THREE.OctahedronGeometry(0.55, 0);
        const gemMat = new THREE.MeshStandardMaterial({{ color: nodeColor, emissive: nodeColor, emissiveIntensity: 0.8 }});
        const gemMesh = new THREE.Mesh(gemGeo, gemMat);
        gemMesh.position.set(0, boxHeight / 2 + 0.8, 0);
        nodeMesh.add(gemMesh);

        // Billboarding Text Sprite
        const sprite = createTextSprite(loc.name, isOutdoor, floor);
        sprite.position.set(pos.x, pos.y + boxHeight + 1.8, pos.z);
        labelsGroup.add(sprite);

        nodeMesh.userData = {{
          locationData: loc,
          sprite: sprite,
          gem: gemMesh,
          originalColor: new THREE.Color(nodeColor),
          hoverColor: new THREE.Color(nodeColor).clone().multiplyScalar(1.4)
        }};

        if (isOutdoor) {{
          outdoorGroup.add(nodeMesh);
        }} else if (floor >= 0 && floor < 5) {{
          fetFloorGroups[floor].add(nodeMesh);
          addRoomFurnishings(loc, fetFloorGroups[floor]);
        }}

        interactiveLocations.push(nodeMesh);
        locationMeshMap[loc.id] = nodeMesh;
      }});

      // 9. Render Pathways (Corridors, Ramps, Roads, Vertical Elevators & Stairs)
      const pathwayMeshes = {{
        stepfree: [],
        ramp: [],
        elevator: [],
        stairs: [],
        blocked: []
      }};

      (DATA.pathways || []).forEach(edge => {{
        const uPos = edge.source_pos;
        const vPos = edge.dest_pos;

        if (edge.is_cross_floor) return;

        const yLevel = uPos.y + 0.08;
        const p1 = new THREE.Vector3(uPos.x, yLevel, uPos.z);
        const p2 = new THREE.Vector3(vPos.x, yLevel, vPos.z);
        const dist = p1.distanceTo(p2);
        const width = edge.is_outdoor ? 2.5 : 1.4;

        const pathGeo = new THREE.PlaneGeometry(width, dist);
        const pathMat = new THREE.MeshStandardMaterial({{
          color: new THREE.Color(edge.color),
          roughness: 0.6,
          metalness: 0.2,
          side: THREE.DoubleSide
        }});
        const pathMesh = new THREE.Mesh(pathGeo, pathMat);
        pathMesh.position.set((p1.x + p2.x) / 2, yLevel, (p1.z + p2.z) / 2);
        pathMesh.rotation.x = -Math.PI / 2;

        const angle = Math.atan2(p2.x - p1.x, p2.z - p1.z);
        pathMesh.rotation.z = -angle;
        pathMesh.receiveShadow = true;

        if (edge.source_floor === -1) {{
          outdoorGroup.add(pathMesh);
        }} else if (edge.source_floor >= 0 && edge.source_floor < 5) {{
          fetFloorGroups[edge.source_floor].add(pathMesh);
        }}

        // Group into pathway layers
        if (edge.is_blocked) pathwayMeshes.blocked.push(pathMesh);
        else if (edge.has_elevator) pathwayMeshes.elevator.push(pathMesh);
        else if (edge.has_stairs) pathwayMeshes.stairs.push(pathMesh);
        else if (edge.has_ramp) pathwayMeshes.ramp.push(pathMesh);
        else pathwayMeshes.stepfree.push(pathMesh);

        // If blocked hazard, add 3D glowing barrier with hazard stripes
        if (edge.is_blocked) {{
          const barrierGeo = new THREE.BoxGeometry(1.8, 1.1, 0.5);
          const barrierMat = new THREE.MeshStandardMaterial({{
            color: 0xF87171, emissive: 0xDC2626, emissiveIntensity: 1.2
          }});
          const barrierMesh = new THREE.Mesh(barrierGeo, barrierMat);
          barrierMesh.position.set((p1.x + p2.x) / 2, yLevel + 0.55, (p1.z + p2.z) / 2);
          barrierMesh.rotation.y = angle;
          scene.add(barrierMesh);
          pathwayMeshes.blocked.push(barrierMesh);
        }}
      }});

      // 10. Live 3D Navigation Route Spline & Traversal Light Orb (Phase 15 Upgraded)
      let routeCurve = null;
      let traversalOrb = null;
      let navAvatarGroup = null;
      let navRingMesh = null;
      let navConeMesh = null;
      let activeSegmentTube = null;
      let routeAnimProgress = 0;
      let isRouteAnimating = true;
      let animSpeedMultiplier = 1.0;

      // Navigation session state variables
      let navWaypoints = [];
      let navSteps = [];
      let currentNavStepIndex = 0;
      let navStepInterpolation = 0.0;
      let isNavigationActive = false;
      let hasArrivedAtDestination = false;

      const navCard = document.getElementById('nav-live-card');
      const navBadge = document.getElementById('nav-hud-state');
      const navDistText = document.getElementById('nav-hud-dist');
      const navIcon = document.getElementById('nav-hud-icon');
      const navInstructionText = document.getElementById('nav-hud-text');
      const navProgressBar = document.getElementById('nav-hud-progress');
      const navStepCountText = document.getElementById('nav-hud-step-count');

      const btnNavPrev = document.getElementById('nav-btn-prev');
      const btnNavPlayPause = document.getElementById('nav-btn-playpause');
      const btnNavNext = document.getElementById('nav-btn-next');
      const btnNavRestart = document.getElementById('nav-btn-restart');

      function updateNavHUD() {{
        if (!navCard || navWaypoints.length < 2) return;
        navCard.classList.remove('hidden');

        const totalSteps = Math.max(1, navWaypoints.length - 1);
        const currIdx = Math.min(currentNavStepIndex, totalSteps - 1);
        const stepData = (navSteps && navSteps[currIdx]) ? navSteps[currIdx] : null;

        if (hasArrivedAtDestination) {{
          navBadge.className = 'nav-hud-badge arrived';
          navBadge.innerText = 'ARRIVED';
          navIcon.innerText = '🎯';
          const destName = navWaypoints[navWaypoints.length - 1].name || 'Destination';
          navInstructionText.innerText = 'You have arrived at ' + destName + '!';
          navDistText.innerText = '0 m remaining';
          navProgressBar.style.width = '100%';
          navStepCountText.innerText = 'Completed (' + totalSteps + '/' + totalSteps + ')';
          btnNavPlayPause.innerText = '🔄';
          return;
        }}

        if (stepData && stepData.has_elevator) {{
          navBadge.className = 'nav-hud-badge';
          navBadge.innerText = 'ELEVATOR';
        }} else if (stepData && stepData.has_stairs) {{
          navBadge.className = 'nav-hud-badge';
          navBadge.innerText = 'STAIRWAY';
        }} else {{
          navBadge.className = 'nav-hud-badge';
          navBadge.innerText = isNavigationActive ? 'NAVIGATING' : 'PAUSED';
        }}

        if (stepData) {{
          navIcon.innerText = stepData.has_elevator ? '🛗' : (stepData.has_stairs ? '🪜' : (stepData.has_ramp ? '♿' : '🚶'));
          navInstructionText.innerText = stepData.instruction || ('Head to ' + stepData.to_name);
          navDistText.innerText = stepData.distance + ' m segment';
        }} else {{
          navIcon.innerText = '🧭';
          navInstructionText.innerText = 'Proceed along active route.';
        }}

        const overallPct = Math.min(100, Math.round(((currIdx + navStepInterpolation) / totalSteps) * 100));
        navProgressBar.style.width = overallPct + '%';
        navStepCountText.innerText = 'Step ' + (currIdx + 1) + ' of ' + totalSteps;
        btnNavPlayPause.innerText = isNavigationActive ? '⏸️' : '▶️';
      }}

      if (DATA.active_route && DATA.active_route.success && DATA.active_route.waypoints.length > 1) {{
        document.getElementById('legend-route').style.display = 'flex';

        navWaypoints = DATA.active_route.waypoints;
        navSteps = DATA.active_route.steps || [];

        const curvePoints = navWaypoints.map(wp => new THREE.Vector3(wp.x, wp.y, wp.z));
        routeCurve = new THREE.CatmullRomCurve3(curvePoints, false, 'catmullrom', 0.2);

        // 1. Base Pathway Trajectory Tube (Amber Gold)
        const tubeGeo = new THREE.TubeGeometry(routeCurve, Math.max(70, navWaypoints.length * 20), 0.38, 12, false);
        const tubeMat = new THREE.MeshStandardMaterial({{
          color: 0xF59E0B,
          emissive: 0xB45309,
          emissiveIntensity: 0.8,
          roughness: 0.3,
          metalness: 0.7
        }});
        const routeTube = new THREE.Mesh(tubeGeo, tubeMat);
        routeGroup.add(routeTube);

        // 2. Origin Beacon Pin
        const startPt = curvePoints[0];
        const startPin = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 1.0, 3.5, 16), new THREE.MeshStandardMaterial({{
          color: 0x35D99A, emissive: 0x16A36A, emissiveIntensity: 1.2
        }}));
        startPin.position.set(startPt.x, startPt.y + 1.75, startPt.z);
        routeGroup.add(startPin);

        // 3. Destination Flag Sphere
        const destPt = curvePoints[curvePoints.length - 1];
        const destPin = new THREE.Mesh(new THREE.SphereGeometry(1.1, 16, 16), new THREE.MeshStandardMaterial({{
          color: 0xEF4444, emissive: 0xDC2626, emissiveIntensity: 1.5
        }}));
        destPin.position.set(destPt.x, destPt.y + 1.5, destPt.z);
        routeGroup.add(destPin);

        // 4. Interactive Real-Time Navigation Avatar Marker (User Position)
        navAvatarGroup = new THREE.Group();
        navAvatarGroup.position.copy(startPt);

        // Base ground pulsing ring
        const ringGeo = new THREE.RingGeometry(0.85, 1.25, 32);
        ringGeo.rotateX(-Math.PI / 2);
        const ringMat = new THREE.MeshBasicMaterial({{
          color: 0x35D99A,
          side: THREE.DoubleSide,
          transparent: true,
          opacity: 0.85
        }});
        navRingMesh = new THREE.Mesh(ringGeo, ringMat);
        navRingMesh.position.y = 0.05;
        navAvatarGroup.add(navRingMesh);

        // Heading directional cone
        const coneGeo = new THREE.ConeGeometry(0.5, 1.4, 16);
        coneGeo.rotateX(Math.PI / 2);
        const coneMat = new THREE.MeshStandardMaterial({{
          color: 0x10B981,
          emissive: 0x35D99A,
          emissiveIntensity: 1.4,
          metalness: 0.4,
          roughness: 0.2
        }});
        navConeMesh = new THREE.Mesh(coneGeo, coneMat);
        navConeMesh.position.y = 0.7;
        navAvatarGroup.add(navConeMesh);

        // Glowing center light orb
        const avatarOrb = new THREE.Mesh(
          new THREE.SphereGeometry(0.42, 16, 16),
          new THREE.MeshBasicMaterial({{ color: 0xFFFFFF }})
        );
        avatarOrb.position.y = 1.6;
        navAvatarGroup.add(avatarOrb);

        const avatarLight = new THREE.PointLight(0x35D99A, 3.5, 20);
        avatarLight.position.y = 1.6;
        navAvatarGroup.add(avatarLight);

        routeGroup.add(navAvatarGroup);

        // Synchronize with navigation session if provided
        if (DATA.navigation_session) {{
          currentNavStepIndex = Math.min(
            DATA.navigation_session.current_step_index || 0,
            navWaypoints.length - 1
          );
          if (DATA.navigation_session.state === 'NAVIGATING') {{
            isNavigationActive = true;
          }} else if (DATA.navigation_session.state === 'ARRIVED') {{
            hasArrivedAtDestination = true;
            currentNavStepIndex = navWaypoints.length - 1;
          }}
        }} else {{
          isNavigationActive = true;
        }}

        updateNavHUD();

        // Attach Navigation HUD Button Event Handlers
        if (btnNavPlayPause) {{
          btnNavPlayPause.addEventListener('click', () => {{
            if (hasArrivedAtDestination) {{
              hasArrivedAtDestination = false;
              currentNavStepIndex = 0;
              navStepInterpolation = 0.0;
              isNavigationActive = true;
            }} else {{
              isNavigationActive = !isNavigationActive;
            }}
            updateNavHUD();
          }});
        }}
        if (btnNavNext) {{
          btnNavNext.addEventListener('click', () => {{
            if (currentNavStepIndex < navWaypoints.length - 2) {{
              currentNavStepIndex++;
              navStepInterpolation = 0.0;
            }} else {{
              currentNavStepIndex = navWaypoints.length - 1;
              hasArrivedAtDestination = true;
              isNavigationActive = false;
            }}
            updateNavHUD();
          }});
        }}
        if (btnNavPrev) {{
          btnNavPrev.addEventListener('click', () => {{
            hasArrivedAtDestination = false;
            if (currentNavStepIndex > 0) {{
              currentNavStepIndex--;
              navStepInterpolation = 0.0;
            }}
            updateNavHUD();
          }});
        }}
        if (btnNavRestart) {{
          btnNavRestart.addEventListener('click', () => {{
            hasArrivedAtDestination = false;
            currentNavStepIndex = 0;
            navStepInterpolation = 0.0;
            isNavigationActive = true;
            updateNavHUD();
          }});
        }}
      }}

      // 11. Raycasting & Location Inspector
      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();
      let hoveredNode = null;
      let selectedNode = null;

      const locationCard = document.getElementById('location-card');
      const cardTitle = document.getElementById('card-title');
      const cardBadge = document.getElementById('card-badge');
      const cardId = document.getElementById('card-id');
      const cardBuilding = document.getElementById('card-building');
      const cardCategory = document.getElementById('card-category');
      const cardAccess = document.getElementById('card-access');
      const cardConnections = document.getElementById('card-connections');
      const cardAmenities = document.getElementById('card-amenities');
      const cardClose = document.getElementById('card-close');
      const btnFocusRoom = document.getElementById('btn-focus-room');
      const hoverTooltip = document.getElementById('hover-tooltip');

      cardClose.addEventListener('click', () => {{
        locationCard.classList.add('hidden');
        selectedNode = null;
      }});

      function showLocationCard(mesh) {{
        if (!mesh) return;
        const loc = mesh.userData.locationData;
        cardBadge.innerText = loc.floor_name;
        cardBadge.style.color = loc.floor === -1 ? '#35D99A' : (loc.floor === 0 ? '#10B981' : '#60A5FA');
        cardTitle.innerText = loc.name;
        cardId.innerText = loc.id;
        cardBuilding.innerText = loc.building;
        cardCategory.innerText = (loc.category || 'Facility').toUpperCase();
        cardAccess.innerText = loc.wheelchair_accessible ? 'Step-Free Accessible' : 'Stairs Navigation Required';
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
        selectedNode = mesh;
      }}

      // Focus Camera on Selected Room
      btnFocusRoom.addEventListener('click', () => {{
        if (!selectedNode) return;
        const loc = selectedNode.userData.locationData;
        const p = loc.pos;
        tweenCamera(new THREE.Vector3(p.x + 18, p.y + 16, p.z + 20), new THREE.Vector3(p.x, p.y + 1, p.z), 800);
      }});

      window.addEventListener('mousemove', (e) => {{
        const rect = canvas.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(interactiveLocations, false);

        if (intersects.length > 0) {{
          const hit = intersects[0].object;
          canvas.style.cursor = 'pointer';

          if (hoveredNode !== hit) {{
            if (hoveredNode) hoveredNode.material.color.copy(hoveredNode.userData.originalColor);
            hoveredNode = hit;
            hoveredNode.material.color.copy(hoveredNode.userData.hoverColor);
          }}

          hoverTooltip.style.display = 'block';
          hoverTooltip.style.left = e.clientX + 'px';
          hoverTooltip.style.top = e.clientY + 'px';
          hoverTooltip.innerText = hit.userData.locationData.name;
        }} else {{
          canvas.style.cursor = 'default';
          if (hoveredNode) {{
            hoveredNode.material.color.copy(hoveredNode.userData.originalColor);
            hoveredNode = null;
          }}
          hoverTooltip.style.display = 'none';
        }}
      }});

      window.addEventListener('click', (e) => {{
        if (e.target !== canvas) return;
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(interactiveLocations, false);
        if (intersects.length > 0) {{
          showLocationCard(intersects[0].object);
        }}
      }});

      // 12. Camera Tweens & View Modes
      function tweenCamera(targetPos, targetLookAt, duration = 750) {{
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

          if (progress < 1.0) requestAnimationFrame(animateCam);
        }}
        requestAnimationFrame(animateCam);
      }}

      // Camera Presets
      document.getElementById('btn-cam-iso').addEventListener('click', () => {{
        tweenCamera(new THREE.Vector3(110, 120, 140), new THREE.Vector3(15, 6, 15));
      }});
      document.getElementById('btn-cam-top').addEventListener('click', () => {{
        tweenCamera(new THREE.Vector3(0, 240, 0.1), new THREE.Vector3(0, 0, 0));
      }});
      document.getElementById('btn-cam-front').addEventListener('click', () => {{
        tweenCamera(new THREE.Vector3(0, 28, 185), new THREE.Vector3(0, 10, 0));
      }});
      document.getElementById('btn-cam-side').addEventListener('click', () => {{
        tweenCamera(new THREE.Vector3(185, 28, 0), new THREE.Vector3(0, 10, 0));
      }});
      document.getElementById('btn-cam-fet').addEventListener('click', () => {{
        tweenCamera(new THREE.Vector3(48, 42, 52), new THREE.Vector3(0, 12, 0));
      }});
      document.getElementById('btn-cam-reset').addEventListener('click', () => {{
        tweenCamera(new THREE.Vector3(110, 120, 140), new THREE.Vector3(15, 6, 15));
      }});

      // Domain Modes
      document.getElementById('btn-mode-all').addEventListener('click', () => {{
        outdoorGroup.visible = true;
        fetBuildingGroup.visible = true;
        tweenCamera(new THREE.Vector3(110, 120, 140), new THREE.Vector3(15, 6, 15));
      }});
      document.getElementById('btn-mode-outdoor').addEventListener('click', () => {{
        outdoorGroup.visible = true;
        fetBuildingGroup.visible = true;
        tweenCamera(new THREE.Vector3(140, 150, 180), new THREE.Vector3(40, 0, 30));
      }});
      document.getElementById('btn-mode-fet').addEventListener('click', () => {{
        outdoorGroup.visible = false;
        fetBuildingGroup.visible = true;
        tweenCamera(new THREE.Vector3(48, 42, 52), new THREE.Vector3(0, 12, 0));
      }});

      // View Modes: Exterior vs Cutaway (Interior)
      document.getElementById('btn-view-exterior').addEventListener('click', (e) => {{
        document.getElementById('btn-view-exterior').classList.add('active');
        document.getElementById('btn-view-cutaway').classList.remove('active');
        exteriorCurtainWalls.forEach(w => {{
          w.visible = true;
          w.material.opacity = 0.55;
        }});
      }});
      document.getElementById('btn-view-cutaway').addEventListener('click', (e) => {{
        document.getElementById('btn-view-cutaway').classList.add('active');
        document.getElementById('btn-view-exterior').classList.remove('active');
        exteriorCurtainWalls.forEach(w => {{
          w.visible = true;
          w.material.opacity = 0.12; // transparent cutaway
        }});
      }});

      // Floor Modes: Stacked vs Exploded
      let isExploded = false;

      function resetFloorPositions() {{
        for (let fl = 0; fl < 5; fl++) {{
          fetFloorGroups[fl].visible = true;
          fetFloorGroups[fl].position.y = 0;
        }}
        verticalConnectorsGroup.visible = true;
        guideRodsGroup.visible = false;
      }}

      document.getElementById('btn-fl-all').addEventListener('click', () => {{
        isExploded = false;
        resetFloorPositions();
        tweenCamera(new THREE.Vector3(48, 42, 52), new THREE.Vector3(0, 12, 0));
      }});

      document.getElementById('btn-fl-exploded').addEventListener('click', () => {{
        isExploded = true;
        for (let fl = 0; fl < 5; fl++) {{
          fetFloorGroups[fl].visible = true;
          fetFloorGroups[fl].position.y = fl * 14.0; // Elevate floors vertically
        }}
        verticalConnectorsGroup.visible = true;
        guideRodsGroup.visible = true;
        tweenCamera(new THREE.Vector3(75, 90, 100), new THREE.Vector3(0, 35, 0));
      }});

      for (let fl = 0; fl < 5; fl++) {{
        document.getElementById('btn-fl-' + fl).addEventListener('click', () => {{
          isExploded = false;
          for (let f = 0; f < 5; f++) {{
            fetFloorGroups[f].visible = (f === fl);
            fetFloorGroups[f].position.y = 0;
          }}
          verticalConnectorsGroup.visible = false;
          guideRodsGroup.visible = false;
          tweenCamera(new THREE.Vector3(42, 32, 46), new THREE.Vector3(0, floorElevations[fl], 0));
        }});
      }}

      // Route Animation Controls
      document.getElementById('btn-anim-toggle').addEventListener('click', (e) => {{
        isRouteAnimating = !isRouteAnimating;
        e.target.classList.toggle('active', isRouteAnimating);
      }});

      const speeds = [1.0, 2.0, 0.5];
      let speedIdx = 0;
      document.getElementById('btn-anim-speed').addEventListener('click', (e) => {{
        speedIdx = (speedIdx + 1) % speeds.length;
        animSpeedMultiplier = speeds[speedIdx];
        e.target.innerText = '⚡ ' + animSpeedMultiplier + 'x';
      }});

      let areLabelsOn = true;
      document.getElementById('btn-labels-toggle').addEventListener('click', (e) => {{
        areLabelsOn = !areLabelsOn;
        labelsGroup.visible = areLabelsOn;
        e.target.classList.toggle('active', areLabelsOn);
      }});

      // 13. Animation Loop & Resize
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

        const time = clock.getElapsedTime();

        // Animate floating gems
        interactiveLocations.forEach(mesh => {{
          if (mesh.userData.gem) {{
            mesh.userData.gem.rotation.y += delta * 1.5;
            mesh.userData.gem.position.y = 1.8 + Math.sin(time * 2.5 + mesh.userData.locationData.pos.x) * 0.12;
          }}
        }});

        // Animate Elevator Cab in Vertical Shaft
        if (elevatorCab) {{
          elevatorCab.position.y = 2.0 + (Math.sin(time * 0.8) + 1.0) * 10.0;
        }}

        // Animate Real-Time Navigation Avatar Marker (Phase 15 Upgraded)
        if (navAvatarGroup && navWaypoints.length > 1) {{
          // Pulse the ground ring
          if (navRingMesh) {{
            const ringScale = 1.0 + Math.sin(time * 4.0) * 0.15;
            navRingMesh.scale.set(ringScale, ringScale, 1.0);
          }}

          if (isNavigationActive && !hasArrivedAtDestination) {{
            navStepInterpolation += delta * 0.35 * animSpeedMultiplier;
            if (navStepInterpolation >= 1.0) {{
              navStepInterpolation = 0.0;
              currentNavStepIndex++;
              if (currentNavStepIndex >= navWaypoints.length - 1) {{
                currentNavStepIndex = navWaypoints.length - 1;
                hasArrivedAtDestination = true;
                isNavigationActive = false;
              }}
              updateNavHUD();
            }}

            const pStart = navWaypoints[currentNavStepIndex];
            const pEnd = navWaypoints[Math.min(currentNavStepIndex + 1, navWaypoints.length - 1)];

            if (pStart && pEnd) {{
              const curX = pStart.x + (pEnd.x - pStart.x) * navStepInterpolation;
              const curY = pStart.y + (pEnd.y - pStart.y) * navStepInterpolation;
              const curZ = pStart.z + (pEnd.z - pStart.z) * navStepInterpolation;
              navAvatarGroup.position.set(curX, curY, curZ);

              // Orient cone forward along trajectory
              if (navConeMesh) {{
                const targetVec = new THREE.Vector3(pEnd.x, curY + 0.7, pEnd.z);
                navConeMesh.lookAt(targetVec);
              }}

              // If elevator transition is occurring, animate elevator cab to match marker Y
              const currStepData = (navSteps && navSteps[currentNavStepIndex]) ? navSteps[currentNavStepIndex] : null;
              if (currStepData && currStepData.has_elevator && elevatorCab) {{
                elevatorCab.position.y = curY;
              }}
            }}
          }} else if (hasArrivedAtDestination) {{
            const destPt = navWaypoints[navWaypoints.length - 1];
            navAvatarGroup.position.set(destPt.x, destPt.y, destPt.z);
            if (navRingMesh) {{
              const pulse = 1.0 + (Math.sin(time * 6.0) + 1.0) * 0.35;
              navRingMesh.scale.set(pulse, pulse, 1.0);
            }}
          }}
        }} else if (routeCurve && traversalOrb && isRouteAnimating) {{
          routeAnimProgress = (routeAnimProgress + delta * 0.12 * animSpeedMultiplier) % 1.0;
          const pt = routeCurve.getPoint(routeAnimProgress);
          traversalOrb.position.copy(pt);
        }}

        renderer.render(scene, camera);
      }}

      animate();
    }})();
  </script>
</body>
</html>"""
    return html_code
