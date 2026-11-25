"""Campus Map Page - Advanced interactive indoor campus navigation and schematic spatial visualizer.

Provides multi-floor topological layouts, architectural floor plan zoning, floor-by-floor filtering,
cross-floor elevator transitions, live destination search, route highlighting, and real-time obstacle visualization.
Supports both JAIN Global Campus (79 locations) and the Benchmark Model (15 locations).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

from modules.accessibility import AccessibilityEngine
from modules.campus_map import CampusMap
from modules.destination_search import get_search_suggestions, search_destinations
from modules.indoor_map import (
    create_indoor_map_figure,
    detect_cross_floor_transitions,
    get_floors_in_campus,
    get_locations_for_floor,
)
from modules.jain_digital_twin import FLOOR_NAMES, load_jain_campus_map
from modules.route_finder import RouteFinder
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

benchmark_cmap = services["campus_map"]
benchmark_rf = services["route_finder"]
obs_manager = services["obstacle_manager"]

st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">🗺️ Interactive Indoor Campus Map & Cartography</div>
        <div class="hero-subtitle">
            Explore architectural floor plan layouts, inspect room accessibility, track active barrier detours,
            and visualize step-free routes across JAIN Global Campus and the 5-Floor FET Building.
        </div>
        <div class="hero-chip-container">
            <span class="hero-chip">🏛️ JAIN Global Campus 2D Digital Twin</span>
            <span class="hero-chip">🏢 5-Floor Architectural Layouts</span>
            <span class="hero-chip">🛗 Elevator & Stair Connector Tracking</span>
            <span class="hero-chip">♿ Step-Free Wheelchair Routing</span>
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
    </div>
    """,
    unsafe_allow_html=True,
)

# --- CAMPUS ENVIRONMENT SELECTOR & TOOLBAR ---
c_env1, c_env2 = st.columns([2.6, 1.4])
with c_env1:
    campus_model_choice = st.radio(
        "🏛️ Active Campus Environment:",
        options=[
            "JAIN Global Campus & 5-Floor FET Building (79 Locations)",
            "Schematic Benchmark Model (15 Locations)",
        ],
        index=0,
        horizontal=True,
        key="campus_map_env_choice",
    )
is_jain = "JAIN" in campus_model_choice

with c_env2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🏢 Switch to 3D Digital Twin", width="stretch", help="Open the 3D WebGL Digital Twin visualization"):
        st.switch_page("pages/3d_campus_map.py")

# Load appropriate CampusMap, RouteFinder, and AccessibilityEngine from Single Source of Truth
if is_jain:
    cmap = load_jain_campus_map()
    obs_manager.sync_obstacles_to_campus_map(cmap)
    route_finder = RouteFinder(cmap)
else:
    cmap = benchmark_cmap
    route_finder = benchmark_rf
acc_engine = AccessibilityEngine(cmap)

floors = get_floors_in_campus(cmap)
all_locations = sorted(cmap.get_all_locations(), key=lambda x: (int(x.get("floor", 0)), str(x.get("name", ""))))

def format_loc_option(loc: Dict[str, Any]) -> str:
    fl = int(loc.get("floor", 0))
    fl_tag = "Outdoor" if fl == -1 else f"Floor {fl}"
    return f"[{fl_tag}] {loc['name']} ({loc['id']})"

loc_label_to_id = {format_loc_option(loc): loc["id"] for loc in all_locations}
loc_labels = list(loc_label_to_id.keys())

# --- CONTROLS: FLOOR SELECTOR & IN-MAP ROUTE PLANNER ---
ctrl_c1, ctrl_c2 = st.columns([1.1, 2.0], gap="medium")

with ctrl_c1:
    with st.container(border=True):
        st.markdown("##### 🏢 Building Floor Filter")

    if is_jain:
        floor_options = [
            "All Campus & Floors",
            "🌳 Outdoor Grounds (-1)",
            "Level 0 — Ground Floor",
            "Level 1 — First Floor",
            "Level 2 — Second Floor",
            "Level 3 — Third Floor",
            "Level 4 — Fourth Floor (HPC)",
        ]
        selected_floor_str = st.radio(
            "Display Level:",
            options=floor_options,
            index=2,  # Default to Ground Floor Level 0
            key="jain_floor_filter_radio",
            help="Switch between individual FET building floor plans or view outdoor campus grounds.",
        )
        floor_filter: int | None = None
        if "Level 0" in selected_floor_str:
            floor_filter = 0
        elif "Level 1" in selected_floor_str:
            floor_filter = 1
        elif "Level 2" in selected_floor_str:
            floor_filter = 2
        elif "Level 3" in selected_floor_str:
            floor_filter = 3
        elif "Level 4" in selected_floor_str:
            floor_filter = 4
        elif "Outdoor" in selected_floor_str:
            floor_filter = -1
        else:
            floor_filter = None
    else:
        floor_options = ["All Floors (Side-by-Side)"] + [
            f"Ground Floor (Floor 0)" if fl == 0 else f"First Floor (Floor {fl})"
            for fl in floors
        ]
        selected_floor_str = st.radio(
            "Display Level:",
            options=floor_options,
            index=0,
            key="bench_floor_filter_radio",
            help="Switch between individual floor layouts or view both floors side-by-side.",
        )
        floor_filter = None
        if "Floor 0" in selected_floor_str:
            floor_filter = 0
        elif "Floor 1" in selected_floor_str:
            floor_filter = 1

with ctrl_c2:
    with st.container(border=True):
        st.markdown("##### 🧭 2D Route Planning Console")

        # Keyword suggestions pills
        st.markdown("<div style='font-size: 11px; color: #9CAFA5; margin-bottom: 4px;'><b>Quick Destination Suggestions:</b></div>", unsafe_allow_html=True)
        pill_cols = st.columns(4)
        quick_keywords = ["HPC Lab", "Library", "Dean", "Robotics"] if is_jain else ["Classroom", "Lab", "Restroom", "Elevator"]
        for i, kw in enumerate(quick_keywords):
            with pill_cols[i]:
                if st.button(kw, key=f"map_pill_{kw}", width="stretch"):
                    st.session_state["map_dest_search_query"] = kw
                    st.rerun()

        if "map_dest_search_query" not in st.session_state:
            st.session_state["map_dest_search_query"] = ""

        # Destination Search with Keyword Intelligence
        dest_search_query = st.text_input(
            "🔍 Search Destination (Lab, Room, Department, Keyword):",
            placeholder="e.g. AI Lab, HPC, Library, Dean, Robotics, Seminar, Sports...",
            key="map_dest_search_query",
        )

        matched_dest_id = None
        if dest_search_query.strip() and is_jain:
            search_matches = search_destinations(dest_search_query, cmap, limit=10)
            if search_matches:
                st.caption(f"✨ Found {len(search_matches)} match(es) for '{dest_search_query}'")
                search_options = {
                    f"[{'Outdoor' if m.floor == -1 else f'Floor {m.floor}'}] {m.name} ({m.location_id})": m.location_id
                    for m in search_matches
                }
                sel_match_label = st.selectbox(
                    "Select Matched Facility:",
                    options=list(search_options.keys()),
                    index=0,
                    key="map_matched_dest_select",
                )
                matched_dest_id = search_options[sel_match_label]
            else:
                st.caption("ℹ️ No exact keyword matches found.")

        rc1, rc2 = st.columns(2)
        with rc1:
            default_start_idx = 0
            if is_jain:
                for idx, label in enumerate(loc_labels):
                    if "OUT_GATE_MAIN" in label:
                        default_start_idx = idx
                        break
            start_sel = st.selectbox(
                "Origin Location:",
                options=loc_labels,
                index=default_start_idx if default_start_idx < len(loc_labels) else 0,
                key="map_start_loc",
            )
            map_source = loc_label_to_id[start_sel]

        with rc2:
            if matched_dest_id:
                map_dest = matched_dest_id
                st.markdown(f"<div style='font-size: 12px; color: #35D99A; margin-top: 28px;'><b>Selected Target:</b> {matched_dest_id}</div>", unsafe_allow_html=True)
            else:
                default_dest_idx = min(len(loc_labels) - 1, 13)
                if is_jain:
                    for idx, label in enumerate(loc_labels):
                        if "FET_4F_HPC_CLUSTER" in label:
                            default_dest_idx = idx
                            break
                dest_sel = st.selectbox(
                    "Destination Location:",
                    options=loc_labels,
                    index=default_dest_idx,
                    key="map_dest_loc",
                )
                map_dest = loc_label_to_id[dest_sel]

        ro1, ro2, ro3 = st.columns([1.2, 1.2, 1.0])
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
            st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
            map_wheelchair = st.checkbox(
                "♿ Wheelchair",
                value=True,
                key="map_wheelchair_check",
                help="Prohibits staircases, enforcing step-free routing through elevators and access ramps.",
            )

        calc_route_click = st.button("🚀 Find & Visualize Route", type="primary", width="stretch")

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

    start_node = cmap.get_location(active_route.path[0]) or {}
    dest_node = cmap.get_location(active_route.path[-1]) or {}
    st.markdown("---")
    st.markdown(f"#### 🚀 Active Route Overlay: **{start_node.get('name', active_route.path[0])}** ➔ **{dest_node.get('name', active_route.path[-1])}**")

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

# --- INTERACTIVE MAP DISPLAY & FACILITY INSPECTOR ---
map_col, inspect_col = st.columns([3.0, 1.8], gap="medium")

with inspect_col:
    st.markdown("### 📍 Location Inspector Panel")
    selected_loc_label = st.selectbox(
        "Select Location to Inspect:",
        options=loc_labels,
        index=0,
        key="inspect_loc_selector",
    )
    inspected_loc_id = loc_label_to_id[selected_loc_label]
    loc_data = cmap.get_location(inspected_loc_id) or {}
    loc_acc = acc_engine.check_location_accessibility(inspected_loc_id)

    # Check for active obstacles affecting this location
    loc_reports = obs_manager.get_reports_by_location(inspected_loc_id)
    active_loc_obstacles = [r for r in loc_reports if r.get("status") == "Verified"]

    floor_num = int(loc_data.get("floor", 0))
    floor_display = "Outdoor Grounds" if floor_num == -1 else f"Floor {floor_num} ({FLOOR_NAMES.get(floor_num, '')})"
    verif_status = loc_data.get("verification_status", "VERIFIED" if not is_jain else "IMAGE_DERIVED")

    badge_colors = {
        "VERIFIED": ("#10B981", "rgba(16, 185, 129, 0.18)"),
        "IMAGE_DERIVED": ("#38BDF8", "rgba(56, 189, 248, 0.18)"),
        "APPROXIMATE": ("#F5B942", "rgba(245, 185, 66, 0.18)"),
        "UNVERIFIED": ("#94A3B8", "rgba(148, 163, 184, 0.18)"),
    }
    badge_fg, badge_bg = badge_colors.get(verif_status, ("#94A3B8", "rgba(148, 163, 184, 0.18)"))

    st.markdown(
        f"""
        <div class="ui-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div style="font-weight: 800; color: #F8FAFC; font-size: 1.15rem;">{loc_data.get('name')}</div>
                    <div style="color: #9CAFA5; font-size: 0.82rem; margin-top: 3px;">
                        <b>ID:</b> <code>{loc_data.get('id')}</code> · <b>Building:</b> {loc_data.get('building', 'FET Complex')}
                    </div>
                </div>
                <span style="background: {badge_bg}; color: {badge_fg}; border: 1px solid {badge_fg}; padding: 2px 7px; border-radius: 4px; font-size: 9.5px; font-weight: 800;">
                    {verif_status}
                </span>
            </div>
            <div style="color: #9CAFA5; font-size: 0.85rem; margin-top: 4px;">
                <b>Level:</b> {floor_display} · <b>Category:</b> {str(loc_data.get('category', 'office')).capitalize()}
            </div>
            <hr style="margin: 8px 0; border-color: rgba(53, 217, 154, 0.15);">
            <div style="font-size: 0.85rem; line-height: 1.7;">
                <span style="color: #9CAFA5;">Classification:</span> <b style="color: #35D99A;">{loc_acc.display_classification or loc_acc.classification}</b><br>
                <span style="color: #9CAFA5;">Accessibility Score:</span> <b style="color: #F8FAFC;">{loc_acc.score} / 100</b><br>
                <span style="color: #9CAFA5;">Connected Pathways:</span> <b style="color: #F8FAFC;">{loc_acc.accessible_connections} Accessible / {loc_acc.total_connections} Total</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1-Click Action Buttons
    c_act1, c_act2 = st.columns(2)
    with c_act1:
        if st.button("🚩 Set as Start", key="map_btn_inspect_start", width="stretch"):
            st.session_state["map_start_loc"] = selected_loc_label
            st.rerun()
    with c_act2:
        if st.button("🎯 Set as Dest", key="map_btn_inspect_dest", width="stretch"):
            st.session_state["map_dest_loc"] = selected_loc_label
            if "map_dest_search_query" in st.session_state:
                st.session_state["map_dest_search_query"] = ""
            st.rerun()

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
            status_tag = "🔴 Blocked" if str(attrs.get("status", "open")).lower() in ("blocked", "closed", "maintenance", "under_maintenance") else "🟢 Open"
            wa_val = attrs.get("wheelchair_accessible")
            if attrs.get("has_elevator"):
                acc_tag = "🛗 Elevator"
            elif attrs.get("has_stairs") and wa_val is not True:
                acc_tag = "🪜 Stairs"
            elif wa_val is True:
                acc_tag = "♿ Accessible"
            elif wa_val is False:
                acc_tag = "🔴 Inaccessible"
            else:
                acc_tag = "⚪ Unknown"
            st.markdown(
                f"- **{target.get('name')}** [`{cp['to_location_id']}`]: {attrs.get('distance')}m · {status_tag} · {acc_tag}"
            )

with map_col:
    st.markdown("### 🗺️ Schematic Architectural Floor Plan")
    mc1, mc2, mc3 = st.columns([1.4, 1.3, 1.0])
    with mc1:
        acc_filter_choice = st.selectbox(
            "Pathway Layer Filter:",
            options=["All Pathways", "Wheelchair Step-Free Only", "Highlight Stairs & Barriers"],
            index=0,
            key="map_acc_layer_filter",
        )
    with mc2:
        label_mode_choice = st.selectbox(
            "Marker Label Mode:",
            options=["Auto (Clean Landmarks)", "Show All Facility Labels"],
            index=0,
            key="map_label_density_mode",
        )
    with mc3:
        st.markdown("<div style='height: 26px;'></div>", unsafe_allow_html=True)
        st.caption("🖱️ Drag to Pan · Scroll to Zoom · Double-Click to Reset")

    acc_mode_key = (
        "wheelchair_only"
        if "Wheelchair" in acc_filter_choice
        else ("barriers_highlight" if "Barriers" in acc_filter_choice else "all")
    )
    show_all_lbl = "Show All" in label_mode_choice

    fig_map = create_indoor_map_figure(
        campus_map=cmap,
        floor_filter=floor_filter,
        highlight_route=highlight_path,
        selected_location_id=inspected_loc_id,
        show_all_labels=True if (show_all_lbl or floor_filter is not None) else False,
        accessibility_mode=acc_mode_key,
    )
    st.plotly_chart(fig_map, width="stretch", config={"scrollZoom": True, "displayModeBar": True})

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
            <div class="ui-card-title">Waypoint Markers & Symbols</div>
            <div style="font-size: 0.85rem; line-height: 1.8; color: #F8FAFC;">
                🟢 <b>Origin Pin:</b> Selected navigation starting point<br>
                🏁 <b>Destination Flag:</b> Selected navigation target destination<br>
                🟣 <b>Halo Circle:</b> Current location inspected in details panel<br>
                🚪 <b>Entrances & Foyers</b> · 🛗 <b>Elevator Banks</b> · 🪜 <b>Stairwells</b><br>
                🔬 <b>Research Laboratories</b> · 📚 <b>Libraries</b> · 🚻 <b>Accessible Restrooms</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
