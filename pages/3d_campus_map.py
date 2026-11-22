"""3D Campus Map Page - Interactive Three.js multi-floor campus navigation visualizer.

Provides 360-degree interactive camera orbit, exploded multi-floor viewing,
room volume inspection, authoritative Python route planning with 3D spline rendering,
vertical elevator/stair transitions, intelligent multi-route comparison,
and dynamic obstacle synchronization.

Supports:
1. JAIN Global Campus & FET 5-Floor Digital Twin (Ground to Fourth Floor + Outdoor Campus).
2. Schematic Benchmark Model (15-Node Topological Reference).

DISCLAIMER:
All 3D building models and pathway geometries are schematic digital twin representations
designed for graph connectivity visualization, accessibility inspection, and pathfinding
demonstration. They do not represent surveyed architectural CAD blueprints or physical dimensions.
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from modules.campus_map import CampusMap
from modules.jain_digital_twin import (
    FLOOR_NAMES,
    build_jain_digital_twin_payload,
    get_jain_multi_route_comparison,
    load_jain_campus_map,
    render_jain_digital_twin_html,
)
from modules.navigation_instructions import format_floor_name
from modules.navigation_session import NavigationSession, NavigationState
from modules.route_finder import RouteFinder
from modules.three_d_map import (
    build_3d_scene_payload,
    render_three_d_scene_html,
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
    render_kpi_card,
)

# Apply unified design system and retrieve singleton services
apply_custom_theme()
services = get_app_services()

benchmark_cmap = services["campus_map"]
benchmark_rf = services["route_finder"]
acc_engine = services["accessibility_engine"]
obs_manager = services["obstacle_manager"]

# Hero Banner
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">🏢 Interactive 3D Campus Navigation & Digital Twin</div>
        <div class="hero-subtitle">
            Explore a 3D isometric representation of JAIN Global Campus and the Faculty of Engineering & Technology (FET).
            Navigate 5 full building levels (Ground to 4th Floor), inspect octagonal corridors and amphitheater steps,
            track elevator shafts and stairwells, and plan wheelchair-accessible routes in full 3D.
        </div>
        <div class="hero-chip-container">
            <span class="hero-chip">✨ Three.js WebGL Engine</span>
            <span class="hero-chip">🏛️ JAIN Global Campus Digital Twin</span>
            <span class="hero-chip">🏢 5-Floor FET Building Reconstruction</span>
            <span class="hero-chip">🛗 Vertical Connector Modeling</span>
            <span class="hero-chip">♿ Real-Time Wheelchair Routing</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Mandatory Architectural Disclaimer
st.markdown(
    """
    <div class="disclaimer-banner">
        <b>📐 Schematic 3D Architecture Notice:</b> The 3D campus models, building volumes, and floor platforms
        rendered below are <b>schematic representations based on illustrative graph coordinates and campus reference layouts</b>.
        They are designed for topological pathfinding demonstration and <b>do not represent surveyed architectural CAD blueprints
        or physical building dimensions</b>.
    </div>
    """,
    unsafe_allow_html=True,
)

# 3D Environment Model Switcher
st.markdown('<div class="ui-card" style="padding: 12px 18px; margin-bottom: 16px;">', unsafe_allow_html=True)
col_m1, col_m2 = st.columns([1.8, 1.2])
with col_m1:
    model_choice = st.radio(
        "🗺️ Select 3D Campus Environment:",
        options=[
            "🏛️ JAIN Global Campus & FET 5-Floor Digital Twin",
            "📐 Schematic Benchmark Model (15-Node Reference)",
        ],
        index=0,
        horizontal=True,
        key="selected_3d_environment_mode",
        help="Switch between the 5-floor JAIN Global Campus digital twin and the schematic 15-node benchmark model.",
    )
with col_m2:
    if "JAIN" in model_choice:
        st.markdown(
            """
            <div style="font-size: 12px; color: #35D99A; padding-top: 8px;">
                <b>Active Campus:</b> JAIN Global Campus, Kanakapura Road<br>
                <b>Structure:</b> FET 5-Floor Complex (79 Locations, 106 Pathways)
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="font-size: 12px; color: #9CAFA5; padding-top: 8px;">
                <b>Active Campus:</b> Academic Complex Benchmark<br>
                <b>Structure:</b> 2-Floor Schematic (15 Locations, 17 Pathways)
            </div>
            """,
            unsafe_allow_html=True,
        )
st.markdown("</div>", unsafe_allow_html=True)

is_jain_twin = "JAIN" in model_choice

# Prepare active map and route finder based on model selection
if is_jain_twin:
    active_cmap = load_jain_campus_map()
    # Synchronize active verified obstacles to JAIN graph
    for haz in obs_manager.get_active_obstacles():
        u = haz.get("source_location_id")
        v = haz.get("destination_location_id")
        if u and v and active_cmap.graph.has_edge(u, v):
            active_cmap.graph[u][v]["status"] = "blocked"
    active_rf = RouteFinder(active_cmap)

    raw_locs = active_cmap.get_all_locations()

    def format_jain_label(loc: dict) -> str:
        fl = int(loc.get("floor", 0))
        fl_str = "Outdoor" if fl == -1 else f"Floor {fl}"
        return f"[{fl_str}] {loc.get('name', loc['id'])} ({loc['id']})"

    all_locs = sorted(
        raw_locs,
        key=lambda x: (int(x.get("floor", 0)), str(x.get("name", ""))),
    )
    loc_options = {format_jain_label(loc): loc["id"] for loc in all_locs}
    loc_labels = list(loc_options.keys())

    # Set smart defaults: Main Gate -> Fourth Floor HPC Lab
    default_start_idx = 0
    default_dest_idx = 0
    for idx, label in enumerate(loc_labels):
        if "OUT_GATE_MAIN" in label:
            default_start_idx = idx
        if "FET_4F_HPC_CLUSTER" in label:
            default_dest_idx = idx
else:
    active_cmap = benchmark_cmap
    active_rf = benchmark_rf

    all_locs = sorted(
        active_cmap.get_all_locations(),
        key=lambda x: (int(x.get("floor", 0)), str(x.get("name", ""))),
    )
    loc_options = {
        f"[{loc['id']}] {loc['name']} (Floor {loc['floor']})": loc["id"]
        for loc in all_locs
    }
    loc_labels = list(loc_options.keys())

    default_start_idx = 0
    default_dest_idx = 0
    for idx, label in enumerate(loc_labels):
        if "[LOC_01]" in label:
            default_start_idx = idx
        if "[LOC_12]" in label:
            default_dest_idx = idx

# --- LAYOUT: 3D VIEWPORT & CONTROL CONSOLE ---
col_viewport, col_controls = st.columns([2.3, 1.0], gap="medium")

with col_controls:
    st.markdown('<div class="ui-card">', unsafe_allow_html=True)
    st.markdown("#### 🧭 3D Route Planning")

    # Search & Filter Enhancements for Location Selection
    if is_jain_twin:
        filter_floor = st.selectbox(
            "Filter Destination by Floor:",
            options=["All Floors & Outdoor", "Outdoor Campus", "Ground Floor (Level 0)", "First Floor (Level 1)", "Second Floor (Level 2)", "Third Floor (Level 3)", "Fourth Floor (Level 4)"],
            index=0,
            key="3d_filter_floor",
        )
        filtered_labels = loc_labels
        if filter_floor == "Outdoor Campus":
            filtered_labels = [l for l in loc_labels if "[Outdoor]" in l]
        elif filter_floor == "Ground Floor (Level 0)":
            filtered_labels = [l for l in loc_labels if "[Floor 0]" in l]
        elif filter_floor == "First Floor (Level 1)":
            filtered_labels = [l for l in loc_labels if "[Floor 1]" in l]
        elif filter_floor == "Second Floor (Level 2)":
            filtered_labels = [l for l in loc_labels if "[Floor 2]" in l]
        elif filter_floor == "Third Floor (Level 3)":
            filtered_labels = [l for l in loc_labels if "[Floor 3]" in l]
        elif filter_floor == "Fourth Floor (Level 4)":
            filtered_labels = [l for l in loc_labels if "[Floor 4]" in l]
        
        if not filtered_labels:
            filtered_labels = loc_labels
    else:
        filtered_labels = loc_labels

    start_label = st.selectbox(
        "Origin Location:",
        options=loc_labels,
        index=default_start_idx if default_start_idx < len(loc_labels) else 0,
        key="3d_route_start",
        help="Choose starting campus facility.",
    )
    start_id = loc_options[start_label]

    # Destination index within filtered list
    dest_idx = 0
    for idx, label in enumerate(filtered_labels):
        if default_dest_idx < len(loc_labels) and label == loc_labels[default_dest_idx]:
            dest_idx = idx
            break

    dest_label = st.selectbox(
        "Destination Facility:",
        options=filtered_labels,
        index=dest_idx,
        key="3d_route_dest",
        help="Choose target campus destination.",
    )
    dest_id = loc_options[dest_label]

    c_algo, c_wheelchair = st.columns(2)
    with c_algo:
        algo_choice = st.selectbox(
            "Algorithm:",
            options=["Dijkstra", "BFS"],
            index=0,
            key="3d_algo_choice",
            help="Dijkstra optimizes distance; BFS finds fewest pathway hops.",
        )
    with c_wheelchair:
        st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)
        wheelchair_only = st.checkbox(
            "♿ Wheelchair",
            value=True,
            key="3d_wheelchair_toggle",
            help="Strictly avoids stairs and utilizes elevator vertical connections.",
        )

    calculate_btn = st.button("🚀 Calculate 3D Route", type="primary", use_container_width=True)

    # Initialize or retrieve persistent Navigation Session in session_state
    if "nav_session" not in st.session_state or st.session_state["nav_session"] is None:
        st.session_state["nav_session"] = NavigationSession()
    nav_session: NavigationSession = st.session_state["nav_session"]

    # Check if route calculation or preview update is needed
    session_needs_update = (
        calculate_btn
        or nav_session.state == NavigationState.IDLE
        or nav_session.origin_id != start_id
        or nav_session.destination_id != dest_id
        or nav_session.wheelchair_mode != wheelchair_only
        or nav_session.algorithm != algo_choice.lower()
    )

    if session_needs_update and nav_session.state in (
        NavigationState.IDLE,
        NavigationState.ROUTE_PREVIEW,
        NavigationState.NO_ACCESSIBLE_ROUTE,
    ):
        nav_session.start_preview(
            origin_id=start_id,
            destination_id=dest_id,
            campus_map=active_cmap,
            route_finder=active_rf,
            algorithm=algo_choice.lower(),
            wheelchair_mode=wheelchair_only,
        )

    # Real-Time Obstacle Detection & Automatic Rerouting
    if nav_session.state in (NavigationState.NAVIGATING, NavigationState.PAUSED):
        nav_session.detect_and_handle_obstacles(
            obstacle_manager=obs_manager,
            campus_map=active_cmap,
            route_finder=active_rf,
        )

    # Real-Time Wayfinding Session Controller
    st.markdown("---")
    st.markdown("##### 🚶 Real-Time Wayfinding Controller")

    if nav_session.state in (NavigationState.IDLE, NavigationState.ROUTE_PREVIEW):
        if st.button("🚀 Start Live Navigation", type="primary", use_container_width=True, key="btn_start_nav"):
            nav_session.start_navigation()
            st.rerun()
    elif nav_session.state == NavigationState.NAVIGATING:
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("⏸️ Pause", use_container_width=True, key="btn_pause_nav"):
                nav_session.pause_navigation()
                st.rerun()
        with c2:
            if st.button("⏭️ Next Step", use_container_width=True, key="btn_step_nav"):
                nav_session.step_forward(active_cmap)
                st.rerun()
        with c3:
            if st.button("⏹️ Cancel", use_container_width=True, key="btn_cancel_nav"):
                nav_session.cancel_navigation()
                st.rerun()
    elif nav_session.state in (NavigationState.PAUSED, NavigationState.FLOOR_TRANSITION):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("▶️ Resume", type="primary", use_container_width=True, key="btn_resume_nav"):
                nav_session.resume_navigation()
                st.rerun()
        with c2:
            if st.button("⏭️ Next Step", use_container_width=True, key="btn_step_nav_p"):
                nav_session.step_forward(active_cmap)
                st.rerun()
        with c3:
            if st.button("🔄 Restart", use_container_width=True, key="btn_restart_nav"):
                nav_session.restart_navigation()
                st.rerun()
    elif nav_session.state == NavigationState.ARRIVED:
        st.success("🎉 You have arrived at your destination!")
        if st.button("🔄 Start New Navigation", type="primary", use_container_width=True, key="btn_arrived_new"):
            nav_session.restart_navigation()
            st.rerun()
    elif nav_session.state == NavigationState.NO_ACCESSIBLE_ROUTE:
        st.warning("⚠️ No accessible route currently available.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Location Inspector Card in Sidebar
    st.markdown('<div class="ui-card" style="margin-top: 14px;">', unsafe_allow_html=True)
    st.markdown("#### 🔍 Facility Inspector")
    inspect_label = st.selectbox(
        "Inspect Location:",
        options=loc_labels,
        index=default_dest_idx if default_dest_idx < len(loc_labels) else 0,
        key="3d_inspect_loc",
        help="Select a campus facility to highlight and view accessibility attributes.",
    )
    selected_inspect_id = loc_options[inspect_label]

    inspect_loc = active_cmap.get_location(selected_inspect_id) or {}
    floor_num = int(inspect_loc.get("floor", 0))
    category = str(inspect_loc.get("category", "office")).title()
    building = str(inspect_loc.get("building", "Academic Complex"))
    is_step_free = bool(inspect_loc.get("wheelchair_accessible", True))

    floor_display = "Outdoor Grounds" if floor_num == -1 else f"Floor {floor_num} ({FLOOR_NAMES.get(floor_num, '')})"

    st.markdown(
        f"""
        <div style="font-size: 13px; line-height: 1.6; margin-top: 6px;">
            <div><b>Facility:</b> <span style="color: {ACCENT_GREEN};">{inspect_loc.get('name', selected_inspect_id)}</span></div>
            <div><b>Building:</b> {building}</div>
            <div><b>Building Level:</b> {floor_display}</div>
            <div><b>Category:</b> {category}</div>
            <div><b>Accessibility:</b> <span style="color: {'#35D99A' if is_step_free else '#F5B942'};">
                {'✅ Step-Free Accessible' if is_step_free else '⚠️ Stair Access Only'}
            </span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Active Verified Hazards Summary
    active_hazards = obs_manager.get_active_obstacles()
    if active_hazards:
        st.markdown('<div class="ui-card" style="margin-top: 14px; border-color: rgba(248, 113, 113, 0.4);">', unsafe_allow_html=True)
        st.markdown(f"#### ⚠️ Active Hazards ({len(active_hazards)})")
        for haz in active_hazards[:3]:
            u, v = haz.get("source_location_id"), haz.get("destination_location_id")
            title = f"{u} ➔ {v}" if u and v else haz.get("location_id", "Campus Pathway")
            st.markdown(
                f"<div style='font-size: 12px; margin-bottom: 4px; color: #F87171;'>"
                f"🚫 <b>{title}:</b> {haz.get('category')} ({haz.get('severity')})</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

# Build authoritative scene payload based on model choice
if is_jain_twin:
    scene_payload = build_jain_digital_twin_payload(
        campus_map=active_cmap,
        route_finder=active_rf,
        obstacle_manager=obs_manager,
        start_id=start_id,
        dest_id=dest_id,
        algorithm=algo_choice.lower(),
        wheelchair_accessible=wheelchair_only,
        selected_location_id=selected_inspect_id,
        view_mode="all_floors",
        navigation_session=nav_session,
    )
    route_data = scene_payload.get("active_route")
    route_comparison = scene_payload.get("route_comparison")
    html_3d = render_jain_digital_twin_html(scene_payload, height=750)
else:
    scene_payload = build_3d_scene_payload(
        campus_map=active_cmap,
        route_finder=active_rf,
        obstacle_manager=obs_manager,
        start_id=start_id,
        dest_id=dest_id,
        algorithm=algo_choice.lower(),
        wheelchair_accessible=wheelchair_only,
        selected_location_id=selected_inspect_id,
        view_mode="combined",
    )
    route_data = scene_payload.get("active_route")
    route_comparison = None
    html_3d = render_three_d_scene_html(scene_payload, height=750)

with col_viewport:
    # Phase 15: Live Navigation Dashboard & Status Banner
    if nav_session and nav_session.state in (
        NavigationState.NAVIGATING,
        NavigationState.PAUSED,
        NavigationState.FLOOR_TRANSITION,
        NavigationState.ARRIVED,
    ):
        curr_instr = nav_session.get_current_instruction()
        next_instr = nav_session.get_next_instruction()
        dest_loc = active_cmap.get_location(nav_session.destination_id or "") or {}
        dest_name = dest_loc.get("name", nav_session.destination_id)
        dest_floor_name = format_floor_name(int(dest_loc.get("floor", 0)))

        is_arr = nav_session.state == NavigationState.ARRIVED
        state_color = "#10B981" if is_arr else ("#35D99A" if nav_session.state == NavigationState.NAVIGATING else "#F5B942")

        st.markdown(
            f"""
            <div style="background: rgba(13, 31, 24, 0.95); border: 1.5px solid {state_color}; border-radius: 12px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.5);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <span style="background: rgba(53, 217, 154, 0.18); color: {state_color}; font-weight: 800; font-size: 11px; padding: 4px 10px; border-radius: 6px; letter-spacing: 0.8px; border: 1px solid {state_color};">
                            {nav_session.state.value}
                        </span>
                        <span style="font-size: 12px; color: #9CAFA5; margin-left: 10px;">
                            Target: <b style="color: #F8FAFC;">{dest_name}</b> ({dest_floor_name})
                        </span>
                    </div>
                    <div style="font-size: 13px; color: #35D99A; font-weight: 700;">
                        {nav_session.remaining_distance:.1f} m remaining &nbsp;|&nbsp; ~{nav_session.remaining_time:.0f} s
                    </div>
                </div>
                <div style="display: flex; align-items: flex-start; gap: 12px; margin: 10px 0;">
                    <div style="font-size: 26px; line-height: 1;">{curr_instr.icon if curr_instr else '🧭'}</div>
                    <div style="flex-grow: 1;">
                        <div style="font-size: 15px; font-weight: 700; color: #F8FAFC;">
                            {curr_instr.text if curr_instr else 'Proceeding along active route...'}
                        </div>
                        {f'<div style="font-size: 11px; color: #9CAFA5; margin-top: 4px;"><b>Next Step:</b> {next_instr.text}</div>' if next_instr and not is_arr else ''}
                    </div>
                </div>
                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 3px; overflow: hidden; margin-top: 8px;">
                    <div style="background: linear-gradient(90deg, #16A36A, #35D99A); width: {nav_session.progress_percentage:.1f}%; height: 100%; transition: width 0.4s ease;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: #9CAFA5; margin-top: 6px;">
                    <span>Progress: <b>{nav_session.progress_percentage:.0f}%</b></span>
                    <span>Steps: <b>{nav_session.completed_steps} of {nav_session.total_steps}</b></span>
                    <span>Current Floor: <b>{format_floor_name(nav_session.current_floor)}</b></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if is_arr:
            st.balloons()
            st.markdown(
                f"""
                <div style="background: rgba(16, 185, 129, 0.15); border: 2px solid #10B981; border-radius: 12px; padding: 16px 20px; margin-bottom: 14px; text-align: center;">
                    <div style="font-size: 22px; font-weight: 800; color: #35D99A; margin-bottom: 6px;">🎉 YOU HAVE ARRIVED!</div>
                    <div style="font-size: 14px; color: #F8FAFC; margin-bottom: 10px;">
                        Destination: <b>{dest_name}</b> | Building: <b>FET Complex</b> | Level: <b>{dest_floor_name}</b>
                    </div>
                    <div style="display: flex; justify-content: center; gap: 24px; font-size: 12px; color: #A7F3D0;">
                        <div>📏 <b>Distance:</b> {nav_session.total_distance:.1f} m</div>
                        <div>⏱️ <b>Estimated Duration:</b> ~{(nav_session.total_time/60):.1f} min</div>
                        <div>🛗 <b>Floor Transitions:</b> {nav_session.floor_transitions_count}</div>
                        <div>♿ <b>Mode:</b> {"Wheelchair Step-Free" if nav_session.wheelchair_mode else "Standard Pedestrian"}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if nav_session.is_rerouted:
            st.markdown(
                f"""
                <div style="background: rgba(245, 185, 66, 0.15); border: 1px solid #F5B942; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; font-size: 12px; color: #F8FAFC;">
                    <b>⚠️ Active Obstacle Detour Notice:</b> {nav_session.reroute_reason}<br>
                    The navigation engine has dynamically rerouted you around the blocked segment to guarantee continuous accessibility.
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Render Three.js HTML Container
    components.html(html_3d, height=760, scrolling=False)

    # 3D Viewport Interaction Guide
    st.markdown(
        """
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center;
                    background: rgba(13, 31, 24, 0.7); border: 1px solid rgba(53, 217, 154, 0.2);
                    border-radius: 10px; padding: 8px 14px; font-size: 12px; color: #9CAFA5; margin-top: 6px;">
            <span>🖱️ <b>Rotate:</b> Left-Click + Drag</span>
            <span>🔍 <b>Zoom:</b> Mouse Scroll</span>
            <span>✋ <b>Pan:</b> Right-Click + Drag</span>
            <span>💥 <b>Exploded View:</b> Click top HUD button to separate building floors</span>
            <span>📍 <b>Select:</b> Click any 3D room/building to inspect</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- ROUTE PERFORMANCE METRICS & TURN-BY-TURN INSTRUCTIONS ---
if route_data and route_data.get("success"):
    st.markdown("---")
    st.markdown("### 🧭 Active Route Guidance & Navigational Performance")

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        render_kpi_card("Total Distance", f"{route_data['total_distance']:.1f} m", "Physical pathway length", PRIMARY_GREEN)
    with m2:
        render_kpi_card("Est. Time", f"{route_data['total_time']:.0f} s", f"~{(route_data['total_time']/60):.1f} min transit", ACCENT_GREEN)
    with m3:
        render_kpi_card("Route Segments", f"{route_data['edge_count']} Steps", f"{len(route_data['path'])} facilities traversed", INFO)
    with m4:
        acc_text = "Wheelchair Step-Free" if route_data.get("is_accessible") else "Stair Navigation"
        render_kpi_card("Accessibility", acc_text, "Barrier-free status", ACCENT_GREEN if route_data.get("is_accessible") else WARNING)
    with m5:
        transitions = route_data.get("cross_floor_transitions", [])
        trans_text = f"{len(transitions)} Transition" if transitions else "Single Floor"
        render_kpi_card("Floor Transfer", trans_text, "Elevator / Stairs connection", INFO)

    # Cross-Floor Alerts
    if transitions:
        for trans in transitions:
            icon = "🛗" if trans.get("connector_type") == "Elevator" else "🪜"
            st.info(f"{icon} **Vertical Transition Alert:** {trans.get('instruction')}")

    # Active Verified Obstacle Detour Banner (if rerouted)
    active_verified_hazards = [h for h in obs_manager.get_active_obstacles() if h.get("status") == "Verified"]
    if active_verified_hazards:
        st.markdown(
            f"""
            <div style="background: rgba(248, 113, 113, 0.15); border: 1px solid rgba(248, 113, 113, 0.4); border-radius: 8px; padding: 10px 14px; margin-top: 10px; font-size: 12px; color: #F8FAFC;">
                <b>⚠️ Active Obstacle Detour Notice:</b> The navigation engine detected <b>{len(active_verified_hazards)} active verified hazard(s)</b> on campus. Routes are dynamically rerouted around blocked corridors and non-operational vertical connectors to guarantee continuous accessibility.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Multi-Route Trade-off Comparison Panel
    if route_comparison and len(route_comparison) > 1:
        st.markdown("#### ⚖️ Multi-Route Trade-off Analysis & Algorithm Comparison")
        st.caption("Heuristic path comparison evaluating physical distance, transit duration, vertical connectors, and step-free accessibility.")

        comp_cols = st.columns(len(route_comparison))
        for idx, (k, r_info) in enumerate(route_comparison.items()):
            if not r_info:
                continue
            with comp_cols[idx]:
                is_current = (k == algo_choice.lower())
                border_color = "#35D99A" if is_current else "rgba(156, 175, 165, 0.25)"
                bg_color = "rgba(53, 217, 154, 0.12)" if is_current else "rgba(13, 31, 24, 0.6)"
                st.markdown(
                    f"""
                    <div style="border: 1px solid {border_color}; background: {bg_color}; border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;">
                        <div style="font-weight: 700; font-size: 13px; color: {'#35D99A' if is_current else '#F8FAFC'}; margin-bottom: 4px;">
                            {'⭐ Active: ' if is_current else ''}{r_info['label']}
                        </div>
                        <div style="font-size: 11px; color: #9CAFA5; line-height: 1.5; margin-bottom: 8px;">
                            {r_info['rationale']}
                        </div>
                        <div style="font-size: 12px; line-height: 1.8;">
                            <div>📏 <b>Distance:</b> {r_info['total_distance']} m</div>
                            <div>⏱️ <b>Est. Time:</b> {r_info['total_time']} s</div>
                            <div>🪜 <b>Segments:</b> {r_info['edge_count']} Steps</div>
                            <div>🛗 <b>Floor Transfers:</b> {r_info['floor_transitions']}</div>
                            <div>♿ <b>Wheelchair:</b> <span style="color: {'#35D99A' if r_info['is_accessible'] else '#F5B942'};">{'Passable' if r_info['is_accessible'] else 'Stairs'}</span></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Detailed Step-by-Step Directions
    with st.expander("📋 Turn-by-Turn Navigational Guidance", expanded=True):
        steps = route_data.get("steps", [])
        for step in steps:
            s_num = step['step_number']
            is_active_step = (
                nav_session.state in (NavigationState.NAVIGATING, NavigationState.PAUSED, NavigationState.FLOOR_TRANSITION)
                and s_num == nav_session.current_step_index + 1
            )
            is_completed_step = (
                nav_session.state in (NavigationState.NAVIGATING, NavigationState.PAUSED, NavigationState.FLOOR_TRANSITION, NavigationState.ARRIVED)
                and s_num < nav_session.current_step_index + 1
            )

            box_border = "2px solid #35D99A" if is_active_step else "1px solid rgba(156, 175, 165, 0.2)"
            box_bg = "rgba(53, 217, 154, 0.14)" if is_active_step else "rgba(13, 31, 24, 0.6)"
            box_opacity = "0.65" if is_completed_step else "1.0"
            status_badge = ""
            if is_active_step:
                status_badge = '<span style="background: #16A36A; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; margin-left: 8px;">📍 YOU ARE HERE</span>'
            elif is_completed_step:
                status_badge = '<span style="background: rgba(16, 185, 129, 0.2); color: #35D99A; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; margin-left: 8px;">✅ COMPLETED</span>'

            icon = "🛗" if step.get("has_elevator") else "🪜" if step.get("has_stairs") else "♿" if step.get("has_ramp") else "🚶"
            st.markdown(
                f"""
                <div class="step-box" style="border: {box_border}; background: {box_bg}; opacity: {box_opacity}; transition: all 0.3s ease;">
                    <div class="step-number" style="{'background: #35D99A; color: #07130F; font-weight: 800;' if is_active_step else ''}">{s_num}</div>
                    <div style="flex-grow: 1;">
                        <div style="font-weight: 600; font-size: 14px; color: {WHITE}; display: flex; align-items: center; flex-wrap: wrap; gap: 4px;">
                            <span>{icon} {step['instruction']}</span> {status_badge}
                        </div>
                        <div style="font-size: 11px; color: {SECONDARY_TEXT}; margin-top: 4px;">
                            Segment: <b>{step['from_name']}</b> (Floor {step['from_floor']}) ➔ <b>{step['to_name']}</b> (Floor {step['to_floor']}) &nbsp;|&nbsp;
                            Distance: <b>{step['distance']:.1f} m</b> &nbsp;|&nbsp;
                            Est. Time: <b>{step['estimated_time']:.1f} s</b> &nbsp;|&nbsp;
                            Wheelchair Passable: <b>{'Yes' if step['wheelchair_accessible'] else 'No (Stairs)'}</b>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Heuristic Accessibility Notice
    st.markdown(
        """
        <div style="font-size: 11px; color: #9CAFA5; margin-top: 14px; padding: 8px 12px; background: rgba(13, 31, 24, 0.5); border-left: 3px solid #35D99A; border-radius: 4px;">
            ℹ️ <b>Accessibility Indicator Disclosure:</b> Route classifications and continuous accessibility scores (0–100) are generated as heuristic navigational guidance based on recorded building features (ramps, elevators, doorway clearance) and live field reports. They serve as assistive navigation metrics and do not constitute statutory architectural accessibility compliance certificates.
        </div>
        """,
        unsafe_allow_html=True,
    )

elif route_data and not route_data.get("success"):
    st.error(f"❌ Route Unavailable: {route_data.get('error_message')}")
    st.markdown(
        """
        <div style="font-size: 12px; color: #F5B942; margin-top: 6px;">
            <b>Guidance:</b> If wheelchair mode is enabled and all vertical elevators connecting to the destination floor are blocked by active maintenance, try disabling wheelchair mode to inspect alternative staircase paths, or choose another destination facility.
        </div>
        """,
        unsafe_allow_html=True,
    )
