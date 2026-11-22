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
from modules.destination_search import (
    get_search_suggestions,
    group_destinations_by_building_and_floor,
    search_destinations,
)
from modules.i18n import SUPPORTED_LANGUAGES, t, translate_instruction
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
    get_current_user,
    render_kpi_card,
)

# Apply unified design system and retrieve singleton services
apply_custom_theme()
services = get_app_services()

benchmark_cmap = services["campus_map"]
benchmark_rf = services["route_finder"]
acc_engine = services["accessibility_engine"]
obs_manager = services["obstacle_manager"]
db_manager = services.get("db_manager")

current_user = get_current_user()
current_user_id = current_user.get("user_id") if current_user else "guest"
user_role = current_user.get("role") if current_user else "Guest"

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

# Language & Accessibility Preferences (Phase 18)
col_pref1, col_pref2, col_pref3, col_pref4 = st.columns([1.3, 0.85, 0.85, 1.1])
with col_pref1:
    selected_lang = st.selectbox(
        "🌐 Language / ಭಾಷೆ / भाषा:",
        options=["en", "kn", "hi"],
        format_func=lambda c: SUPPORTED_LANGUAGES.get(c, c),
        index=0,
        key="campus_active_lang",
    )
with col_pref2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    pref_high_contrast = st.checkbox(
        "👁️ High Contrast",
        value=False,
        key="pref_high_contrast",
        help="Enhances UI contrast with pure black backgrounds and high-visibility borders.",
    )
with col_pref3:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    pref_reduced_motion = st.checkbox(
        "⚡ Reduced Motion",
        value=False,
        key="pref_reduced_motion",
        help="Disables smooth transitions and motion animations for cognitive accessibility.",
    )
with col_pref4:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🗺️ 2D Floor Plan", use_container_width=True, help="Switch to 2D Architectural Floor Plan"):
        st.switch_page("pages/campus_map.py")

if pref_high_contrast:
    st.markdown(
        """
        <style>
        .ui-card, .hero-banner, div[data-testid="stExpander"] {
            background-color: #000000 !important;
            border: 2px solid #FFFF00 !important;
            color: #FFFFFF !important;
        }
        span, p, div, label {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }
        .stButton>button {
            border: 2px solid #00FFFF !important;
            color: #00FFFF !important;
            background: #000000 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

if pref_reduced_motion:
    st.markdown(
        """
        <style>
        * {
            animation-duration: 0.001ms !important;
            transition-duration: 0.001ms !important;
        }
        </style>
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
col_viewport, col_controls = st.columns([2.8, 1.2], gap="medium")

with col_controls:
    st.markdown('<div class="ui-card">', unsafe_allow_html=True)
    st.markdown("#### 🧭 3D Route Planning")

    # Search & Filter Enhancements for Location Selection
    start_label = st.selectbox(
        "Origin Location:",
        options=loc_labels,
        index=default_start_idx if default_start_idx < len(loc_labels) else 0,
        key="3d_route_start",
        help="Choose starting campus facility.",
    )
    start_id = loc_options[start_label]

    # Quick Destination Suggestions Pills
    st.markdown("<div style='font-size: 11px; color: #9CAFA5; margin-bottom: 4px;'><b>Quick Destination Suggestions:</b></div>", unsafe_allow_html=True)
    pill_cols = st.columns(4)
    quick_keywords = ["HPC Lab", "Library", "Dean", "Robotics"] if is_jain_twin else ["Classroom", "Lab", "Restroom", "Elevator"]
    for i, kw in enumerate(quick_keywords):
        with pill_cols[i]:
            if st.button(kw, key=f"3d_pill_{kw}", use_container_width=True):
                st.session_state["3d_dest_search_input"] = kw
                st.rerun()

    # Destination Search with Keyword Intelligence
    dest_search_query = st.text_input(
        "🔍 Search Destination (Lab, Room, Dept, Keyword):",
        value=st.session_state.get("3d_dest_search_input", ""),
        placeholder="e.g. AI Lab, HPC, Library, Robotics, Seminar, Mechanical...",
        key="3d_dest_search_input",
        help="Search 79 campus locations by room name, department, category, abbreviation, or keywords.",
    )

    matched_dest_id = None
    if dest_search_query.strip() and is_jain_twin:
        search_matches = search_destinations(dest_search_query, active_cmap, limit=15)
        if search_matches:
            st.caption(f"✨ Found {len(search_matches)} match(es) for '{dest_search_query}'")
            search_options = {
                f"[{'Outdoor' if m.floor == -1 else f'Floor {m.floor}'}] {m.name} ({m.location_id}) — {m.category.title()}": m.location_id
                for m in search_matches
            }
            matched_labels = list(search_options.keys())
            selected_match_label = st.selectbox(
                "Select Matched Facility:",
                options=matched_labels,
                index=0,
                key="3d_matched_dest_select",
            )
            matched_dest_id = search_options[selected_match_label]
        else:
            st.caption("ℹ️ No exact keyword matches found. Browse via floor filter below.")
            suggestions = get_search_suggestions(dest_search_query, active_cmap)
            if suggestions:
                st.caption("💡 Suggestions: " + ", ".join(suggestions[:5]))

    if matched_dest_id:
        dest_id = matched_dest_id
    else:
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

    # Phase 18: Bookmark Destination & Saved Places
    if current_user and db_manager and hasattr(db_manager, "save_place"):
        c_bk1, c_bk2 = st.columns(2)
        with c_bk1:
            if st.button("⭐ Bookmark Place", use_container_width=True, help="Bookmark destination to your saved places profile"):
                db_manager.save_place(current_user, dest_id, dest_label)
                st.success("Destination saved to your profile!")
        with c_bk2:
            if st.button("❤️ Save Route", use_container_width=True, help="Save this route to your favourite routes"):
                db_manager.save_favourite_route(current_user, start_id, dest_id, "wheelchair" if wheelchair_only else "standard", f"{start_id} ➔ {dest_id}")
                st.success("Route saved to favourite routes!")

        saved_places = db_manager.get_saved_places(current_user) if hasattr(db_manager, "get_saved_places") else []
        if saved_places:
            with st.expander(f"⭐ Saved Places ({len(saved_places)})", expanded=False):
                for p in saved_places:
                    p_loc = p.get("location_id")
                    p_name = p.get("custom_name") or p_loc
                    st.markdown(f"<b>{p_name}</b> (`{p_loc}`)", unsafe_allow_html=True)
                    sp_col1, sp_col2 = st.columns(2)
                    with sp_col1:
                        if st.button("🎯 Destination", key=f"btn_set_dest_{p.get('saved_id')}", use_container_width=True):
                            st.session_state["3d_matched_dest_select"] = p_loc
                            st.rerun()
                    with sp_col2:
                        if st.button("🗑️ Remove", key=f"btn_del_saved_{p.get('saved_id')}", use_container_width=True):
                            db_manager.remove_saved_place(current_user, p_loc)
                            st.rerun()

        fav_routes = db_manager.get_favourite_routes(current_user) if hasattr(db_manager, "get_favourite_routes") else []
        if fav_routes:
            with st.expander(f"❤️ Favourite Routes ({len(fav_routes)})", expanded=False):
                for r in fav_routes:
                    r_lbl = r.get("custom_label") or f"{r.get('origin_id')} ➔ {r.get('destination_id')}"
                    st.markdown(f"<b>{r_lbl}</b> ({r.get('route_mode', 'standard').title()})", unsafe_allow_html=True)
                    rf_col1, rf_col2 = st.columns(2)
                    with rf_col1:
                        if st.button("🚀 Load Route", key=f"btn_load_route_{r.get('route_id')}", use_container_width=True):
                            nav_session.start_preview(
                                origin_id=r.get("origin_id"),
                                destination_id=r.get("destination_id"),
                                campus_map=active_cmap,
                                route_finder=active_rf,
                                algorithm=algo_choice.lower(),
                                wheelchair_mode=(r.get("route_mode") == "wheelchair"),
                            )
                            st.rerun()
                    with rf_col2:
                        if st.button("🗑️ Remove", key=f"btn_del_route_{r.get('route_id')}", use_container_width=True):
                            db_manager.remove_favourite_route(current_user, r.get("route_id"))
                            st.rerun()

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
            nav_session.user_id = current_user_id
            nav_session.start_navigation(db_manager=db_manager)
            st.rerun()
    elif nav_session.state == NavigationState.NAVIGATING:
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("⏸️ Pause", use_container_width=True, key="btn_pause_nav"):
                nav_session.pause_navigation()
                nav_session.persist_session_state(db_manager)
                st.rerun()
        with c2:
            if st.button("⏭️ Next Step", use_container_width=True, key="btn_step_nav"):
                nav_session.step_forward(active_cmap, db_manager=db_manager)
                st.rerun()
        with c3:
            if st.button("⏹️ Cancel", use_container_width=True, key="btn_cancel_nav"):
                nav_session.cancel_navigation(db_manager=db_manager)
                st.rerun()
    elif nav_session.state in (NavigationState.PAUSED, NavigationState.FLOOR_TRANSITION):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("▶️ Resume", type="primary", use_container_width=True, key="btn_resume_nav"):
                nav_session.resume_navigation()
                nav_session.persist_session_state(db_manager)
                st.rerun()
        with c2:
            if st.button("⏭️ Next Step", use_container_width=True, key="btn_step_nav_p"):
                nav_session.step_forward(active_cmap, db_manager=db_manager)
                st.rerun()
        with c3:
            if st.button("🔄 Restart", use_container_width=True, key="btn_restart_nav"):
                nav_session.restart_navigation()
                nav_session.persist_session_state(db_manager)
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
    dept = str(inspect_loc.get("department", "FET Complex"))
    is_step_free = bool(inspect_loc.get("wheelchair_accessible", True))

    floor_display = "Outdoor Grounds" if floor_num == -1 else f"Floor {floor_num} ({FLOOR_NAMES.get(floor_num, '')})"

    verif_status = inspect_loc.get("verification_status", "IMAGE_DERIVED")
    badge_colors = {
        "VERIFIED": ("#10B981", "rgba(16, 185, 129, 0.18)"),
        "IMAGE_DERIVED": ("#38BDF8", "rgba(56, 189, 248, 0.18)"),
        "APPROXIMATE": ("#F5B942", "rgba(245, 185, 66, 0.18)"),
        "UNVERIFIED": ("#94A3B8", "rgba(148, 163, 184, 0.18)"),
    }
    badge_fg, badge_bg = badge_colors.get(verif_status, ("#94A3B8", "rgba(148, 163, 184, 0.18)"))

    verif_source = inspect_loc.get("verification_source", "Floor Plan Layout Analysis")
    last_verif = inspect_loc.get("last_verified", "2026-11-22")
    conf_level = inspect_loc.get("confidence_level", "Medium")
    verif_notes = inspect_loc.get("verification_notes", "Derived from reference imagery.")
    search_keys = inspect_loc.get("search_keywords", inspect_loc.get("aliases", []))
    keywords_str = ", ".join(search_keys) if search_keys else "None"

    st.markdown(
        f"""
        <div style="font-size: 13px; line-height: 1.6; margin-top: 6px;">
            <div><b>Facility:</b> <span style="color: {ACCENT_GREEN};">{inspect_loc.get('name', selected_inspect_id)}</span></div>
            <div><b>Building:</b> {building}</div>
            <div><b>Building Level:</b> {floor_display}</div>
            <div><b>Category:</b> {category}</div>
            <div><b>Department:</b> {dept}</div>
            <div><b>Accessibility:</b> <span style="color: {'#35D99A' if is_step_free else '#F5B942'};">
                {'✅ Step-Free Accessible' if is_step_free else '⚠️ Stair Access Only'}
            </span></div>
        </div>

        <div style="margin-top: 10px; padding: 10px; background: rgba(0,0,0,0.25); border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 11px; font-weight: 700; color: #9CAFA5; text-transform: uppercase; letter-spacing: 0.5px;">Data Reliability</span>
                <span style="background: {badge_bg}; color: {badge_fg}; border: 1px solid {badge_fg}; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 800;">
                    {verif_status}
                </span>
            </div>
            <div style="font-size: 11px; color: #9CAFA5; line-height: 1.5;">
                <div><b>Source:</b> {verif_source}</div>
                <div><b>Confidence:</b> {conf_level} &nbsp;|&nbsp; <b>Verified:</b> {last_verif}</div>
                <div><b>Keywords / Aliases:</b> {keywords_str}</div>
                <div style="margin-top: 4px; font-style: italic; color: #CBD5E1;">"{verif_notes}"</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1-Click Quick Actions for Inspected Facility
    c_fi1, c_fi2 = st.columns(2)
    with c_fi1:
        if st.button("🚩 Set as Start", key="3d_btn_inspect_start", use_container_width=True):
            st.session_state["3d_route_start"] = inspect_label
            st.rerun()
    with c_fi2:
        if st.button("🎯 Set as Dest", key="3d_btn_inspect_dest", use_container_width=True):
            st.session_state["3d_route_dest"] = inspect_label
            if "3d_dest_search_input" in st.session_state:
                st.session_state["3d_dest_search_input"] = ""
            st.rerun()

    if st.button("🗺️ Switch to 2D Architectural Map", key="btn_switch_2d_from_3d", use_container_width=True):
        st.switch_page("pages/campus_map.py")

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
            h_deg = step.get("heading_deg")
            c_dir = step.get("cardinal_direction")
            if h_deg is None and step.get("from_id") and step.get("to_id"):
                u_loc = active_cmap.get_location(step["from_id"]) or {}
                v_loc = active_cmap.get_location(step["to_id"]) or {}
                if u_loc and v_loc:
                    from modules.navigation_instructions import compute_bearing_and_cardinal
                    h_deg, c_dir = compute_bearing_and_cardinal(u_loc, v_loc)

            heading_info = ""
            if h_deg is not None and c_dir and c_dir != "Stationary":
                heading_info = f" &nbsp;|&nbsp; 🧭 <b>Heading:</b> {c_dir} ({h_deg:.0f}°)"
            elif c_dir and c_dir != "Stationary":
                heading_info = f" &nbsp;|&nbsp; 🧭 <b>Heading:</b> {c_dir}"

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
                            Wheelchair Passable: <b>{'Yes' if step['wheelchair_accessible'] else 'No (Stairs)'}</b>{heading_info}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div style="font-size: 11px; color: #9CAFA5; margin-top: 10px; padding: 6px 12px; background: rgba(13, 31, 24, 0.4); border-left: 3px solid #38BDF8; border-radius: 4px;">
                🧭 <b>Directional & Heading Disclosure:</b> Compass bearings (0°–360° clockwise from campus grid North) and cardinal orientations are calculated from schematic 3D coordinates relative to campus grid North (-Z axis) for spatial reference and assistive wayfinding.
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

# --- RECENT NAVIGATION HISTORY & USER STATS ---
if db_manager and hasattr(db_manager, "get_navigation_history"):
    st.markdown("---")
    st.markdown("### 📜 Recent Navigation History & Wayfinding Telemetry")

    try:
        hist_records = db_manager.get_navigation_history(user_id=current_user_id, limit=5)
    except Exception:
        hist_records = []

    try:
        stats = db_manager.get_navigation_stats(user_id=current_user_id)
    except Exception:
        stats = {
            "total_sessions": 0,
            "completed_sessions": 0,
            "completion_rate": 0.0,
            "total_distance_navigated": 0.0,
            "average_duration_seconds": 0.0,
        }

    h1, h2, h3, h4 = st.columns(4)
    with h1:
        render_kpi_card("Total Journeys", f"{stats['total_sessions']} Sessions", "Logged in navigation history", PRIMARY_GREEN)
    with h2:
        render_kpi_card("Completed Routes", f"{stats['completed_sessions']} Arrived", f"{stats['completion_rate']:.0f}% completion rate", ACCENT_GREEN)
    with h3:
        render_kpi_card("Total Distance Navigated", f"{stats['total_distance_navigated']:.1f} m", "Physical distance traversed", INFO)
    with h4:
        avg_dur = stats['average_duration_seconds']
        render_kpi_card("Avg Transit Time", f"{avg_dur:.0f} s", f"~{(avg_dur/60):.1f} min per journey", WHITE)

    if hist_records:
        with st.expander("🔍 View Recent Wayfinding Log", expanded=False):
            for rec in hist_records:
                status_val = rec.get("status") or rec.get("state") or "COMPLETED"
                stat_color = "#10B981" if status_val == "ARRIVED" else ("#F87171" if status_val == "CANCELLED" else ("#F5B942" if status_val == "REROUTED" else ("#35D99A" if status_val == "NAVIGATING" else "#9CAFA5")))
                orig_disp = rec.get("origin_name") or rec.get("origin_id", "Origin")
                dest_disp = rec.get("destination_name") or rec.get("destination_id", "Destination")
                tot_dist = float(rec.get("total_distance") or 0.0)
                tot_time = float(rec.get("total_time") or 0.0)
                algo_str = str(rec.get("algorithm") or "dijkstra").upper()
                wc_str = "Yes" if rec.get("wheelchair_mode") else "Standard"
                reroute_str = "Yes" if rec.get("is_rerouted") else "No"
                created_str = str(rec.get("created_at") or "")[:19]
                st.markdown(
                    f"""
                    <div style="background: rgba(13, 31, 24, 0.6); border: 1px solid rgba(156, 175, 165, 0.2); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 700; color: #F8FAFC; font-size: 13px;">
                                🚀 {orig_disp} ➔ {dest_disp}
                            </span>
                            <span style="background: rgba(255,255,255,0.06); color: {stat_color}; border: 1px solid {stat_color}; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 4px;">
                                {status_val}
                            </span>
                        </div>
                        <div style="font-size: 11px; color: #9CAFA5; margin-top: 6px; display: flex; flex-wrap: wrap; gap: 16px;">
                            <span>Session: <code>{rec.get('session_id', 'N/A')}</code></span>
                            <span>Distance: <b>{tot_dist:.1f} m</b></span>
                            <span>Time: <b>{tot_time:.0f} s</b></span>
                            <span>Algorithm: <b>{algo_str}</b></span>
                            <span>Wheelchair: <b>{wc_str}</b></span>
                            <span>Rerouted: <b>{reroute_str}</b></span>
                            <span>Logged: <b>{created_str}</b></span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.caption("No historical navigation sessions recorded yet. Start a navigation session to log wayfinding telemetry.")

# --- ADMINISTRATIVE DATA QUALITY & VERIFICATION GOVERNANCE ---
if is_jain_twin and db_manager:
    st.markdown("---")
    with st.expander("🛡️ Administrative Campus Data Quality & Verification Governance", expanded=False):
        st.markdown("##### 📊 Campus Graph Verification Distribution")
        st.caption("Authoritative classification of 79 locations and 106 pathways across the JAIN Global Campus & FET complex.")

        # Compute live distribution from active_cmap
        loc_counts = {"VERIFIED": 0, "IMAGE_DERIVED": 0, "APPROXIMATE": 0, "UNVERIFIED": 0}
        for loc in active_cmap.get_all_locations():
            stt = loc.get("verification_status", "IMAGE_DERIVED")
            loc_counts[stt] = loc_counts.get(stt, 0) + 1

        path_counts = {"VERIFIED": 0, "IMAGE_DERIVED": 0, "APPROXIMATE": 0, "UNVERIFIED": 0}
        for u, v, data in active_cmap.graph.edges(data=True):
            pstt = data.get("verification_status", "IMAGE_DERIVED")
            path_counts[pstt] = path_counts.get(pstt, 0) + 1

        q1, q2 = st.columns(2)
        with q1:
            st.markdown(
                f"""
                <div style="background: rgba(13, 31, 24, 0.7); border: 1px solid rgba(53, 217, 154, 0.2); border-radius: 8px; padding: 12px 16px;">
                    <div style="font-weight: 700; font-size: 13px; color: #35D99A; margin-bottom: 8px;">📍 Campus Locations (Total: {len(active_cmap.get_all_locations())})</div>
                    <div style="font-size: 12px; line-height: 1.8;">
                        <div>🟢 <b>VERIFIED:</b> {loc_counts['VERIFIED']} location(s) (Physical Entrance audited)</div>
                        <div>🔵 <b>IMAGE_DERIVED:</b> {loc_counts['IMAGE_DERIVED']} location(s) (Derived from official floor plans)</div>
                        <div>🟡 <b>APPROXIMATE:</b> {loc_counts['APPROXIMATE']} location(s)</div>
                        <div>⚪ <b>UNVERIFIED:</b> {loc_counts['UNVERIFIED']} location(s)</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with q2:
            st.markdown(
                f"""
                <div style="background: rgba(13, 31, 24, 0.7); border: 1px solid rgba(53, 217, 154, 0.2); border-radius: 8px; padding: 12px 16px;">
                    <div style="font-weight: 700; font-size: 13px; color: #38BDF8; margin-bottom: 8px;">🛤️ Campus Pathways (Total: {len(active_cmap.graph.edges())})</div>
                    <div style="font-size: 12px; line-height: 1.8;">
                        <div>🟢 <b>VERIFIED:</b> {path_counts['VERIFIED']} pathway(s)</div>
                        <div>🔵 <b>IMAGE_DERIVED:</b> {path_counts['IMAGE_DERIVED']} pathway(s) (Indoor corridors & vertical shafts)</div>
                        <div>🟡 <b>APPROXIMATE:</b> {path_counts['APPROXIMATE']} pathway(s) (Outdoor estimated perimeter trails)</div>
                        <div>⚪ <b>UNVERIFIED:</b> {path_counts['UNVERIFIED']} pathway(s)</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("##### ✍️ Update Entity Verification Status (Administrator Only)")
        is_admin = (user_role == "Administrator")
        if not is_admin:
            st.info("🔒 Status updating requires **Administrator** role privileges. Log in with an administrator account to submit verification records.")
        
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            entity_type_choice = st.selectbox("Entity Classification:", ["Location", "Pathway"], key="admin_entity_type")
            if entity_type_choice == "Location":
                target_entity_id = st.selectbox("Select Target Location:", options=[loc['id'] for loc in all_locs], key="admin_target_loc")
            else:
                conn_options = [f"{u} ➔ {v}" for u, v in active_cmap.graph.edges()]
                target_conn_str = st.selectbox("Select Target Pathway:", options=conn_options, key="admin_target_path")
                target_entity_id = target_conn_str

        with col_u2:
            new_status_choice = st.selectbox("New Verification Status:", ["VERIFIED", "IMAGE_DERIVED", "APPROXIMATE", "UNVERIFIED"], key="admin_new_status")
            verif_source_input = st.text_input("Verification Source:", value="On-site physical validation", key="admin_verif_source")

        verif_notes_input = st.text_area("Audit Notes & Justification:", value="Verified physical accessibility and dimensions during campus survey.", key="admin_verif_notes")

        if st.button("💾 Submit Verification Update", disabled=not is_admin, key="btn_submit_verif"):
            success, msg = db_manager.update_campus_verification(
                entity_type=entity_type_choice.lower(),
                entity_id=target_entity_id,
                status=new_status_choice,
                source=verif_source_input,
                notes=verif_notes_input,
                user_role=user_role,
                user_id=current_user_id,
            )
            if success:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")

        st.markdown("---")
        st.markdown("##### 📬 Review Campus User Feedback Submissions")
        pending_feedbacks = db_manager.get_feedback_list("Pending") if hasattr(db_manager, "get_feedback_list") else []
        if not pending_feedbacks:
            st.caption("No pending user feedback submissions awaiting administrative review.")
        else:
            st.info(f"📋 {len(pending_feedbacks)} pending user feedback submission(s) require review.")
            for fb in pending_feedbacks:
                st.markdown(
                    f"""
                    <div style="background: rgba(0,0,0,0.3); border-left: 4px solid #38BDF8; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
                        <b>ID:</b> {fb.get('feedback_id')} &nbsp;|&nbsp; <b>Category:</b> {fb.get('feedback_type')} &nbsp;|&nbsp; <b>Target:</b> {fb.get('target_id') or 'General'}<br>
                        <b>Submitted At:</b> {fb.get('submitted_at')}<br>
                        <div style="margin-top: 4px; color: #E2E8F0;"><i>"{fb.get('details')}"</i></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if is_admin or user_role == "Field Staff":
                    fb_act_col1, fb_act_col2 = st.columns([1, 1])
                    with fb_act_col1:
                        if st.button("✅ Mark Reviewed", key=f"btn_rev_{fb.get('feedback_id')}"):
                            db_manager.review_feedback(fb.get('feedback_id'), current_user_id, "Reviewed", "Verified by administrator.")
                            st.rerun()
                    with fb_act_col2:
                        if st.button("❌ Dismiss", key=f"btn_dis_{fb.get('feedback_id')}"):
                            db_manager.review_feedback(fb.get('feedback_id'), current_user_id, "Dismissed", "Deemed not applicable.")
                            st.rerun()

    # Phase 18: Campus User Feedback & Corrections Submission Form
    with st.expander("💬 Submit Campus Feedback & Correction Notice", expanded=False):
        st.markdown("##### 📝 Report Campus Inaccuracies or Suggest Corrections")
        st.caption("Submit reports regarding room placement, inaccessible pathways, or routing improvements for administrative review.")
        
        fb_c1, fb_c2 = st.columns(2)
        with fb_c1:
            fb_type_map = {
                "incorrect_location": "📍 Incorrect Room / Facility Information",
                "blocked_path": "🚫 Blocked / Obstructed Pathway",
                "missing_accessible_route": "♿ Missing Wheelchair / Accessible Route",
                "instruction_error": "🧭 Navigation Instruction Error",
                "general": "💡 General Suggestion / Feedback",
            }
            fb_type = st.selectbox(
                "Feedback Category:",
                options=list(fb_type_map.keys()),
                format_func=lambda k: fb_type_map[k],
                key="fb_user_type",
            )
        with fb_c2:
            fb_target = st.selectbox(
                "Target Facility (Optional):",
                options=["None / General Campus"] + [loc['id'] for loc in all_locs],
                key="fb_user_target",
            )
        
        fb_details = st.text_area(
            "Feedback Details:",
            placeholder="Describe the discrepancy, missing ramp, blocked door, or recommended correction...",
            key="fb_user_details",
        )
        
        if st.button("📤 Submit Feedback", type="primary", key="btn_submit_user_feedback"):
            if not fb_details.strip():
                st.warning("Please provide descriptive feedback details before submitting.")
            else:
                target_val = None if fb_target == "None / General Campus" else fb_target
                f_id = db_manager.submit_feedback(
                    user_id=current_user_id if current_user else None,
                    feedback_type=fb_type,
                    details=fb_details.strip(),
                    target_id=target_val,
                )
                st.success(f"✅ Thank you! Feedback report '{f_id}' successfully submitted for administrative review.")
