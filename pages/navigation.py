"""Navigation Page - Route planning, turn-by-turn guidance, and accessibility evaluation."""

from __future__ import annotations

import streamlit as st

from modules.ui_theme import apply_custom_theme, get_app_services

apply_custom_theme()
services = get_app_services()

cmap = services["campus_map"]
route_finder = services["route_finder"]
acc_engine = services["accessibility_engine"]

st.title("🧭 Accessible Route Planner")
st.write(
    "Calculate optimal, step-free navigation routes across campus buildings, "
    "evaluating elevator availability, ramps, and real-time active obstacles."
)

locations = cmap.get_all_locations()
# Create options sorted by floor then name
location_options = {
    f"[{loc['id']}] {loc['name']} (Floor {loc['floor']})": loc["id"]
    for loc in sorted(locations, key=lambda x: (x["floor"], x["name"]))
}

# --- ROUTE INPUT FORM ---
with st.container():
    st.subheader("Route Configuration")
    c1, c2 = st.columns(2)

    with c1:
        start_label = st.selectbox(
            "Start Location (Origin):",
            options=list(location_options.keys()),
            index=0,  # Main Campus Entrance (LOC_01)
        )
        source_id = location_options[start_label]

    with c2:
        # Default destination: Faculty Office Suite (Floor 1) or Computer Science Lab
        dest_default_idx = min(len(location_options) - 1, 13)
        dest_label = st.selectbox(
            "Destination:",
            options=list(location_options.keys()),
            index=dest_default_idx,
        )
        dest_id = location_options[dest_label]

    opt_col1, opt_col2, opt_col3 = st.columns(3)

    with opt_col1:
        algorithm = st.selectbox(
            "Routing Algorithm:",
            options=["Dijkstra's Algorithm", "Breadth-First Search (BFS)"],
            index=0,
            help="Dijkstra optimizes continuous metrics like distance and time. BFS minimizes the number of transitions.",
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

    calculate_btn = st.button("🚀 Calculate Accessible Route", use_container_width=True)

st.markdown("---")

# --- CALCULATION AND DISPLAY ---
if calculate_btn:
    if source_id == dest_id:
        st.warning("Starting location and destination are identical. Distance: 0 meters.")
    else:
        with st.spinner("Computing optimal route..."):
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
                    "a strictly step-free route may be impossible. Check the Obstacle Reports page or uncheck wheelchair restriction to view emergency stairs."
                )
        else:
            # Perform accessibility assessment
            acc_eval = acc_engine.evaluate_route_accessibility(route_result)

            st.success(f"Route found successfully via **{algorithm}**!")

            # --- ROUTE SUMMARY METRICS ---
            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                st.metric("Total Distance", f"{route_result.total_distance:.1f} m")
            with m2:
                mins = int(route_result.total_time // 60)
                secs = int(route_result.total_time % 60)
                time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
                st.metric("Est. Travel Time", time_str)
            with m3:
                st.metric("Path Transitions", f"{route_result.edge_count} hops")
            with m4:
                st.metric("Classification", acc_eval.overall_classification)
            with m5:
                st.metric("Accessibility Score", f"{acc_eval.accessibility_score}/100")

            # Warnings display
            if acc_eval.warnings:
                for w in acc_eval.warnings:
                    st.warning(f"⚠️ {w}")

            # Infrastructure features
            feat_badges = []
            if acc_eval.has_elevator:
                feat_badges.append("🛗 Elevator Transition Included")
            if acc_eval.has_ramp:
                feat_badges.append("♿ Access Ramp Included")
            if not acc_eval.has_elevator and not acc_eval.has_ramp:
                feat_badges.append("🚶 Flat Ground/Corridor Walkway")

            st.markdown(
                f"<div style='margin-bottom: 14px;'><b>Infrastructure Highlights:</b> {' · '.join(feat_badges)}</div>",
                unsafe_allow_html=True,
            )

            # --- TURN-BY-TURN GUIDANCE ---
            st.subheader("📋 Turn-by-Turn Navigation Sequence")

            for step in route_result.steps:
                icon = "🚶"
                badge = "Corridor"
                if step.has_elevator:
                    icon = "🛗"
                    badge = "Elevator"
                elif step.has_stairs:
                    icon = "🪜"
                    badge = "Stairway (Inaccessible)"
                elif step.has_ramp:
                    icon = "♿"
                    badge = "Access Ramp"

                mins_s = int(step.estimated_time // 60)
                secs_s = int(step.estimated_time % 60)
                t_str = f"{mins_s}m {secs_s}s" if mins_s > 0 else f"{secs_s}s"

                st.markdown(
                    f"""
                    <div class="step-box">
                        <div class="step-header">{icon} Step {step.step_number}: {step.from_name} ➔ {step.to_name}</div>
                        <div class="step-instruction">{step.instruction}</div>
                        <div class="step-meta">Segment: {step.distance:.1f} m · Est. Time: {t_str} · Type: <b>{badge}</b></div>
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
                with st.expander(f"🔄 View Alternative Routes ({len(alt_routes)} available)"):
                    for idx, alt in enumerate(alt_routes, 1):
                        alt_names = [cmap.get_location(nid)["name"] for nid in alt.path]
                        st.markdown(
                            f"**Alternative {idx}:** {' ➔ '.join(alt_names)}  \n"
                            f"*Distance: {alt.total_distance:.1f} m · Est. Time: {alt.total_time:.1f} s*"
                        )
