"""Obstacle Reports Page - Review barrier reports, filter hazards, and manage field verification."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.ui_theme import apply_custom_theme, get_app_services, get_current_user

apply_custom_theme()
services = get_app_services()

obs_manager = services["obstacle_manager"]
cmap = services["campus_map"]

current_user = get_current_user()
user_role = current_user.get("role") if current_user else None
is_staff_or_admin = user_role in ("Field Staff", "Administrator")

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

# =============================================================================
# STAFF / ADMIN VERIFICATION & RESOLUTION ACTIONS (FIELD STAFF & ADMIN ONLY)
# =============================================================================
if is_staff_or_admin:
    st.subheader("🛠️ Field Operations Queue")
    staff_tab1, staff_tab2 = st.tabs(["📋 Pending Review Queue", "🔧 Resolve Active Obstacles"])

    with staff_tab1:
        pending_list = [r for r in all_reports if r["status"] == "Pending"]
        if not pending_list:
            st.success("✅ No reports currently require verification.")
        else:
            st.write(f"**{len(pending_list)}** reports awaiting inspection and verification:")
            for p in pending_list:
                with st.expander(f"Pending #{p['report_id']} - {p['obstacle_category']} ({p['severity']})", expanded=True):
                    # Target description
                    if p["target_type"] == "pathway":
                        s_loc = cmap.get_location(p["source_location_id"])
                        d_loc = cmap.get_location(p["destination_location_id"])
                        tgt_name = f"Pathway: {s_loc['name'] if s_loc else p['source_location_id']} ↔ {d_loc['name'] if d_loc else p['destination_location_id']}"
                    else:
                        loc = cmap.get_location(p["location_id"])
                        tgt_name = f"Location: {loc['name'] if loc else p['location_id']}"

                    st.markdown(f"**Target:** {tgt_name} | **Severity:** {p['severity']} | **Filed by:** {p['reporter_name']}")
                    st.markdown(f"**Description:** {p['description']}")

                    act_col1, act_col2 = st.columns([1, 2])
                    with act_col1:
                        if st.button("✅ Verify & Block Route", key=f"obs_verify_{p['report_id']}", type="primary"):
                            try:
                                obs_manager.verify_report(p["report_id"], actor_user=current_user)
                                st.success(f"Report {p['report_id']} verified. Route blocked on graph.")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Failed to verify report: {ex}")

                    with act_col2:
                        with st.popover(f"❌ Reject Report"):
                            rej_input = st.text_input("Rejection Reason:", key=f"obs_rej_reason_{p['report_id']}", placeholder="e.g. Duplicate or obstruction cleared")
                            if st.button("Confirm Rejection", key=f"obs_confirm_rej_{p['report_id']}"):
                                try:
                                    obs_manager.reject_report(p["report_id"], rejection_reason=rej_input, actor_user=current_user)
                                    st.info(f"Report {p['report_id']} rejected.")
                                    st.rerun()
                                except Exception as ex:
                                    st.error(f"Failed to reject report: {ex}")

    with staff_tab2:
        verified_list = [r for r in all_reports if r["status"] == "Verified"]
        if not verified_list:
            st.info("No active verified obstacles currently blocking navigation.")
        else:
            st.write(f"**{len(verified_list)}** active obstacles currently blocking navigation routes:")
            for v in verified_list:
                with st.expander(f"Active Obstacle #{v['report_id']} - {v['obstacle_category']} ({v['severity']})", expanded=False):
                    if v["target_type"] == "pathway":
                        s_loc = cmap.get_location(v["source_location_id"])
                        d_loc = cmap.get_location(v["destination_location_id"])
                        tgt_name = f"Pathway: {s_loc['name'] if s_loc else v['source_location_id']} ↔ {d_loc['name'] if d_loc else v['destination_location_id']}"
                    else:
                        loc = cmap.get_location(v["location_id"])
                        tgt_name = f"Location: {loc['name'] if loc else v['location_id']}"

                    st.markdown(f"**Target:** {tgt_name} | **Status:** <span style='color:red;'><b>ACTIVE BLOCKAGE</b></span>", unsafe_allow_html=True)
                    st.markdown(f"**Description:** {v['description']}")

                    with st.form(f"resolve_form_{v['report_id']}"):
                        res_notes = st.text_area("Mandatory Resolution Notes:", placeholder="Describe the maintenance performed and confirmed clearance...")
                        if st.form_submit_button("Mark as Resolved & Restore Route", type="primary"):
                            if not res_notes.strip():
                                st.error("Resolution notes are mandatory when marking an obstacle resolved.")
                            else:
                                try:
                                    obs_manager.resolve_report(v["report_id"], resolution_notes=res_notes.strip(), actor_user=current_user)
                                    st.success(f"Report {v['report_id']} marked as Resolved. Pathway restored!")
                                    st.rerun()
                                except Exception as ex:
                                    st.error(f"Failed to resolve report: {ex}")

    st.markdown("---")

# =============================================================================
# FILTERING CONTROLS
# =============================================================================
st.subheader("🔍 Browse Incident Log")
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

# If user is a student, offer a checkbox to view only their submitted reports
if current_user and not is_staff_or_admin:
    only_my_reports = st.checkbox("Show only my filed reports", value=False)
    if only_my_reports:
        filtered_reports = [
            r for r in filtered_reports
            if f"@{current_user['username']}" in r.get("reporter_name", "")
            or r.get("reporter_name") == current_user["full_name"]
        ]

st.markdown(f"**Found {len(filtered_reports)} matching reports**")

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

# =============================================================================
# REPORT SUBMISSION FORM WITH DUPLICATE DETECTION WARNING
# =============================================================================
with st.expander("➕ Log a New Obstacle or Hazard Report", expanded=False):
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

        default_rep_name = f"{current_user['full_name']} (@{current_user['username']})" if current_user else ""
        rep_name = st.text_input("Reporter Name:", value=default_rep_name, placeholder="e.g. Facilities Staff or Anonymous")

    # DUPLICATE DETECTION CHECK
    potential_duplicates = obs_manager.detect_potential_duplicates(
        source_location_id=target_src_id,
        destination_location_id=target_dst_id,
        location_id=target_loc_id,
    )
    if potential_duplicates:
        st.warning(
            f"⚠️ **Duplicate Warning**: There are currently **{len(potential_duplicates)}** active or pending report(s) "
            f"already affecting this target (e.g. Report **{potential_duplicates[0]['report_id']}** - "
            f"Status: **{potential_duplicates[0]['status']}**). You can still submit if you are filing additional observations."
        )

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
                    reporter_name=rep_name if rep_name.strip() else ("Anonymous" if not current_user else current_user["full_name"]),
                )
                st.success(f"Report **{new_rep['report_id']}** successfully submitted with status **Pending**!")
                st.rerun()
            except Exception as ex:
                st.error(f"Failed to submit report: {ex}")
