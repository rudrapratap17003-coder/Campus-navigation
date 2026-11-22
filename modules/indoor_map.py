"""Advanced interactive indoor campus map and schematic navigation visualizer.

Provides multi-floor topological layouts, floor-by-floor filtering, cross-floor
elevator transitions, route highlighting, and real-time obstacle visualization.

DISCLAIMER:
Coordinates and node positions are schematic graph-layout coordinates designed
strictly for connectivity visualization and pathfinding demonstration. They do
not represent surveyed architectural CAD blueprints or surveyed physical dimensions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
import plotly.graph_objects as go

from modules.campus_map import CampusMap


def get_floors_in_campus(campus_map: CampusMap) -> List[int]:
    """Retrieve sorted list of all unique floor numbers present in the campus graph.

    Args:
        campus_map: CampusMap instance.

    Returns:
        Sorted list of integer floor levels (e.g. [0, 1]).
    """
    floors: Set[int] = set()
    for loc in campus_map.get_all_locations():
        fl = loc.get("floor")
        if fl is not None:
            try:
                floors.add(int(fl))
            except (ValueError, TypeError):
                pass
    return sorted(floors) if floors else [0]


def get_locations_for_floor(
    campus_map: CampusMap, floor: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Retrieve locations filtered by floor level.

    Args:
        campus_map: CampusMap instance.
        floor: Target floor integer, or None to return all locations.

    Returns:
        List of location dictionaries.
    """
    all_locs = campus_map.get_all_locations()
    if floor is None:
        return all_locs
    return [loc for loc in all_locs if loc.get("floor") == floor]


def get_connections_for_floor(
    campus_map: CampusMap, floor: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Retrieve connections (edges) filtered by floor.

    If floor is specified, only returns intra-floor connections where both
    endpoints reside on that floor. If floor is None, returns all connections
    including inter-floor elevator/stair links.

    Args:
        campus_map: CampusMap instance.
        floor: Optional floor number.

    Returns:
        List of dictionaries with source, destination, and edge attributes.
    """
    graph = campus_map.graph
    connections: List[Dict[str, Any]] = []

    for u, v, data in graph.edges(data=True):
        u_loc = campus_map.get_location(u)
        v_loc = campus_map.get_location(v)
        if not u_loc or not v_loc:
            continue

        u_floor = u_loc.get("floor")
        v_floor = v_loc.get("floor")

        if floor is not None:
            # Intra-floor connection
            if u_floor == floor and v_floor == floor:
                connections.append(
                    {"source": u, "destination": v, "is_cross_floor": False, **data}
                )
        else:
            is_cross = u_floor != v_floor
            connections.append(
                {"source": u, "destination": v, "is_cross_floor": is_cross, **data}
            )

    return connections


def detect_cross_floor_transitions(
    path: List[str], campus_map: CampusMap
) -> List[Dict[str, Any]]:
    """Analyze a planned route sequence to identify vertical floor transitions.

    Args:
        path: List of location IDs representing the route.
        campus_map: CampusMap instance.

    Returns:
        List of dictionaries detailing vertical transitions (elevator, stairs, etc.).
    """
    transitions: List[Dict[str, Any]] = []
    if not path or len(path) < 2:
        return transitions

    graph = campus_map.graph

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        u_loc = campus_map.get_location(u) or {}
        v_loc = campus_map.get_location(v) or {}
        u_floor = u_loc.get("floor", 0)
        v_floor = v_loc.get("floor", 0)

        if u_floor != v_floor:
            edge_data = graph.get_edge_data(u, v) or {}
            has_elevator = bool(edge_data.get("has_elevator", False))
            has_stairs = bool(edge_data.get("has_stairs", False))

            if has_elevator:
                conn_type = "Elevator"
                icon = "🛗"
                guidance = (
                    f"Board the elevator at {u_loc.get('name', u)} (Floor {u_floor}) "
                    f"and exit on Floor {v_floor} at {v_loc.get('name', v)}."
                )
            elif has_stairs:
                conn_type = "Stairway"
                icon = "🪜"
                direction = "up" if v_floor > u_floor else "down"
                guidance = (
                    f"Take the stairs {direction} from {u_loc.get('name', u)} (Floor {u_floor}) "
                    f"to Floor {v_floor} ({v_loc.get('name', v)})."
                )
            else:
                conn_type = "Vertical Connector"
                icon = "↕️"
                guidance = f"Transition between Floor {u_floor} and Floor {v_floor}."

            transitions.append(
                {
                    "step_index": i + 1,
                    "from_id": u,
                    "to_id": v,
                    "from_name": u_loc.get("name", u),
                    "to_name": v_loc.get("name", v),
                    "from_floor": u_floor,
                    "to_floor": v_floor,
                    "connector_type": conn_type,
                    "icon": icon,
                    "wheelchair_accessible": bool(edge_data.get("wheelchair_accessible", False)),
                    "distance": float(edge_data.get("distance", 0.0)),
                    "estimated_time": float(edge_data.get("estimated_time", 0.0)),
                    "guidance": guidance,
                }
            )

    return transitions


def calculate_display_coordinates(
    campus_map: CampusMap, floor_filter: Optional[int] = None
) -> Dict[str, Tuple[float, float]]:
    """Compute schematic (X, Y) rendering coordinates for campus nodes.

    - When viewing a single floor (e.g. 0, 1, or outdoor -1), uses original node layout coordinates.
    - When viewing 'All Floors' on benchmark map, side-by-side plate separation is applied:
      Floor 0 appears on the left plate, and Floor 1 is offset to the right by X + 65.0.
    - When viewing 'All Floors' on JAIN digital twin, horizontal multi-plate separation is applied
      across outdoor grounds and 5 FET levels.
    - Missing coordinates are assigned deterministic fallback layout positions to ensure
      the visualizer never crashes.

    Args:
        campus_map: CampusMap instance.
        floor_filter: Specific floor integer, or None for All Floors side-by-side layout.

    Returns:
        Mapping of location_id to (display_x, display_y).
    """
    coords: Dict[str, Tuple[float, float]] = {}
    fallback_index = 0
    is_jain = len(campus_map.locations) > 20

    for loc in campus_map.get_all_locations():
        loc_id = loc["id"]
        raw_x = loc.get("x")
        raw_y = loc.get("y")
        try:
            floor = int(loc.get("floor", 0))
        except (ValueError, TypeError):
            floor = 0

        # Handle missing coordinates gracefully with fallback grid position
        if raw_x is None or raw_y is None:
            x_val = 10.0 + (fallback_index % 4) * 15.0
            y_val = 10.0 + (fallback_index // 4) * 15.0
            fallback_index += 1
        else:
            try:
                x_val = float(raw_x)
                y_val = float(raw_y)
            except (ValueError, TypeError):
                x_val = 10.0 + (fallback_index % 4) * 15.0
                y_val = 10.0 + (fallback_index // 4) * 15.0
                fallback_index += 1

        # Multi-floor side-by-side offset
        if is_jain:
            if floor_filter is None:
                offset_map = {-1: 0.0, 0: 210.0, 1: 330.0, 2: 450.0, 3: 570.0, 4: 690.0}
                display_x = x_val + offset_map.get(floor, 0.0)
            else:
                display_x = x_val
        else:
            if floor_filter is None and floor == 1:
                display_x = x_val + 65.0
            else:
                display_x = x_val

        display_y = y_val
        coords[loc_id] = (display_x, display_y)

    return coords


def create_indoor_map_figure(
    campus_map: CampusMap,
    floor_filter: Optional[int] = None,
    highlight_route: Optional[List[str]] = None,
    selected_location_id: Optional[str] = None,
) -> go.Figure:
    """Construct an interactive Plotly figure representing the schematic indoor campus map.

    Color Coding:
    - Green (#2d6a4f): Accessible open pathways and ramps.
    - Teal (#2a9d8f): Elevator vertical connections.
    - Orange (#e76f51): Staircase connections.
    - Red (#e63946): Verified blocked pathways (dynamically synchronized).
    - Grey (#6c757d): Unknown or unverified accessibility.
    - Glowing Gold/Amber (#f59e0b): Active highlighted navigation route.

    Args:
        campus_map: CampusMap instance with live graph.
        floor_filter: None for All Floors (side-by-side), or 0 / 1 for isolated floor.
        highlight_route: Optional list of location IDs along calculated route.
        selected_location_id: Optional location ID to highlight on map.

    Returns:
        Configured Plotly Figure.
    """
    graph = campus_map.graph
    coords = calculate_display_coordinates(campus_map, floor_filter)

    # Determine node IDs to include in visual
    if floor_filter is not None:
        visible_nodes = {
            loc["id"]
            for loc in campus_map.get_all_locations()
            if loc.get("floor") == floor_filter
        }
    else:
        visible_nodes = set(campus_map.locations.keys())

    fig = go.Figure()

    # Route edge set for fast lookup
    route_edges: Set[Tuple[str, str]] = set()
    if highlight_route and len(highlight_route) > 1:
        for i in range(len(highlight_route) - 1):
            u, v = highlight_route[i], highlight_route[i + 1]
            route_edges.add((u, v))
            route_edges.add((v, u))

    # --- 1. RENDER BASE CONNECTIVITY EDGES ---
    for u, v, data in graph.edges(data=True):
        if u not in visible_nodes or v not in visible_nodes:
            continue
        if u not in coords or v not in coords:
            continue

        x0, y0 = coords[u]
        x1, y1 = coords[v]

        status = str(data.get("status", "open")).lower()
        is_acc = data.get("wheelchair_accessible", True)
        has_stairs = bool(data.get("has_stairs", False))
        has_elevator = bool(data.get("has_elevator", False))
        has_ramp = bool(data.get("has_ramp", False))

        # Determine line styling and color based on accessibility
        if status in ("blocked", "closed", "maintenance", "under_maintenance"):
            line_color = "#F87171"  # Error Red
            line_dash = "dash"
            line_width = 3.5
            edge_desc = "⛔ Blocked Pathway"
        elif has_elevator:
            line_color = "#60A5FA"  # Info Blue/Teal
            line_dash = "solid"
            line_width = 4.0
            edge_desc = "🛗 Elevator Connection"
        elif has_stairs and not is_acc:
            line_color = "#F5B942"  # Warning Amber/Orange
            line_dash = "dot"
            line_width = 3.0
            edge_desc = "🪜 Staircase (Inaccessible)"
        elif has_ramp:
            line_color = "#35D99A"  # Accent Green
            line_dash = "solid"
            line_width = 3.5
            edge_desc = "♿ Accessible Ramp"
        elif is_acc:
            line_color = "#16A36A"  # Primary Green
            line_dash = "solid"
            line_width = 3.0
            edge_desc = "🟢 Accessible Corridor"
        else:
            line_color = "#9CAFA5"  # Secondary Text Grey
            line_dash = "dashdot"
            line_width = 2.5
            edge_desc = "⚪ Unknown Accessibility"

        # Dim base edge if a route is actively highlighted
        if highlight_route and (u, v) not in route_edges:
            line_opacity = 0.35
        else:
            line_opacity = 0.95

        u_name = campus_map.get_location(u)["name"]
        v_name = campus_map.get_location(v)["name"]
        hover_text = (
            f"<b>{edge_desc}</b><br>[{u}] {u_name} ↔ [{v}] {v_name}<br>"
            f"Traversable Distance: {data.get('distance', 0)} m<br>"
            f"Status: {status.capitalize()}"
        )

        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(color=line_color, width=line_width, dash=line_dash),
                opacity=line_opacity,
                hoverinfo="text",
                hovertext=hover_text,
                showlegend=False,
            )
        )

    # --- 2. RENDER HIGHLIGHTED ROUTE TRACE OVERLAY ---
    if highlight_route and len(highlight_route) > 1:
        route_xs: List[float] = []
        route_ys: List[float] = []
        for nid in highlight_route:
            if nid in coords and (floor_filter is None or nid in visible_nodes):
                x_val, y_val = coords[nid]
                route_xs.append(x_val)
                route_ys.append(y_val)

        if len(route_xs) > 1:
            fig.add_trace(
                go.Scatter(
                    x=route_xs,
                    y=route_ys,
                    mode="lines",
                    line=dict(color="#f59e0b", width=7.0),
                    opacity=0.95,
                    name="Active Navigation Route",
                    hoverinfo="skip",
                )
            )

    # --- 3. RENDER CAMPUS LOCATION NODES ---
    category_colors = {
        "entrance": "#10B981",
        "gate": "#059669",
        "lobby": "#16A36A",
        "elevator": "#38BDF8",
        "stairs": "#F59E0B",
        "restroom": "#818CF8",
        "classroom": "#60A5FA",
        "auditorium": "#A855F7",
        "cafeteria": "#FB923C",
        "lab": "#35D99A",
        "library": "#0EA5E9",
        "office": "#64748B",
        "sports": "#EAB308",
        "admin": "#14B8A6",
        "ramp": "#34D399",
        "parking": "#6366F1",
    }

    category_icons = {
        "entrance": "🚪",
        "gate": "⛩️",
        "lobby": "🏛️",
        "elevator": "🛗",
        "stairs": "🪜",
        "restroom": "🚻",
        "classroom": "🏫",
        "auditorium": "🎭",
        "cafeteria": "🥪",
        "lab": "🔬",
        "library": "📚",
        "office": "💼",
        "sports": "⚽",
        "admin": "🏛️",
        "ramp": "♿",
        "parking": "🅿️",
    }

    # Group locations by category for clean Plotly legend
    categorized_nodes: Dict[str, List[Dict[str, Any]]] = {}
    for loc in campus_map.get_all_locations():
        if loc["id"] in visible_nodes and loc["id"] in coords:
            cat = loc.get("category", "other").lower()
            categorized_nodes.setdefault(cat, []).append(loc)

    for cat, loc_list in categorized_nodes.items():
        cat_xs = [coords[loc["id"]][0] for loc in loc_list]
        cat_ys = [coords[loc["id"]][1] for loc in loc_list]
        cat_color = category_colors.get(cat, "#4a5568")
        icon = category_icons.get(cat, "📍")

        hover_texts = []
        for loc in loc_list:
            fl_val = loc.get("floor", 0)
            fl_text = "Outdoor Grounds" if fl_val == -1 else f"Floor {fl_val}"
            acc_str = "✅ Step-Free Accessible" if loc.get("wheelchair_accessible", True) else "⚠️ Stair Access"
            ht = (
                f"<b>[{loc['id']}] {loc['name']}</b><br>"
                f"Building: {loc.get('building', 'Academic Complex')}<br>"
                f"Level: {fl_text} · Category: {cat.capitalize()}<br>"
                f"Accessibility: {acc_str}<br>"
                f"Coordinates: ({loc.get('x')}, {loc.get('y')})"
            )
            hover_texts.append(ht)

        fig.add_trace(
            go.Scatter(
                x=cat_xs,
                y=cat_ys,
                mode="markers+text",
                marker=dict(
                    size=16,
                    color=cat_color,
                    line=dict(width=2, color="#07130F"),
                ),
                text=[f"{icon} {loc['id']}" for loc in loc_list],
                textposition="top center",
                textfont=dict(size=9.5, color="#F8FAFC", family="Arial, sans-serif"),
                name=cat.capitalize(),
                hoverinfo="text",
                hovertext=hover_texts,
            )
        )

    # --- 4. RENDER SPECIAL START / DESTINATION / SELECTION MARKERS ---
    if highlight_route:
        # Start marker (Green pin halo)
        start_id = highlight_route[0]
        if start_id in coords and start_id in visible_nodes:
            sx, sy = coords[start_id]
            fig.add_trace(
                go.Scatter(
                    x=[sx],
                    y=[sy],
                    mode="markers+text",
                    marker=dict(
                        size=24,
                        color="#16A36A",
                        symbol="circle",
                        line=dict(width=3, color="#35D99A"),
                    ),
                    text=["🟢 Origin"],
                    textposition="bottom center",
                    textfont=dict(size=11, color="#35D99A"),
                    name="Route Origin",
                    hoverinfo="text",
                    hovertext=f"<b>Route Starting Point:</b> {campus_map.get_location(start_id)['name']}",
                )
            )

        # Destination marker (Checkered/Red flag halo)
        dest_id = highlight_route[-1]
        if dest_id in coords and dest_id in visible_nodes:
            dx, dy = coords[dest_id]
            fig.add_trace(
                go.Scatter(
                    x=[dx],
                    y=[dy],
                    mode="markers+text",
                    marker=dict(
                        size=24,
                        color="#F87171",
                        symbol="star",
                        line=dict(width=3, color="#FFFFFF"),
                    ),
                    text=["🏁 Destination"],
                    textposition="bottom center",
                    textfont=dict(size=11, color="#F87171"),
                    name="Route Destination",
                    hoverinfo="text",
                    hovertext=f"<b>Route Destination:</b> {campus_map.get_location(dest_id)['name']}",
                )
            )

    # Selected location marker (Halo circle)
    if selected_location_id and selected_location_id in coords:
        if floor_filter is None or selected_location_id in visible_nodes:
            px, py = coords[selected_location_id]
            sel_loc = campus_map.get_location(selected_location_id)
            sel_name = sel_loc["name"] if sel_loc else selected_location_id
            fig.add_trace(
                go.Scatter(
                    x=[px],
                    y=[py],
                    mode="markers",
                    marker=dict(
                        size=28,
                        color="rgba(53, 217, 154, 0.25)",
                        symbol="circle",
                        line=dict(width=3, color="#35D99A"),
                    ),
                    name="Selected Location",
                    hoverinfo="text",
                    hovertext=f"<b>Selected Inspector Target:</b> {sel_name}",
                )
            )

    # --- 5. RENDER ARCHITECTURAL FLOOR BOUNDARIES & ZONES ---
    annotations = []
    shapes = []
    is_jain = len(campus_map.locations) > 20

    if is_jain:
        if floor_filter in (0, 1, 2, 3, 4):
            # FET 5-Floor Architectural Floor Plan
            floor_names = {
                0: "Ground Floor (Level 0) - Foundation Labs & Foyer",
                1: "First Floor (Level 1) - Computing & Electronics",
                2: "Second Floor (Level 2) - Software & Department Classrooms",
                3: "Third Floor (Level 3) - Core Sciences & Design Studios",
                4: "Fourth Floor (Level 4) - Executive Dean & High-Performance Computing",
            }
            # Central Atrium & Rotunda circle
            shapes.append(
                dict(
                    type="circle",
                    x0=-15,
                    y0=-15,
                    x1=15,
                    y1=15,
                    line=dict(color="rgba(53, 217, 154, 0.45)", width=2),
                    fillcolor="rgba(18, 40, 32, 0.6)",
                    layer="below",
                )
            )
            # South Entrance & Elevator Foyer
            shapes.append(
                dict(
                    type="rect",
                    x0=-18,
                    y0=12,
                    x1=18,
                    y1=28,
                    line=dict(color="rgba(53, 217, 154, 0.35)", width=1.5),
                    fillcolor="rgba(22, 163, 106, 0.12)",
                    layer="below",
                )
            )
            # West Academic Wing
            shapes.append(
                dict(
                    type="rect",
                    x0=-38,
                    y0=-18,
                    x1=-16,
                    y1=18,
                    line=dict(color="rgba(96, 165, 250, 0.35)", width=1.5),
                    fillcolor="rgba(13, 31, 24, 0.5)",
                    layer="below",
                )
            )
            # East Academic Wing
            shapes.append(
                dict(
                    type="rect",
                    x0=16,
                    y0=-18,
                    x1=38,
                    y1=18,
                    line=dict(color="rgba(96, 165, 250, 0.35)", width=1.5),
                    fillcolor="rgba(13, 31, 24, 0.5)",
                    layer="below",
                )
            )
            # North Wing
            shapes.append(
                dict(
                    type="rect",
                    x0=-16,
                    y0=-34,
                    x1=16,
                    y1=-16,
                    line=dict(color="rgba(96, 165, 250, 0.35)", width=1.5),
                    fillcolor="rgba(13, 31, 24, 0.5)",
                    layer="below",
                )
            )

            annotations.append(
                dict(
                    x=0,
                    y=33,
                    text=f"<b>🏛️ FET Complex: {floor_names.get(floor_filter, '')}</b>",
                    font=dict(size=13, color="#35D99A"),
                    showarrow=False,
                )
            )
            annotations.append(
                dict(
                    x=0,
                    y=0,
                    text="<b>Central Atrium & Rotunda</b>",
                    font=dict(size=10.5, color="rgba(167, 243, 208, 0.7)"),
                    showarrow=False,
                )
            )
            annotations.append(
                dict(
                    x=-27,
                    y=0,
                    text="<b>West Wing</b>",
                    font=dict(size=10, color="rgba(156, 175, 165, 0.8)"),
                    showarrow=False,
                )
            )
            annotations.append(
                dict(
                    x=27,
                    y=0,
                    text="<b>East Wing</b>",
                    font=dict(size=10, color="rgba(156, 175, 165, 0.8)"),
                    showarrow=False,
                )
            )
            annotations.append(
                dict(
                    x=0,
                    y=-25,
                    text="<b>North Wing & Seminar</b>",
                    font=dict(size=10, color="rgba(156, 175, 165, 0.8)"),
                    showarrow=False,
                )
            )
            annotations.append(
                dict(
                    x=0,
                    y=20,
                    text="<b>South Entrance & Elevators</b>",
                    font=dict(size=10, color="rgba(156, 175, 165, 0.8)"),
                    showarrow=False,
                )
            )

            x_range = [-46, 46]
            y_range = [-40, 38]

        elif floor_filter == -1:
            # JAIN Outdoor Campus Grounds
            # Stadium & Sports Complex
            shapes.append(
                dict(
                    type="rect",
                    x0=-35,
                    y0=-120,
                    x1=115,
                    y1=-55,
                    line=dict(color="rgba(234, 179, 8, 0.35)", width=1.5, dash="dot"),
                    fillcolor="rgba(18, 40, 32, 0.45)",
                    layer="below",
                )
            )
            # Central Quad & Admin Plaza
            shapes.append(
                dict(
                    type="rect",
                    x0=15,
                    y0=45,
                    x1=55,
                    y1=80,
                    line=dict(color="rgba(53, 217, 154, 0.35)", width=1.5),
                    fillcolor="rgba(22, 163, 106, 0.12)",
                    layer="below",
                )
            )
            # FET Building Footprint
            shapes.append(
                dict(
                    type="rect",
                    x0=-30,
                    y0=-18,
                    x1=30,
                    y1=28,
                    line=dict(color="rgba(96, 165, 250, 0.4)", width=2),
                    fillcolor="rgba(13, 31, 24, 0.65)",
                    layer="below",
                )
            )

            annotations.append(
                dict(
                    x=35,
                    y=155,
                    text="<b>🌳 JAIN Global Campus - Outdoor Grounds & Pathways</b>",
                    font=dict(size=13, color="#35D99A"),
                    showarrow=False,
                )
            )
            annotations.append(
                dict(
                    x=40,
                    y=-88,
                    text="<b>⚽ International Sports Arena & Cricket Grounds</b>",
                    font=dict(size=11, color="#F5B942"),
                    showarrow=False,
                )
            )
            annotations.append(
                dict(
                    x=0,
                    y=5,
                    text="<b>🏢 FET Academic Complex</b>",
                    font=dict(size=11, color="#60A5FA"),
                    showarrow=False,
                )
            )
            annotations.append(
                dict(
                    x=35,
                    y=62,
                    text="<b>🏛️ Central Quadrangle & Administration</b>",
                    font=dict(size=10.5, color="#A7F3D0"),
                    showarrow=False,
                )
            )

            x_range = [-80, 125]
            y_range = [-130, 165]

        else:
            # JAIN All Floors & Outdoor Combined Overview
            plates = [
                (-1, "Outdoor Grounds", -75, 120, "#35D99A"),
                (0, "Ground Floor", 175, 245, "#10B981"),
                (1, "1st Floor", 295, 365, "#38BDF8"),
                (2, "2nd Floor", 415, 485, "#60A5FA"),
                (3, "3rd Floor", 535, 605, "#818CF8"),
                (4, "4th Floor (HPC)", 655, 725, "#A855F7"),
            ]
            for fl, name, px0, px1, col in plates:
                shapes.append(
                    dict(
                        type="rect",
                        x0=px0,
                        y0=-125 if fl == -1 else -38,
                        x1=px1,
                        y1=150 if fl == -1 else 35,
                        line=dict(color=f"{col}55", width=1.5, dash="dot"),
                        fillcolor="rgba(13, 31, 24, 0.45)",
                        layer="below",
                    )
                )
                annotations.append(
                    dict(
                        x=(px0 + px1) / 2,
                        y=156 if fl == -1 else 42,
                        text=f"<b>{name}</b>",
                        font=dict(size=11, color=col),
                        showarrow=False,
                    )
                )

            x_range = [-85, 740]
            y_range = [-135, 168]

    else:
        # Benchmark 15-Node Topological Reference Map
        if floor_filter is None:
            # Ground Floor Plate Boundary
            shapes.append(
                dict(
                    type="rect",
                    x0=0,
                    y0=5,
                    x1=60,
                    y1=50,
                    line=dict(color="rgba(53, 217, 154, 0.4)", width=1.5, dash="dot"),
                    fillcolor="rgba(18, 40, 32, 0.45)",
                    layer="below",
                )
            )
            annotations.append(
                dict(
                    x=30,
                    y=52,
                    text="<b>Ground Floor (Floor 0) Plate</b>",
                    font=dict(size=13, color="#35D99A"),
                    showarrow=False,
                )
            )

            # First Floor Plate Boundary
            shapes.append(
                dict(
                    type="rect",
                    x0=65,
                    y0=5,
                    x1=125,
                    y1=50,
                    line=dict(color="rgba(96, 165, 250, 0.4)", width=1.5, dash="dot"),
                    fillcolor="rgba(13, 31, 24, 0.45)",
                    layer="below",
                )
            )
            annotations.append(
                dict(
                    x=95,
                    y=52,
                    text="<b>First Floor (Floor 1) Plate</b>",
                    font=dict(size=13, color="#60A5FA"),
                    showarrow=False,
                )
            )

            x_range = [-5, 130]
            y_range = [0, 56]
        else:
            # Isolated single floor view
            floor_name = "Ground Floor (Floor 0)" if floor_filter == 0 else f"Floor {floor_filter}"
            annotations.append(
                dict(
                    x=30,
                    y=48,
                    text=f"<b>{floor_name} - Schematic Indoor Layout</b>",
                    font=dict(size=13, color="#35D99A"),
                    showarrow=False,
                )
            )
            x_range = [0, 60]
            y_range = [5, 52]

    fig.update_layout(
        height=540,
        margin=dict(l=20, r=20, t=35, b=25),
        xaxis=dict(
            title="Schematic X Coordinate",
            range=x_range,
            showgrid=True,
            gridcolor="rgba(53, 217, 154, 0.08)",
            zeroline=False,
            title_font=dict(color="#9CAFA5", size=11),
            tickfont=dict(color="#9CAFA5", size=10),
        ),
        yaxis=dict(
            title="Schematic Y Coordinate",
            range=y_range,
            showgrid=True,
            gridcolor="rgba(53, 217, 154, 0.08)",
            zeroline=False,
            scaleanchor="x",
            title_font=dict(color="#9CAFA5", size=11),
            tickfont=dict(color="#9CAFA5", size=10),
        ),
        shapes=shapes,
        annotations=annotations,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.28,
            xanchor="center",
            x=0.5,
            font=dict(size=10.5, color="#F8FAFC"),
        ),
        plot_bgcolor="#07130F",
        paper_bgcolor="rgba(13, 31, 24, 0.75)",
    )

    return fig
