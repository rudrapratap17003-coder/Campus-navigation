"""Three.js 3D Digital Twin Engine for JAIN Global Campus & FET 5-Floor Building.

Reconstructs:
1. JAIN Global Campus (Jakkasandra Post, Kanakapura Taluk, Ramanagara District, Karnataka, India):
   - Outdoor 3D buildings: FET Complex, Colosseum Arena, JIRS Aquatic Pool, Cricket Stadium,
     Sports Grounds, SBMJCE Dining Complex, Student Hostels, Admin Block, Aerospace Research Hangar.
   - Outdoor arterial avenues, pedestrian pathways, parking zones, and Kanakapura Road gateway.
2. Faculty of Engineering and Technology (FET) 5-Floor Complex:
   - Ground Floor (Level 0), First Floor (Level 1), Second Floor (Level 2), Third Floor (Level 3), Fourth Floor (Level 4).
   - Annular octagonal building footprint with central semi-circular tiered amphitheater.
   - Four vertical staircase towers (North, East, South, West) and central wheelchair-accessible elevator shaft.
   - Exploded 5-floor building presentation and individual floor isolation.
3. Unified Navigation Graph:
   - Outdoor campus pathways -> FET West Ramp / Front Portico -> 5-Floor Indoor Corridors -> Elevator/Stairs -> Room.
   - Full authoritative Python route calculation with animated 3D glowing spline trajectories.
4. Dynamic SQLite Obstacle Synchronization:
   - Verified obstacles render as glowing crimson red barriers with hazard blocks.
   - Automatic live detour recalculation.
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

# Theme Palette
PALETTE = {
    "primary_bg": "#07130F",
    "secondary_bg": "#0D1F18",
    "card_bg": "#122820",
    "building_surface": "#1C382C",
    "building_roof": "#264D3D",
    "fet_slab": "#0F261D",
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

        # Scale and position coordinates
        x_val = float(loc.get("x", 0.0))
        z_val = float(loc.get("y", 0.0))

        # Determine neighbors
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
            "is_accessible": False,
            "algorithm_used": algorithm.upper(),
        }

    path_nodes = route_res.path
    waypoints: List[Dict[str, Any]] = []

    for i, loc_id in enumerate(path_nodes):
        loc = campus_map.get_location(loc_id) or {}
        fl = int(loc.get("floor", 0))
        elev_y = FLOOR_ELEVATIONS.get(fl, 0.5) + 0.4  # Slightly above floor
        x_val = float(loc.get("x", 0.0))
        z_val = float(loc.get("y", 0.0))

        waypoints.append({
            "id": loc_id,
            "name": loc.get("name", loc_id),
            "floor": fl,
            "x": round(x_val, 2),
            "y": round(elev_y, 2),
            "z": round(z_val, 2),
            "step_index": i,
        })

        # Inject vertical transit intermediate waypoint if next node is on a different floor
        if i < len(path_nodes) - 1:
            next_id = path_nodes[i + 1]
            next_loc = campus_map.get_location(next_id) or {}
            next_fl = int(next_loc.get("floor", 0))
            if fl != next_fl:
                next_y = FLOOR_ELEVATIONS.get(next_fl, 0.5) + 0.4
                mid_y = (elev_y + next_y) / 2.0
                waypoints.append({
                    "id": f"{loc_id}_TRANSIT_{next_id}",
                    "name": f"Vertical Shaft Transfer (Floor {fl} -> Floor {next_fl})",
                    "floor": -99,
                    "x": round((x_val + float(next_loc.get("x", 0.0))) / 2.0, 2),
                    "y": round(mid_y, 2),
                    "z": round((z_val + float(next_loc.get("y", 0.0))) / 2.0, 2),
                    "step_index": i + 0.5,
                    "is_transition": True,
                })

    # Steps serialization
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

    # Cross-floor transition alerts
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
    if route_finder and start_id and dest_id and start_id != dest_id:
        active_route = get_jain_3d_route_data(
            campus_map=campus_map,
            route_finder=route_finder,
            start_id=start_id,
            dest_id=dest_id,
            algorithm=algorithm,
            wheelchair_accessible=wheelchair_accessible,
        )

    active_obstacles: List[Dict[str, Any]] = []
    if obstacle_manager:
        try:
            active_obstacles = obstacle_manager.get_active_obstacles()
        except Exception:
            active_obstacles = []

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
        "active_obstacles": active_obstacles,
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
      background: rgba(13, 31, 24, 0.88);
      border: 1px solid rgba(53, 217, 154, 0.3);
      border-radius: 12px;
      padding: 6px 10px;
      backdrop-filter: blur(10px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
      pointer-events: auto;
    }}
    .hud-title {{
      font-size: 12px;
      font-weight: 700;
      color: #35D99A;
      margin-right: 4px;
      display: flex;
      align-items: center;
      gap: 5px;
    }}
    .hud-btn {{
      background: rgba(22, 163, 106, 0.15);
      border: 1px solid rgba(53, 217, 154, 0.3);
      color: #F8FAFC;
      border-radius: 8px;
      padding: 5px 9px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 4px;
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
      bottom: 18px;
      left: 18px;
      width: 320px;
      max-width: calc(100% - 36px);
      background: rgba(13, 31, 24, 0.94);
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
      background: rgba(13, 31, 24, 0.88);
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
        <button class="hud-btn" id="btn-cam-top">Top View</button>
        <button class="hud-btn" id="btn-cam-front">Front</button>
        <button class="hud-btn" id="btn-cam-reset">🔄 Reset</button>
      </div>

      <!-- Domain View Mode -->
      <div class="hud-group">
        <span class="hud-title">🌐 Domain:</span>
        <button class="hud-btn active" id="btn-mode-all">All Campus & FET</button>
        <button class="hud-btn" id="btn-mode-outdoor">Outdoor Campus</button>
        <button class="hud-btn" id="btn-mode-fet">FET Building</button>
      </div>

      <!-- FET 5-Floor Isolation & Exploded Controls -->
      <div class="hud-group" id="group-floors">
        <span class="hud-title">🏢 FET Levels:</span>
        <button class="hud-btn active" id="btn-fl-all">Stacked</button>
        <button class="hud-btn" id="btn-fl-exploded">💥 Exploded 5F</button>
        <button class="hud-btn" id="btn-fl-0">G</button>
        <button class="hud-btn" id="btn-fl-1">1F</button>
        <button class="hud-btn" id="btn-fl-2">2F</button>
        <button class="hud-btn" id="btn-fl-3">3F</button>
        <button class="hud-btn" id="btn-fl-4">4F</button>
      </div>

      <!-- Animation / Labels -->
      <div class="hud-group">
        <button class="hud-btn active" id="btn-anim-toggle">⏯️ Traversal</button>
        <button class="hud-btn active" id="btn-labels-toggle">🏷️ Labels</button>
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
        <span>Wheelchair Access:</span>
        <span class="val" id="card-access" style="color: #35D99A;">Step-Free Accessible</span>
      </div>
      <div class="card-row">
        <span>Connected Paths:</span>
        <span class="val" id="card-connections">3 routes</span>
      </div>
      <div style="margin-top: 6px; font-size: 11px; color: #9CAFA5; font-weight: 600;">Verified Amenities:</div>
      <div class="amenities-list" id="card-amenities">
        <!-- Rendered dynamically -->
      </div>
    </div>

    <!-- 3D Legend -->
    <div class="hud-legend">
      <div style="font-weight: 700; color: #35D99A; margin-bottom: 2px;">Campus Digital Twin:</div>
      <div class="legend-item"><div class="legend-dot" style="background: #16A36A;"></div><span>Step-Free Accessible Pathway</span></div>
      <div class="legend-item"><div class="legend-dot" style="background: #35D99A;"></div><span>Access Ramp</span></div>
      <div class="legend-item"><div class="legend-dot" style="background: #60A5FA;"></div><span>Elevator Vertical Shaft (5 Floors)</span></div>
      <div class="legend-item"><div class="legend-dot" style="background: #F5B942;"></div><span>Stairwell Towers</span></div>
      <div class="legend-item"><div class="legend-dot" style="background: #F87171;"></div><span>Verified Blocked Hazard</span></div>
      <div class="legend-item" id="legend-route" style="display: none;"><div class="legend-dot" style="background: #F59E0B;"></div><span>Live Navigation Trajectory</span></div>
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
      scene.fog = new THREE.FogExp2(0x07130F, 0.0035);

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
      renderer.toneMappingExposure = 1.15;
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;

      const controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.maxPolarAngle = Math.PI / 2 - 0.02;
      controls.minDistance = 15;
      controls.maxDistance = 600;
      controls.target.set(20, 5, 20);

      // Lighting Rig
      const ambientLight = new THREE.AmbientLight(0x133829, 0.9);
      scene.add(ambientLight);

      const sunLight = new THREE.DirectionalLight(0xFFFFFF, 1.1);
      sunLight.position.set(150, 220, 120);
      sunLight.castShadow = true;
      sunLight.shadow.mapSize.width = 2048;
      sunLight.shadow.mapSize.height = 2048;
      sunLight.shadow.camera.near = 10;
      sunLight.shadow.camera.far = 600;
      sunLight.shadow.camera.left = -180;
      sunLight.shadow.camera.right = 180;
      sunLight.shadow.camera.top = 180;
      sunLight.shadow.camera.bottom = -180;
      scene.add(sunLight);

      const blueFill = new THREE.DirectionalLight(0x60A5FA, 0.4);
      blueFill.position.set(-150, 100, -150);
      scene.add(blueFill);

      // Groups for Hierarchical Layer Control
      const outdoorGroup = new THREE.Group();
      const fetBuildingGroup = new THREE.Group();
      const fetFloorGroups = [new THREE.Group(), new THREE.Group(), new THREE.Group(), new THREE.Group(), new THREE.Group()];
      const verticalConnectorsGroup = new THREE.Group();
      const labelsGroup = new THREE.Group();
      const routeGroup = new THREE.Group();

      scene.add(outdoorGroup);
      scene.add(fetBuildingGroup);
      fetFloorGroups.forEach(fg => fetBuildingGroup.add(fg));
      fetBuildingGroup.add(verticalConnectorsGroup);
      scene.add(labelsGroup);
      scene.add(routeGroup);

      // 2. Build Outdoor Campus Landscape & External Buildings
      // Ground plane
      const terrainGeo = new THREE.PlaneGeometry(500, 500);
      const terrainMat = new THREE.MeshStandardMaterial({{ color: 0x0A1C14, roughness: 0.9, metalness: 0.1 }});
      const terrainMesh = new THREE.Mesh(terrainGeo, terrainMat);
      terrainMesh.rotation.x = -Math.PI / 2;
      terrainMesh.position.y = -0.1;
      terrainMesh.receiveShadow = true;
      outdoorGroup.add(terrainMesh);

      // Kanakapura Road (NH-948)
      const roadGeo = new THREE.PlaneGeometry(450, 22);
      const roadMat = new THREE.MeshStandardMaterial({{ color: 0x1A231F, roughness: 0.8 }});
      const roadMesh = new THREE.Mesh(roadGeo, roadMat);
      roadMesh.rotation.x = -Math.PI / 2;
      roadMesh.position.set(0, 0.01, 155);
      roadMesh.receiveShadow = true;
      outdoorGroup.add(roadMesh);

      // Outdoor Buildings Representation
      const buildingMeshes = [];
      const interactiveLocations = [];
      const locationMeshMap = {{}};

      (DATA.buildings || []).forEach(bld => {{
        if (bld.id === 'BLD_FET') return; // Handled separately as 5-Floor detailed structure

        let bldGeo;
        let bldMat = new THREE.MeshStandardMaterial({{
          color: bld.category === 'sports' ? 0x2A453B : 0x1E3B2F,
          roughness: 0.5,
          metalness: 0.25
        }});

        if (bld.shape === 'oval') {{
          bldGeo = new THREE.CylinderGeometry(bld.width / 2, bld.width / 2, bld.height, 32);
        }} else if (bld.shape === 'pool') {{
          bldGeo = new THREE.BoxGeometry(bld.width, bld.height, bld.depth);
          bldMat = new THREE.MeshStandardMaterial({{ color: 0x0284C7, roughness: 0.3 }});
        }} else {{
          bldGeo = new THREE.BoxGeometry(bld.width, bld.height, bld.depth);
        }}

        const bldMesh = new THREE.Mesh(bldGeo, bldMat);
        bldMesh.position.set(bld.center_x, bld.height / 2, bld.center_z);
        bldMesh.castShadow = true;
        bldMesh.receiveShadow = true;

        // Wireframe architectural accent
        const edges = new THREE.EdgesGeometry(bldGeo);
        const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({{ color: 0x35D99A, transparent: true, opacity: 0.3 }}));
        bldMesh.add(line);

        bldMesh.userData = {{ buildingData: bld }};
        outdoorGroup.add(bldMesh);
        buildingMeshes.push(bldMesh);
      }});

      // 3. Reconstruct FET 5-Floor Detailed Building
      // Annular Octagonal Building Slabs for all 5 floors
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

        const extrudeSettings = {{ depth: thickness, bevelEnabled: true, bevelThickness: 0.2, bevelSize: 0.2, bevelSegments: 3 }};
        return new THREE.ExtrudeGeometry(shape, extrudeSettings);
      }}

      const slabThickness = 0.5;
      const floorElevations = [0.2, 6.2, 12.2, 18.2, 24.2];

      for (let fl = 0; fl < 5; fl++) {{
        const slabGeo = createOctagonalFloorSlab(40, slabThickness);
        const slabMat = new THREE.MeshStandardMaterial({{
          color: fl === 0 ? 0x0E261D : 0x123024,
          roughness: 0.4,
          metalness: 0.25,
          transparent: true,
          opacity: 0.88
        }});
        const slabMesh = new THREE.Mesh(slabGeo, slabMat);
        slabMesh.rotation.x = -Math.PI / 2;
        slabMesh.position.set(0, floorElevations[fl], 0);
        slabMesh.receiveShadow = true;
        fetFloorGroups[fl].add(slabMesh);

        // Ground Floor Central Amphitheater Concentric Steps
        if (fl === 0) {{
          for (let step = 1; step <= 5; step++) {{
            const stepGeo = new THREE.CylinderGeometry(step * 3.2, step * 3.2, 0.4, 32, 1, false, 0, Math.PI);
            const stepMat = new THREE.MeshStandardMaterial({{ color: 0x1B4332, roughness: 0.7 }});
            const stepMesh = new THREE.Mesh(stepGeo, stepMat);
            stepMesh.position.set(0, 0.2 + (5 - step) * 0.3, 0);
            stepMesh.rotation.y = Math.PI / 2;
            fetFloorGroups[0].add(stepMesh);
          }}
        }}
      }}

      // 4. Vertical Circulation (Elevator Shaft + 4 Stairwells across all 5 Floors)
      // Elevator Glass Shaft Tower (Serving Level 0 to Level 4, Height ~ 26m)
      const elevatorHeight = 25.5;
      const elevShaftGeo = new THREE.BoxGeometry(4.5, elevatorHeight, 4.5);
      const elevShaftMat = new THREE.MeshStandardMaterial({{
        color: 0x60A5FA,
        transparent: true,
        opacity: 0.35,
        roughness: 0.1,
        metalness: 0.8
      }});
      const elevShaft = new THREE.Mesh(elevShaftGeo, elevShaftMat);
      elevShaft.position.set(-6.0, elevatorHeight / 2, 18.0);
      verticalConnectorsGroup.add(elevShaft);

      // Glowing Elevator Cab
      const cabGeo = new THREE.BoxGeometry(3.5, 3.0, 3.5);
      const cabMat = new THREE.MeshStandardMaterial({{
        color: 0x3B82F6,
        emissive: 0x1D4ED8,
        emissiveIntensity: 0.8
      }});
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
        const stairShaftGeo = new THREE.BoxGeometry(4.2, elevatorHeight, 4.2);
        const stairShaftMat = new THREE.MeshStandardMaterial({{
          color: 0xF5B942,
          transparent: true,
          opacity: 0.45,
          roughness: 0.3
        }});
        const stairShaft = new THREE.Mesh(stairShaftGeo, stairShaftMat);
        stairShaft.position.set(pos.x, elevatorHeight / 2, pos.z);
        verticalConnectorsGroup.add(stairShaft);
      }});

      // 5. Render All Locations & 3D Spatial Nodes
      function createTextSprite(text, isOutdoor, floorNum) {{
        const canvas = document.createElement('canvas');
        canvas.width = 300;
        canvas.height = 70;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = isOutdoor ? 'rgba(10, 28, 20, 0.92)' : 'rgba(7, 19, 15, 0.9)';
        ctx.roundRect ? ctx.roundRect(4, 4, 292, 62, 12) : ctx.rect(4, 4, 292, 62);
        ctx.fill();
        ctx.strokeStyle = isOutdoor ? '#35D99A' : (floorNum === 0 ? '#10B981' : '#60A5FA');
        ctx.lineWidth = 3;
        ctx.stroke();

        ctx.font = 'bold 22px sans-serif';
        ctx.fillStyle = '#F8FAFC';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        const displayTxt = text.length > 20 ? text.substring(0, 19) + '...' : text;
        ctx.fillText(displayTxt, 150, 35);

        const tex = new THREE.CanvasTexture(canvas);
        const mat = new THREE.SpriteMaterial({{ map: tex, depthTest: false }});
        const sprite = new THREE.Sprite(mat);
        sprite.scale.set(6.5, 1.5, 1);
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
        const gemGeo = new THREE.OctahedronGeometry(0.6, 0);
        const gemMat = new THREE.MeshStandardMaterial({{ color: nodeColor, emissive: nodeColor, emissiveIntensity: 0.8 }});
        const gemMesh = new THREE.Mesh(gemGeo, gemMat);
        gemMesh.position.set(0, boxHeight / 2 + 0.8, 0);
        nodeMesh.add(gemMesh);

        // Billboarding Text Sprite
        const sprite = createTextSprite(loc.name, isOutdoor, floor);
        sprite.position.set(pos.x, pos.y + boxHeight + 2.0, pos.z);
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
        }}

        interactiveLocations.push(nodeMesh);
        locationMeshMap[loc.id] = nodeMesh;
      }});

      // 6. Render Pathways (Corridors, Ramps, Roads, Vertical Elevators & Stairs)
      (DATA.pathways || []).forEach(edge => {{
        const uPos = edge.source_pos;
        const vPos = edge.dest_pos;

        if (edge.is_cross_floor) {{
          // Cross-floor connections handled by elevator shaft & stair tower models
          return;
        }}

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

        // If blocked hazard, add 3D red warning block
        if (edge.is_blocked) {{
          const barrierGeo = new THREE.BoxGeometry(1.8, 1.0, 0.5);
          const barrierMat = new THREE.MeshStandardMaterial({{ color: 0xF87171, emissive: 0xDC2626, emissiveIntensity: 1.0 }});
          const barrierMesh = new THREE.Mesh(barrierGeo, barrierMat);
          barrierMesh.position.set((p1.x + p2.x) / 2, yLevel + 0.5, (p1.z + p2.z) / 2);
          barrierMesh.rotation.y = angle;
          scene.add(barrierMesh);
        }}
      }});

      // 7. Live 3D Navigation Route Spline & Traveling Light Orb
      let routeCurve = null;
      let traversalOrb = null;
      let routeAnimProgress = 0;
      let isRouteAnimating = true;

      if (DATA.active_route && DATA.active_route.success && DATA.active_route.waypoints.length > 1) {{
        document.getElementById('legend-route').style.display = 'flex';

        const waypoints = DATA.active_route.waypoints;
        const curvePoints = waypoints.map(wp => new THREE.Vector3(wp.x, wp.y, wp.z));
        routeCurve = new THREE.CatmullRomCurve3(curvePoints, false, 'catmullrom', 0.2);

        // Glowing 3D Tube
        const tubeGeo = new THREE.TubeGeometry(routeCurve, Math.max(60, waypoints.length * 20), 0.45, 12, false);
        const tubeMat = new THREE.MeshStandardMaterial({{
          color: 0xF59E0B,
          emissive: 0xF59E0B,
          emissiveIntensity: 1.4,
          roughness: 0.1,
          metalness: 0.8
        }});
        const routeTube = new THREE.Mesh(tubeGeo, tubeMat);
        routeGroup.add(routeTube);

        // Origin Beacon Pin
        const startPt = curvePoints[0];
        const startPinGeo = new THREE.CylinderGeometry(0.3, 1.0, 3.5, 16);
        const startPinMat = new THREE.MeshStandardMaterial({{ color: 0x35D99A, emissive: 0x16A36A, emissiveIntensity: 1.2 }});
        const startPin = new THREE.Mesh(startPinGeo, startPinMat);
        startPin.position.set(startPt.x, startPt.y + 1.75, startPt.z);
        routeGroup.add(startPin);

        // Destination Pin
        const destPt = curvePoints[curvePoints.length - 1];
        const destPinGeo = new THREE.SphereGeometry(1.0, 16, 16);
        const destPinMat = new THREE.MeshStandardMaterial({{ color: 0xEF4444, emissive: 0xDC2626, emissiveIntensity: 1.5 }});
        const destPin = new THREE.Mesh(destPinGeo, destPinMat);
        destPin.position.set(destPt.x, destPt.y + 1.5, destPt.z);
        routeGroup.add(destPin);

        // Animated Traversal Light Orb
        const orbGeo = new THREE.SphereGeometry(0.7, 16, 16);
        const orbMat = new THREE.MeshBasicMaterial({{ color: 0xFFFFFF }});
        traversalOrb = new THREE.Mesh(orbGeo, orbMat);
        traversalOrb.position.copy(startPt);
        routeGroup.add(traversalOrb);

        const orbLight = new THREE.PointLight(0xF59E0B, 3.0, 25);
        traversalOrb.add(orbLight);
      }}

      // 8. Raycasting & Location Selection
      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();
      let hoveredNode = null;
      let selectedNode = null;

      const locationCard = document.getElementById('location-card');
      const cardTitle = document.getElementById('card-title');
      const cardBadge = document.getElementById('card-badge');
      const cardId = document.getElementById('card-id');
      const cardBuilding = document.getElementById('card-building');
      const cardAccess = document.getElementById('card-access');
      const cardConnections = document.getElementById('card-connections');
      const cardAmenities = document.getElementById('card-amenities');
      const cardClose = document.getElementById('card-close');
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

      // 9. Camera Tweens & View Modes
      function tweenCamera(targetPos, targetLookAt, duration = 700) {{
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
        tweenCamera(new THREE.Vector3(110, 120, 140), new THREE.Vector3(20, 5, 20));
      }});
      document.getElementById('btn-cam-top').addEventListener('click', () => {{
        tweenCamera(new THREE.Vector3(0, 240, 0.1), new THREE.Vector3(0, 0, 0));
      }});
      document.getElementById('btn-cam-front').addEventListener('click', () => {{
        tweenCamera(new THREE.Vector3(0, 30, 190), new THREE.Vector3(0, 10, 0));
      }});
      document.getElementById('btn-cam-reset').addEventListener('click', () => {{
        tweenCamera(new THREE.Vector3(110, 120, 140), new THREE.Vector3(20, 5, 20));
      }});

      // Domain Modes (All, Outdoor Only, FET Only)
      document.getElementById('btn-mode-all').addEventListener('click', () => {{
        outdoorGroup.visible = true;
        fetBuildingGroup.visible = true;
        tweenCamera(new THREE.Vector3(110, 120, 140), new THREE.Vector3(20, 5, 20));
      }});
      document.getElementById('btn-mode-outdoor').addEventListener('click', () => {{
        outdoorGroup.visible = true;
        fetBuildingGroup.visible = true;
        tweenCamera(new THREE.Vector3(140, 150, 180), new THREE.Vector3(40, 0, 30));
      }});
      document.getElementById('btn-mode-fet').addEventListener('click', () => {{
        outdoorGroup.visible = false;
        fetBuildingGroup.visible = true;
        tweenCamera(new THREE.Vector3(55, 45, 60), new THREE.Vector3(0, 12, 0));
      }});

      // FET 5-Floor Isolation & Exploded Modes
      let isExploded = false;

      function resetFloorPositions() {{
        for (let fl = 0; fl < 5; fl++) {{
          fetFloorGroups[fl].visible = true;
          fetFloorGroups[fl].position.y = 0;
        }}
        verticalConnectorsGroup.visible = true;
      }}

      document.getElementById('btn-fl-all').addEventListener('click', () => {{
        isExploded = false;
        resetFloorPositions();
        tweenCamera(new THREE.Vector3(55, 45, 60), new THREE.Vector3(0, 12, 0));
      }});

      document.getElementById('btn-fl-exploded').addEventListener('click', () => {{
        isExploded = true;
        for (let fl = 0; fl < 5; fl++) {{
          fetFloorGroups[fl].visible = true;
          fetFloorGroups[fl].position.y = fl * 12.0; // Elevate floors vertically
        }}
        verticalConnectorsGroup.visible = true;
        tweenCamera(new THREE.Vector3(75, 85, 95), new THREE.Vector3(0, 30, 0));
      }});

      for (let fl = 0; fl < 5; fl++) {{
        document.getElementById('btn-fl-' + fl).addEventListener('click', () => {{
          isExploded = false;
          for (let f = 0; f < 5; f++) {{
            fetFloorGroups[f].visible = (f === fl);
            fetFloorGroups[f].position.y = 0;
          }}
          verticalConnectorsGroup.visible = false;
          tweenCamera(new THREE.Vector3(45, 35, 50), new THREE.Vector3(0, floorElevations[fl], 0));
        }});
      }}

      // Animation & Label Toggles
      document.getElementById('btn-anim-toggle').addEventListener('click', (e) => {{
        isRouteAnimating = !isRouteAnimating;
        e.target.classList.toggle('active', isRouteAnimating);
      }});

      let areLabelsOn = true;
      document.getElementById('btn-labels-toggle').addEventListener('click', (e) => {{
        areLabelsOn = !areLabelsOn;
        labelsGroup.visible = areLabelsOn;
        e.target.classList.toggle('active', areLabelsOn);
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

        // Animate floating gems
        const time = clock.getElapsedTime();
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

        // Animate Route Traversal Light
        if (routeCurve && traversalOrb && isRouteAnimating) {{
          routeAnimProgress = (routeAnimProgress + delta * 0.12) % 1.0;
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
