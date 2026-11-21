"""3D Campus Map Page - Interactive Three.js isometric multi-floor campus navigation visualizer.

Provides 360-degree interactive camera orbit, exploded multi-floor viewing,
room volume inspection, authoritative Python route planning with 3D spline rendering,
vertical elevator/stair transitions, and dynamic obstacle synchronization.

DISCLAIMER:
Coordinates and node positions are schematic graph-layout coordinates designed
strictly for connectivity visualization and pathfinding demonstration. They do
not represent surveyed architectural CAD blueprints or surveyed physical dimensions.
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from modules.three_d_map import (
    SCHEMATIC_SCALE,
    build_3d_scene_payload,
    get_3d_locations_data,
    get_3d_pathways_data,
    get_3d_route_data,
    normalize_3d_coordinates,
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

cmap = services["campus_map"]
route_finder = services["route_finder"]
acc_engine = services["accessibility_engine"]
obs_manager = services["obstacle_manager"]

# Hero Banner
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">🏢 Interactive 3D Campus Navigation Engine</div>
        <div class="hero-subtitle">
            Explore a 3D isometric representation of the academic complex. Inspect multi-floor rooms,
            track vertical elevator shafts and stairwells, and visualize live accessible routes in full 3D.
        </div>
        <div class="hero-chip-container">
            <span class="hero-chip">✨ Three.js WebGL Engine</span>
            <span class="hero-chip">📐 Multi-Floor Isometric Projection</span>
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
        <b>📐 Schematic 3D Architecture Notice:</b> The 3D building models, floor platforms, and pathway geometries
        rendered below are <b>schematic representations based on illustrative graph-layout coordinates</b>.
        They are designed for topological pathfinding demonstration and <b>do not represent surveyed architectural CAD blueprints
        or physical building dimensions</b>.
    </div>
    """,
    unsafe_allow_html=True,
)

# Prepare location selection options
all_locs = sorted(cmap.get_all_locations(), key=lambda x: (x.get("floor", 0), x.get("name", "")))
loc_options = {
    f"[{loc['id']}] {loc['name']} (Floor {loc['floor']})": loc["id"]
    for loc in all_locs
}
loc_labels = list(loc_options.keys())

# Default selections: LOC_01 (Main Entrance) -> LOC_12 (CS Lab 101)
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

    inspect_loc = cmap.get_location(selected_inspect_id) or {}
    floor_num = inspect_loc.get("floor", 0)
    category = inspect_loc.get("category", "office").title()
    is_step_free = selected_inspect_id != "LOC_11"

    st.markdown(
        f"""
        <div style="font-size: 13px; line-height: 1.6; margin-top: 6px;">
            <div><b>Facility:</b> <span style="color: {ACCENT_GREEN};">{inspect_loc.get('name', selected_inspect_id)}</span></div>
            <div><b>Building Level:</b> Floor {floor_num} {'(Ground)' if floor_num == 0 else '(Upper)'}</div>
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

# Build authoritative scene payload
initial_view_mode = "combined"
scene_payload = build_3d_scene_payload(
    campus_map=cmap,
    route_finder=route_finder,
    obstacle_manager=obs_manager,
    start_id=start_id,
    dest_id=dest_id,
    algorithm=algo_choice.lower(),
    wheelchair_accessible=wheelchair_only,
    selected_location_id=selected_inspect_id,
    view_mode=initial_view_mode,
)

route_data = scene_payload.get("active_route")

with col_viewport:
    # Render Three.js HTML Container
    html_3d = render_three_d_scene_html(scene_payload, height=720)
    components.html(html_3d, height=730, scrolling=False)

    # 3D Viewport Interaction Guide
    st.markdown(
        """
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center;
                    background: rgba(13, 31, 24, 0.7); border: 1px solid rgba(53, 217, 154, 0.2);
                    border-radius: 10px; padding: 8px 14px; font-size: 12px; color: #9CAFA5; margin-top: 6px;">
            <span>🖱️ <b>Rotate:</b> Left-Click + Drag</span>
            <span>🔍 <b>Zoom:</b> Mouse Scroll</span>
            <span>✋ <b>Pan:</b> Right-Click + Drag</span>
            <span>💥 <b>Exploded View:</b> Click top HUD button to separate Floor 1</span>
            <span>📍 <b>Select:</b> Click any 3D room to inspect</span>
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
