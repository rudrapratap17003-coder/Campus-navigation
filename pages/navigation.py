"""Navigation Page - Route planning, turn-by-turn guidance, and accessibility evaluation.

Supports both JAIN Global Campus (79 locations across 6 levels) and the Benchmark Model (15 locations).
"""

from __future__ import annotations

from typing import Any, Dict
import streamlit as st

from modules.accessibility import AccessibilityEngine
from modules.destination_search import search_destinations
from modules.jain_digital_twin import load_jain_campus_map
from modules.route_finder import RouteFinder
from modules.ui_theme import (
    ACCENT_GREEN,
    ERROR,
    PRIMARY_GREEN,
    SECONDARY_TEXT,
    WARNING,
    WHITE,
    apply_custom_theme,
    get_app_services,
    render_kpi_card,
)

apply_custom_theme()
services = get_app_services()

st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">🧭 Accessible Route Planner</div>
        <div class="hero-subtitle">
            Calculate barrier-free pedestrian routes across campus facilities.
            Automatically avoids stairways and active hazard reports while utilizing code-compliant ramps and elevators.
        </div>
        <div class="hero-chips">
            <span class="hero-chip">🏛️ JAIN Global Campus & FET</span>
            <span class="hero-chip">🏢 Multi-Floor Wayfinding</span>
            <span class="hero-chip">♿ Step-Free Routing</span>
            <span class="hero-chip">🛗 Elevator Guidance</span>
        </div>
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
        key="nav_campus_env_choice",
    )
is_jain = "JAIN" in campus_model_choice

with c_env2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🏢 Switch to 3D Digital Twin", width="stretch", help="Open 3D WebGL Digital Twin navigation"):
        st.switch_page("pages/3d_campus_map.py")

obs_manager = services["obstacle_manager"]
if is_jain:
    cmap = load_jain_campus_map()
    obs_manager.sync_obstacles_to_campus_map(cmap)
    route_finder = RouteFinder(cmap)
    acc_engine = AccessibilityEngine(cmap)
else:
    cmap = services["campus_map"]
    route_finder = services["route_finder"]
    acc_engine = AccessibilityEngine(cmap)

locations = sorted(cmap.get_all_locations(), key=lambda x: (int(x.get("floor", 0)), str(x.get("name", ""))))

def format_nav_label(loc: Dict[str, Any]) -> str:
    fl = int(loc.get("floor", 0))
    fl_tag = "Outdoor" if fl == -1 else f"Floor {fl}"
    return f"[{fl_tag}] {loc['name']} ({loc['id']})"

location_options = {format_nav_label(loc): loc["id"] for loc in locations}
loc_labels = list(location_options.keys())

# --- ROUTE INPUT FORM CARD ---
with st.container(border=True):
    st.markdown("#### ⚙️ Route Configuration & Criteria")

    # Quick suggestions pills
    st.markdown("<div style='font-size: 11px; color: #9CAFA5; margin-bottom: 4px;'><b>Quick Destination Suggestions:</b></div>", unsafe_allow_html=True)
    pill_cols = st.columns(4)
    quick_keywords = ["HPC Lab", "Library", "Dean", "Robotics"] if is_jain else ["Classroom", "Lab", "Restroom", "Elevator"]
    for i, kw in enumerate(quick_keywords):
        with pill_cols[i]:
            if st.button(kw, key=f"nav_pill_{kw}", width="stretch"):
                st.session_state["nav_dest_search_query"] = kw
                st.rerun()

    if "nav_dest_search_query" not in st.session_state:
        st.session_state["nav_dest_search_query"] = ""

    # Destination Search with Keyword Intelligence
    dest_search_query = st.text_input(
        "🔍 Search Destination (Lab, Room, Department, Keyword):",
        placeholder="e.g. AI Lab, HPC, Library, Robotics, Seminar, Mechanical...",
        key="nav_dest_search_query",
    )

    matched_dest_id = None
    if dest_search_query.strip() and is_jain:
        search_matches = search_destinations(dest_search_query, cmap, limit=10)
        if search_matches:
            st.caption(f"✨ Found {len(search_matches)} match(es) for '{dest_search_query}'")
            search_opts = {
                f"[{'Outdoor' if m.floor == -1 else f'Floor {m.floor}'}] {m.name} ({m.location_id})": m.location_id
                for m in search_matches
            }
            sel_match_label = st.selectbox(
                "Select Matched Facility:",
                options=list(search_opts.keys()),
                index=0,
                key="nav_matched_dest_select",
            )
            matched_dest_id = search_opts[sel_match_label]
        else:
            st.caption("ℹ️ No exact keyword matches found.")

    c1, c2 = st.columns(2)

    with c1:
        default_start_idx = 0
        if is_jain:
            for idx, label in enumerate(loc_labels):
                if "OUT_GATE_MAIN" in label:
                    default_start_idx = idx
                    break
        start_label = st.selectbox(
            "Start Location (Origin):",
            options=loc_labels,
            index=default_start_idx if default_start_idx < len(loc_labels) else 0,
            key="nav_start_loc_select",
        )
        source_id = location_options[start_label]

    with c2:
        if matched_dest_id:
            dest_id = matched_dest_id
            st.markdown(f"<div style='font-size: 12px; color: #35D99A; margin-top: 28px;'><b>Selected Target:</b> {matched_dest_id}</div>", unsafe_allow_html=True)
        else:
            default_dest_idx = min(len(loc_labels) - 1, 13)
            if is_jain:
                for idx, label in enumerate(loc_labels):
                    if "FET_4F_HPC_CLUSTER" in label:
                        default_dest_idx = idx
                        break
            dest_label = st.selectbox(
                "Destination Location:",
                options=loc_labels,
                index=default_dest_idx,
                key="nav_dest_loc_select",
            )
            dest_id = location_options[dest_label]

    opt_col1, opt_col2, opt_col3 = st.columns(3)

    with opt_col1:
        algorithm = st.selectbox(
            "Routing Algorithm:",
            options=["Dijkstra's Algorithm", "Breadth-First Search (BFS)"],
            index=0,
            help="Dijkstra optimizes continuous metrics like distance and time. BFS minimizes the total number of transitions.",
        )
        algo_key = "dijkstra" if "Dijkstra" in algorithm else "bfs"

    with opt_col2:
        optimization_metric = st.selectbox(
            "Optimization Goal:",
            options=["Shortest Distance", "Fastest Travel Time"],
            index=0,
            disabled=(algo_key == "bfs"),
            help="Select whether Dijkstra minimizes total meters or estimated transit seconds.",
        )
        opt_key = "time" if "Time" in optimization_metric else "distance"

    with opt_col3:
        wheelchair_mode = st.checkbox(
            "♿ Wheelchair Accessible Only",
            value=True,
            help="Enforces step-free routing. Automatically avoids staircases and routes exclusively through ramps and elevators.",
        )

    calculate_btn = st.button("🚀 Calculate Accessible Route", type="primary", width="stretch")

st.markdown("---")

# --- CALCULATION AND DISPLAY ---
if calculate_btn:
    if source_id == dest_id:
        st.warning("⚠️ Starting location and destination are identical. Distance: 0 meters.")
    else:
        with st.spinner("Computing optimal step-free path..."):
            route_result = route_finder.find_route(
                source=source_id,
                destination=dest_id,
                algorithm=algo_key,
                optimize_for=opt_key,
                wheelchair_accessible=wheelchair_mode,
            )

        if not route_result.success:
            st.error(f"❌ Route Calculation Failed: {route_result.error_message}")
            if wheelchair_mode:
                st.info(
                    "💡 Tip: If an elevator or access ramp is currently unavailable or blocked, "
                    "a strictly step-free route may be impossible. Check Obstacle Reports or uncheck wheelchair restriction to view emergency stairs."
                )
        else:
            acc_eval = acc_engine.evaluate_route_accessibility(route_result)
            start_info = cmap.get_location(source_id) or {}
            dest_info = cmap.get_location(dest_id) or {}

            floors_visited = []
            for nid in route_result.path:
                fl = int((cmap.get_location(nid) or {}).get("floor", 0))
                if not floors_visited or floors_visited[-1] != fl:
                    floors_visited.append(fl)
            floors_crossed = sum(1 for s in route_result.steps if s.from_floor != s.to_floor)
            elevators_used = sum(1 for s in route_result.steps if s.has_elevator)
            ramps_used = sum(1 for s in route_result.steps if s.has_ramp)
            stairs_used = sum(1 for s in route_result.steps if s.has_stairs)

            active_obs_list = obs_manager.get_active_obstacles()
            if active_obs_list:
                st.info(
                    f"🛡️ **Obstacle-Aware Routing Active:** {len(active_obs_list)} verified blockage(s) "
                    "currently excluded from route calculation to maintain safe traversal."
                )

            st.success(
                f"Optimal route computed via **{algorithm}** from **{start_info.get('name', source_id)}** "
                f"to **{dest_info.get('name', dest_id)}**."
            )

            # --- ROUTE SUMMARY METRICS (5-COL CARDS) ---
            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                st.metric("Total Distance", f"{route_result.total_distance:.1f} m")
            with m2:
                mins = int(route_result.total_time // 60)
                secs = int(route_result.total_time % 60)
                time_str = f"~{mins}m {secs}s" if mins > 0 else f"~{secs}s"
                st.metric("Est. Travel Time (Estimate)", time_str)
            with m3:
                st.metric("Route Segments", f"{route_result.edge_count} Steps")
            with m4:
                st.metric("Accessibility Status", acc_eval.display_classification or acc_eval.overall_classification)
            with m5:
                st.metric("Heuristic Score", f"{acc_eval.accessibility_score}/100")

            # Infrastructure & Transition Breakdown
            st.markdown(
                f"""
                <div class="ui-card" style="padding: 12px 18px; margin-top: 10px;">
                    <div style="display: flex; flex-wrap: wrap; gap: 18px; font-size: 0.85rem; color: #F8FAFC;">
                        <span>🏢 <b>Floors Crossed:</b> {floors_crossed} transition(s)</span>
                        <span>🛗 <b>Elevators Used:</b> {elevators_used}</span>
                        <span>♿ <b>Ramps Used:</b> {ramps_used}</span>
                        <span>🪜 <b>Stairs Encountered:</b> {stairs_used}</span>
                        <span>⛔ <b>Blocked Sections:</b> {acc_eval.num_blocked_connections}</span>
                        <span>⚪ <b>Unverified Sections:</b> {acc_eval.num_unknown_connections}</span>
                        <span>🔎 <b>Dataset Verification:</b> <code>{acc_eval.verification_status}</code></span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Warnings display with full contextual explanation & alternative check
            if acc_eval.warnings:
                for w in acc_eval.warnings:
                    st.warning(f"⚠️ {w}")

                if any("assistance" in w.lower() for w in acc_eval.warnings):
                    alt_check = route_finder.find_alternative_routes(
                        source=source_id,
                        destination=dest_id,
                        max_alternatives=2,
                        optimize_for=opt_key,
                        wheelchair_accessible=wheelchair_mode,
                    )
                    no_assist_alt = any(
                        acc_engine.evaluate_route_accessibility(a).overall_classification == "Fully Accessible"
                        for a in alt_check
                    )
                    if not no_assist_alt:
                        st.caption(
                            "ℹ️ **Alternative Availability Note:** This route was selected because all wheelchair step-free "
                            "entrances from the main campus quadrangle traverse the West Access Ramp (≥ 35 m continuous run)."
                        )
                    else:
                        st.caption(
                            "💡 **Alternative Availability Note:** A shorter ramp-free alternative route is available in the Alternative Routes panel below."
                        )

            # Infrastructure highlights chips
            feat_badges = []
            if acc_eval.has_elevator:
                feat_badges.append('<span class="hero-chip">🛗 Elevator Transition Included</span>')
            if acc_eval.has_ramp:
                feat_badges.append('<span class="hero-chip">♿ Access Ramp Included</span>')
            if not acc_eval.has_elevator and not acc_eval.has_ramp:
                feat_badges.append('<span class="hero-chip">🚶 Flat Ground Corridor Walkway</span>')

            st.markdown(
                f"<div style='margin: 12px 0 18px 0;'><b>Infrastructure Highlights:</b> {' '.join(feat_badges)}</div>",
                unsafe_allow_html=True,
            )

            # --- TURN-BY-TURN GUIDANCE ---
            st.markdown("### 📋 Step-by-Step Navigation Sequence")

            for step in route_result.steps:
                icon = "🚶"
                badge = "Corridor"
                if step.has_elevator:
                    icon = "🛗"
                    badge = "Elevator Hub"
                elif step.has_stairs:
                    icon = "🪜"
                    badge = "Stairway (Inaccessible)"
                elif step.has_ramp:
                    icon = "♿"
                    badge = "Access Ramp"

                mins_s = int(step.estimated_time // 60)
                secs_s = int(step.estimated_time % 60)
                t_str = f"{mins_s}m {secs_s}s" if mins_s > 0 else f"{secs_s}s"

                fl_from = "Outdoor" if step.from_floor == -1 else f"Floor {step.from_floor}"
                fl_to = "Outdoor" if step.to_floor == -1 else f"Floor {step.to_floor}"
                fl_note = f"{fl_from} ➔ {fl_to}" if step.from_floor != step.to_floor else f"{fl_from} (Same Level)"
                acc_note = "Step-Free" if step.wheelchair_accessible else "Stairs / Restricted"

                st.markdown(
                    f"""
                    <div class="step-box">
                        <div class="step-header">{icon} Step {step.step_number}: {step.from_name} ➔ {step.to_name}</div>
                        <div class="step-instruction">{step.instruction}</div>
                        <div class="step-meta">
                            Segment: <b>{step.distance:.1f} m</b> · Est. Transit: <b>~{t_str}</b> ·
                            Link Type: <b>{badge}</b> · Level: <b>{fl_note}</b> · Access: <b>{acc_note}</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # --- ALTERNATIVE ROUTES ---
            alt_routes = route_finder.find_alternative_routes(
                source=source_id,
                destination=dest_id,
                max_alternatives=2,
                optimize_for=opt_key,
                wheelchair_accessible=wheelchair_mode,
            )

            if alt_routes:
                with st.expander(f"🔄 View Distinct Alternative Routes ({len(alt_routes)} Available)"):
                    for idx, alt in enumerate(alt_routes, 1):
                        alt_names = [cmap.get_location(nid)["name"] for nid in alt.path]
                        st.markdown(
                            f"""
                            <div class="ui-card" style="margin-bottom: 8px; padding: 12px 16px;">
                                <div style="font-weight: 700; color: #35D99A; margin-bottom: 4px;">Alternative Route #{idx}</div>
                                <div style="color: #F8FAFC; font-size: 0.9rem;">{' ➔ '.join(alt_names)}</div>
                                <div style="color: #9CAFA5; font-size: 0.8rem; margin-top: 4px;">Distance: {alt.total_distance:.1f} m · Est. Time: {alt.total_time:.1f} s</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
