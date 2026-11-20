"""Campus Map Page - Advanced interactive indoor campus navigation and schematic spatial visualizer."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.indoor_map import (
    create_indoor_map_figure,
    detect_cross_floor_transitions,
    get_floors_in_campus,
    get_locations_for_floor,
)
from modules.ui_theme import (
    ACCENT_GREEN,
    ERROR,
    INFO,
    PRIMARY_GREEN,
    SECONDARY_TEXT,
    WARNING,
    WHITE,
    apply_custom_theme,
    get_app_services,
)

apply_custom_theme()
services = get_app_services()

cmap = services["campus_map"]
route_finder = services["route_finder"]
acc_engine = services["accessibility_engine"]
obs_manager = services["obstacle_manager"]

st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">🗺️ Interactive Indoor Campus Map & Cartography</div>
        <div class="hero-subtitle">
            Explore multi-floor topological layouts, inspect room accessibility, track active barrier detours,
            and visualize step-free routes between academic facilities.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Mandatory Architectural Disclaimer
st.markdown(
    """
    <div class="disclaimer-banner">
        <b>📐 Schematic Connectivity Layout Notice:</b> The node positions and 2D layouts rendered below
        are <b>illustrative graph-layout coordinates</b> designed for schematic pathfinding and connectivity visualization.
        They are <b>not geographically surveyed coordinates</b> and do not represent architectural CAD blueprints or surveyed physical dimensions.
        Verified architectural floor plans will be integrated as spatial overlays in future updates.
    </div>
    """,
    unsafe_allow_html=True,
)

# Get all unique floors and locations
floors = get_floors_in_campus(cmap)
all_locations = sorted(cmap.get_all_locations(), key=lambda x: (x.get("floor", 0), x.get("name", "")))
loc_label_to_id = {
    f"[{loc['id']}] {loc['name']} (Floor {loc['floor']})": loc["id"]
    for loc in all_locations
}

# --- CONTROLS: FLOOR SELECTOR & IN-MAP ROUTE PLANNER ---
ctrl_c1, ctrl_c2 = st.columns([1, 2])

with ctrl_c1:
    st.markdown('<div class="ui-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown("##### 🏢 Floor Level Filter")
    floor_options = ["All Floors (Side-by-Side)"] + [
        f"Ground Floor (Floor 0)" if fl == 0 else f"First Floor (Floor {fl})"
        for fl in floors
    ]
    selected_floor_str = st.radio(
        "Display Level:",
        options=floor_options,
        index=0,
        help="Switch between individual floor layouts or view both floors side-by-side.",
    )

    floor_filter: int | None = None
    if "Floor 0" in selected_floor_str:
        floor_filter = 0
    elif "Floor 1" in selected_floor_str:
        floor_filter = 1

    st.markdown("</div>", unsafe_allow_html=True)

with ctrl_c2:
    with st.expander("🧭 In-Map Route Planning Controls", expanded=True):
        rc1, rc2 = st.columns(2)
        with rc1:
            start_sel = st.selectbox(
                "Origin Location:",
                options=list(loc_label_to_id.keys()),
                index=0,  # LOC_01
                key="map_start_loc",
            )
            map_source = loc_label_to_id[start_sel]

        with rc2:
            dest_default_idx = min(len(loc_label_to_id) - 1, 13)  # LOC_14
            dest_sel = st.selectbox(
                "Destination:",
                options=list(loc_label_to_id.keys()),
                index=dest_default_idx,
                key="map_dest_loc",
            )
            map_dest = loc_label_to_id[dest_sel]

        ro1, ro2, ro3 = st.columns([1, 1, 1])
        with ro1:
            map_algo = st.selectbox(
                "Algorithm:",
                options=["Dijkstra's Algorithm", "Breadth-First Search (BFS)"],
                index=0,
                key="map_algo_choice",
            )
        with ro2:
            map_opt = st.selectbox(
                "Optimization:",
                options=["Shortest Distance", "Fastest Time"],
                index=0,
                disabled=("BFS" in map_algo),
                key="map_opt_choice",
            )
        with ro3:
            map_wheelchair = st.checkbox(
                "♿ Wheelchair Only",
                value=True,
                key="map_wheelchair_check",
                help="Prohibits staircases, enforcing step-free routing through elevators and access ramps.",
            )

        calc_route_click = st.button("🗺️ Visualize Route on Map", type="primary", use_container_width=True)

# Maintain route in session state so floor switching doesn't wipe active calculated route
if "active_map_route" not in st.session_state:
    st.session_state.active_map_route = None

if calc_route_click:
    if map_source == map_dest:
        st.warning("⚠️ Origin and destination locations are identical.")
        st.session_state.active_map_route = None
    else:
        algo_k = "dijkstra" if "Dijkstra" in map_algo else "bfs"
        opt_k = "time" if "Time" in map_opt else "distance"
        calc_res = route_finder.find_route(
            source=map_source,
            destination=map_dest,
            algorithm=algo_k,
            optimize_for=opt_k,
            wheelchair_accessible=map_wheelchair,
        )
        if calc_res.success:
            st.session_state.active_map_route = calc_res
            st.session_state.active_map_route_algo = map_algo
        else:
            st.error(f"Route calculation failed: {calc_res.error_message}")
            st.session_state.active_map_route = None

active_route: Any = st.session_state.active_map_route
highlight_path: list[str] | None = active_route.path if active_route and active_route.success else None

# --- ROUTE SUMMARY CARD (IF ACTIVE ROUTE EXISTS) ---
if active_route and active_route.success:
    route_acc_eval = acc_engine.evaluate_route_accessibility(active_route)
    transitions = detect_cross_floor_transitions(active_route.path, cmap)

    st.markdown("---")
    st.markdown(f"#### 🚀 Active Route Overlay: **{cmap.get_location(active_route.path[0])['name']}** ➔ **{cmap.get_location(active_route.path[-1])['name']}**")

    rm1, rm2, rm3, rm4, rm5 = st.columns(5)
    with rm1:
        st.metric("Total Distance", f"{active_route.total_distance:.1f} m")
    with rm2:
        m_mins = int(active_route.total_time // 60)
        m_secs = int(active_route.total_time % 60)
        st.metric("Est. Time", f"{m_mins}m {m_secs}s" if m_mins > 0 else f"{m_secs}s")
    with rm3:
        st.metric("Transitions", f"{active_route.edge_count} Hops")
    with rm4:
        st.metric("Classification", route_acc_eval.overall_classification)
    with rm5:
        st.metric("Accessibility Score", f"{route_acc_eval.accessibility_score} / 100")

    # Multi-floor elevator transition alert
    if transitions:
        for trans in transitions:
            st.info(
                f"**{trans['icon']} Multi-Floor Elevator Transfer (Step {trans['step_index']}):** "
                f"{trans['guidance']} (Distance: {trans['distance']} m)"
            )

    if route_acc_eval.warnings:
        for w in route_acc_eval.warnings:
            st.warning(f"⚠️ {w}")

st.markdown("---")

# --- INTERACTIVE MAP DISPLAY ---
map_col, inspect_col = st.columns([3, 2])

with inspect_col:
    st.markdown("### 📍 Location Inspector Panel")
    selected_loc_label = st.selectbox(
        "Select Location to Inspect:",
        options=list(loc_label_to_id.keys()),
        index=0,
        key="inspect_loc_selector",
    )
    inspected_loc_id = loc_label_to_id[selected_loc_label]
    loc_data = cmap.get_location(inspected_loc_id) or {}
    loc_acc = acc_engine.check_location_accessibility(inspected_loc_id)

    # Check for active obstacles affecting this location
    loc_reports = obs_manager.get_reports_by_location(inspected_loc_id)
    active_loc_obstacles = [r for r in loc_reports if r.get("status") == "Verified"]

    st.markdown(
        f"""
        <div class="ui-card">
            <div style="font-weight: 800; color: #F8FAFC; font-size: 1.2rem;">[{loc_data.get('id')}] {loc_data.get('name')}</div>
            <div style="color: #9CAFA5; font-size: 0.85rem; margin-top: 4px;">
                <b>Building:</b> {loc_data.get('building')} · <b>Floor:</b> {loc_data.get('floor')} · <b>Category:</b> {str(loc_data.get('category')).capitalize()}
            </div>
            <hr style="margin: 10px 0; border-color: rgba(53, 217, 154, 0.15);">
            <div style="font-size: 0.88rem; line-height: 1.8;">
                <span style="color: #9CAFA5;">Classification:</span> <b style="color: #35D99A;">{loc_acc.classification}</b><br>
                <span style="color: #9CAFA5;">Accessibility Score:</span> <b style="color: #F8FAFC;">{loc_acc.score} / 100</b><br>
                <span style="color: #9CAFA5;">Connected Pathways:</span> <b style="color: #F8FAFC;">{loc_acc.accessible_connections} Accessible / {loc_acc.total_connections} Total</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Amenities badges
    amenities_list = []
    if loc_acc.has_accessible_restroom:
        amenities_list.append("♿ Accessible Restroom Facility")
    if loc_acc.is_elevator_hub:
        amenities_list.append("🛗 Multi-Floor Elevator Hub")
    if loc_acc.has_ramp_access:
        amenities_list.append("♿ Code-Compliant Access Ramp")

    if amenities_list:
        st.success("Available Amenities:\n- " + "\n- ".join(amenities_list))

    # Obstacle alerts on location
    if active_loc_obstacles:
        st.error(f"⛔ Active Disruption Reported at this Location ({len(active_loc_obstacles)} active):")
        for obs in active_loc_obstacles:
            st.markdown(f"- **{obs['obstacle_category']} ({obs['severity']}):** {obs['description']}")

    # Connected pathways breakdown
    connected_paths = cmap.get_connected_paths(inspected_loc_id)
    with st.expander(f"🔗 Connected Pathways ({len(connected_paths)} Links)"):
        for cp in connected_paths:
            target = cp["target_location"]
            attrs = cp["attributes"]
            status_tag = "🔴 Blocked" if attrs.get("status") in ("blocked", "closed") else "🟢 Open"
            acc_tag = "♿ Accessible" if attrs.get("wheelchair_accessible", True) and not attrs.get("has_stairs") else "🪜 Stairs"
            st.markdown(
                f"- **{target.get('name')}** [`{cp['to_location_id']}`]: {attrs.get('distance')}m · {status_tag} · {acc_tag}"
            )

with map_col:
    st.markdown("### 🗺️ Schematic Floor Plan")
    fig_map = create_indoor_map_figure(
        campus_map=cmap,
        floor_filter=floor_filter,
        highlight_route=highlight_path,
        selected_location_id=inspected_loc_id,
    )
    st.plotly_chart(fig_map, use_container_width=True)

# --- MAP LEGENDS ---
st.markdown("---")
st.markdown("### 📖 Visual Legend & Map Key")

leg_c1, leg_c2 = st.columns(2)

with leg_c1:
    st.markdown(
        """
        <div class="ui-card">
            <div class="ui-card-title">Pathway Indicators</div>
            <div style="font-size: 0.85rem; line-height: 1.8; color: #F8FAFC;">
                🟢 <b style="color: #35D99A;">Solid Green:</b> Fully Accessible / Step-Free corridor or ramp<br>
                🔵 <b style="color: #60A5FA;">Solid Blue:</b> Multi-Floor Elevator vertical connection<br>
                🟠 <b style="color: #F5B942;">Dotted Amber:</b> Staircase connector (Inaccessible for wheelchairs)<br>
                🔴 <b style="color: #F87171;">Dashed Red:</b> Temporarily Blocked / Closed pathway (Active obstacle)<br>
                ⚪ <b style="color: #9CAFA5;">Dash-Dot Grey:</b> Pathway with unverified accessibility<br>
                🟡 <b style="color: #FCD34D;">Glowing Amber Overlay:</b> Active planned navigation route
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with leg_c2:
    st.markdown(
        """
        <div class="ui-card">
            <div class="ui-card-title">Waypoint Markers</div>
            <div style="font-size: 0.85rem; line-height: 1.8; color: #F8FAFC;">
                🟢 <b>Origin Pin:</b> Selected navigation starting point<br>
                🏁 <b>Destination Flag:</b> Selected navigation target destination<br>
                🟣 <b>Purple / Green Halo:</b> Current location inspected in details panel<br>
                🔵 <b>Color-Coded Nodes:</b> Entrances, lobbies, classrooms, labs, offices, and restrooms
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
