"""Obstacle Reports Page - Review existing barrier reports, filter hazards, and inspect active disruptions."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.ui_theme import apply_custom_theme, get_app_services

apply_custom_theme()
services = get_app_services()

obs_manager = services["obstacle_manager"]
cmap = services["campus_map"]

st.title("⚠️ Obstacle & Hazard Reports")
st.write(
    "Central repository of campus accessibility obstructions, construction barricades, "
    "and pathway maintenance reports stored persistently via SQLite."
)

# Fetch stats and reports from SQLite
stats = obs_manager.get_obstacle_statistics()
all_reports = obs_manager.get_all_reports()

# --- TOP STATS ROW ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Filed Reports", stats["total_reports"])
with c2:
    st.metric("Pending Review", stats["status_counts"].get("Pending", 0))
with c3:
    st.metric(
        "Active & Verified Obstacles",
        stats["active_obstacles_count"],
        delta="- Affecting Routing" if stats["active_obstacles_count"] > 0 else "None",
        delta_color="inverse",
    )
with c4:
    st.metric("Resolved Issues", stats["status_counts"].get("Resolved", 0))

st.markdown("---")

# --- FILTERING CONTROLS ---
st.subheader("🔍 Filter Reports")
f_col1, f_col2, f_col3 = st.columns(3)

with f_col1:
    status_filter = st.selectbox(
        "Filter by Status:",
        options=["All Statuses", "Pending", "Verified", "Resolved", "Rejected"],
        index=0,
    )

with f_col2:
    severity_filter = st.selectbox(
        "Filter by Severity:",
        options=["All Severities", "Critical", "High", "Medium", "Low"],
        index=0,
    )

with f_col3:
    category_filter = st.selectbox(
        "Filter by Category:",
        options=["All Categories"] + list(obs_manager.ALLOWED_CATEGORIES),
        index=0,
    )

# Apply filters
filtered_reports = all_reports
if status_filter != "All Statuses":
    filtered_reports = [r for r in filtered_reports if r["status"] == status_filter]
if severity_filter != "All Severities":
    filtered_reports = [r for r in filtered_reports if r["severity"] == severity_filter]
if category_filter != "All Categories":
    filtered_reports = [r for r in filtered_reports if r["obstacle_category"] == category_filter]

st.markdown("---")

# --- REPORTS TABLE ---
st.subheader(f"📋 Incident Log ({len(filtered_reports)} matching reports)")

if not filtered_reports:
    st.info(
        "No obstacle reports match the selected filters. "
        "When campus barriers or maintenance issues are logged, they will appear here."
    )
else:
    table_data = []
    for r in filtered_reports:
        # Determine target display string
        if r["target_type"] == "pathway":
            src_name = cmap.get_location(r["source_location_id"])
            dst_name = cmap.get_location(r["destination_location_id"])
            s_str = src_name["name"] if src_name else r["source_location_id"]
            d_str = dst_name["name"] if dst_name else r["destination_location_id"]
            target_str = f"Pathway: {s_str} ↔ {d_str}"
        else:
            loc = cmap.get_location(r["location_id"])
            loc_str = loc["name"] if loc else r["location_id"]
            target_str = f"Location: {loc_str}"

        # Clean timestamp
        reported_ts = str(r["reported_at"])[:19].replace("T", " ")

        table_data.append(
            {
                "Report ID": r["report_id"],
                "Target Affected": target_str,
                "Category": r["obstacle_category"],
                "Severity": r["severity"],
                "Status": r["status"],
                "Reported At (UTC)": reported_ts,
                "Reporter": r["reporter_name"],
                "Description": r["description"],
                "Resolution Notes": r["resolution_notes"] or "None",
            }
        )

    df_reports = pd.DataFrame(table_data)
    st.dataframe(df_reports, use_container_width=True, hide_index=True)

# --- QUICK REPORT SUBMISSION ACCORDION ---
with st.expander("➕ Log a New Obstacle or Hazard Report"):
    st.write("File a field report regarding an accessibility obstacle, broken lift, or construction closure.")

    sub_c1, sub_c2 = st.columns(2)
    with sub_c1:
        rep_type = st.radio("Obstacle Target Type:", options=["Single Location", "Pathway Connection"], horizontal=True)
        rep_category = st.selectbox("Obstacle Category:", options=obs_manager.ALLOWED_CATEGORIES)
        rep_severity = st.selectbox("Severity Level:", options=obs_manager.ALLOWED_SEVERITIES, index=1)

    all_locs = sorted(cmap.get_all_locations(), key=lambda x: (x["floor"], x["name"]))
    loc_map = {f"[{loc['id']}] {loc['name']}": loc["id"] for loc in all_locs}

    with sub_c2:
        if rep_type == "Single Location":
            target_loc_label = st.selectbox("Affected Location:", options=list(loc_map.keys()))
            target_loc_id = loc_map[target_loc_label]
            target_src_id = None
            target_dst_id = None
        else:
            target_loc_id = None
            src_label = st.selectbox("Pathway Source:", options=list(loc_map.keys()), key="src_loc")
            dst_label = st.selectbox("Pathway Destination:", options=list(loc_map.keys()), key="dst_loc")
            target_src_id = loc_map[src_label]
            target_dst_id = loc_map[dst_label]

        rep_name = st.text_input("Reporter Name (Optional):", placeholder="e.g. Facilities Staff or Anonymous")

    rep_desc = st.text_area("Detailed Description of Obstacle:", placeholder="Provide clear details on the obstruction...")

    if st.button("Submit Report to Queue", type="primary"):
        if not rep_desc.strip():
            st.error("Please enter a description for the obstacle report.")
        elif rep_type == "Pathway Connection" and target_src_id == target_dst_id:
            st.error("Pathway source and destination cannot be the same location.")
        elif rep_type == "Pathway Connection" and not cmap.graph.has_edge(target_src_id, target_dst_id):
            st.error("There is no direct pathway connection between the selected locations.")
        else:
            try:
                new_rep = obs_manager.submit_report(
                    obstacle_category=rep_category,
                    severity=rep_severity,
                    description=rep_desc,
                    location_id=target_loc_id,
                    source_location_id=target_src_id,
                    destination_location_id=target_dst_id,
                    reporter_name=rep_name,
                )
                st.success(f"Report **{new_rep['report_id']}** successfully submitted with status **Pending**!")
                st.rerun()
            except Exception as ex:
                st.error(f"Failed to submit report: {ex}")
