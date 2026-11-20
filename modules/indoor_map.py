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

    - When viewing a single floor (e.g. 0 or 1), uses original node layout coordinates.
    - When viewing 'All Floors', side-by-side plate separation is applied:
      Floor 0 appears on the left plate, and Floor 1 is offset to the right by X + 65.0.
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

    for loc in campus_map.get_all_locations():
        loc_id = loc["id"]
        raw_x = loc.get("x")
        raw_y = loc.get("y")
        floor = loc.get("floor", 0)

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

        # Multi-floor side-by-side offset: Floor 1 is offset horizontally by 65 units
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
        "entrance": "#1b4332",
        "lobby": "#2d6a4f",
        "elevator": "#2a9d8f",
        "stairs": "#e76f51",
        "restroom": "#457b9d",
        "classroom": "#3a86ff",
        "auditorium": "#8338ec",
        "cafeteria": "#f4a261",
        "lab": "#06d6a0",
        "library": "#118ab2",
        "office": "#073b4c",
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

        hover_texts = []
        for loc in loc_list:
            fl_text = f"Floor {loc.get('floor', 0)}"
            ht = (
                f"<b>[{loc['id']}] {loc['name']}</b><br>"
                f"Building: {loc.get('building', 'Academic Complex')}<br>"
                f"Level: {fl_text} · Category: {cat.capitalize()}<br>"
                f"Schematic Layout Pos: ({loc.get('x')}, {loc.get('y')})"
            )
            hover_texts.append(ht)

        fig.add_trace(
            go.Scatter(
                x=cat_xs,
                y=cat_ys,
                mode="markers+text",
                marker=dict(
                    size=15,
                    color=cat_color,
                    line=dict(width=2, color="#07130F"),
                ),
                text=[loc["id"] for loc in loc_list],
                textposition="top center",
                textfont=dict(size=10, color="#F8FAFC"),
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

    # --- 5. RENDER FLOOR BOUNDARIES & HEADERS FOR ALL-FLOORS VIEW ---
    annotations = []
    shapes = []

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
        height=520,
        margin=dict(l=20, r=20, t=35, b=25),
        xaxis=dict(
            title="Schematic X Position",
            range=x_range,
            showgrid=True,
            gridcolor="rgba(53, 217, 154, 0.08)",
            zeroline=False,
            title_font=dict(color="#9CAFA5", size=11),
            tickfont=dict(color="#9CAFA5", size=10),
        ),
        yaxis=dict(
            title="Schematic Y Position",
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
            font=dict(size=11, color="#F8FAFC"),
        ),
        plot_bgcolor="#07130F",
        paper_bgcolor="rgba(13, 31, 24, 0.75)",
    )

    return fig
