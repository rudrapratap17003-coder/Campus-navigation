"""3D Campus Map Page - Interactive Three.js multi-floor campus navigation visualizer.

Provides 360-degree interactive camera orbit, exploded multi-floor viewing,
room volume inspection, authoritative Python route planning with 3D spline rendering,
vertical elevator/stair transitions, and dynamic obstacle synchronization.

Supports:
1. JAIN Global Campus & FET 5-Floor Digital Twin (Ground to Fourth Floor + Outdoor Campus).
2. Schematic Benchmark Model (15-Node Topological Reference).

DISCLAIMER:
All 3D building models and pathway geometries are schematic digital twin representations
designed for graph connectivity visualization, accessibility inspection, and pathfinding
demonstration. They do not represent surveyed architectural CAD blueprints or surveyed physical dimensions.
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from modules.campus_map import CampusMap
from modules.jain_digital_twin import (
    FLOOR_NAMES,
    build_jain_digital_twin_payload,
    load_jain_campus_map,
    render_jain_digital_twin_html,
)
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

    all_locs = sorted(
        active_cmap.get_all_locations(),
        key=lambda x: (int(x.get("floor", 0)), str(x.get("name", ""))),
    )

    def format_jain_label(loc: dict) -> str:
        fl = int(loc.get("floor", 0))
        fl_str = "Outdoor" if fl == -1 else f"Floor {fl}"
        return f"[{fl_str}] {loc.get('name', loc['id'])} ({loc['id']})"

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

    start_label = st.selectbox(
        "Origin Location:",
        options=loc_labels,
        index=default_start_idx,
        key="3d_route_start",
        help="Choose starting campus facility.",
    )
    start_id = loc_options[start_label]

    dest_label = st.selectbox(
        "Destination Facility:",
        options=loc_labels,
        index=default_dest_idx,
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
    st.markdown("</div>", unsafe_allow_html=True)

    # Location Inspector Card in Sidebar
    st.markdown('<div class="ui-card" style="margin-top: 14px;">', unsafe_allow_html=True)
    st.markdown("#### 🔍 Facility Inspector")
    inspect_label = st.selectbox(
        "Inspect Location:",
        options=loc_labels,
        index=default_dest_idx,
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
    )
    route_data = scene_payload.get("active_route")
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
    html_3d = render_three_d_scene_html(scene_payload, height=750)

with col_viewport:
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

    # Detailed Step-by-Step Directions
    with st.expander("📋 Turn-by-Turn Navigational Guidance", expanded=True):
        steps = route_data.get("steps", [])
        for step in steps:
            icon = "🛗" if step.get("has_elevator") else "🪜" if step.get("has_stairs") else "♿" if step.get("has_ramp") else "🚶"
            st.markdown(
                f"""
                <div class="step-box">
                    <div class="step-number">{step['step_number']}</div>
                    <div style="flex-grow: 1;">
                        <div style="font-weight: 600; font-size: 14px; color: {WHITE};">
                            {icon} {step['instruction']}
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

elif route_data and not route_data.get("success"):
    st.error(f"❌ Route Unavailable: {route_data.get('error_message')}")
