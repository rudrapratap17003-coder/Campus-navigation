"""Dashboard Page - High-level overview of campus accessibility metrics, pathways, and obstacles."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from modules.ui_theme import apply_custom_theme, get_app_services

apply_custom_theme()
services = get_app_services()

cmap = services["campus_map"]
acc_engine = services["accessibility_engine"]
obs_manager = services["obstacle_manager"]

st.title("📊 Campus Accessibility & Navigation Dashboard")
st.write(
    "Live operational status of campus pedestrian infrastructure, accessibility coverage, "
    "and active obstacle management."
)

# Fetch actual data from live campus graph and SQLite database
acc_summary = acc_engine.get_accessibility_summary()
obs_stats = obs_manager.get_obstacle_statistics()
all_reports = obs_manager.get_all_reports()

active_count = obs_stats["active_obstacles_count"]
pending_count = obs_stats["status_counts"].get("Pending", 0)
resolved_count = obs_stats["status_counts"].get("Resolved", 0)

# --- TOP ROW: CAMPUS INFRASTRUCTURE KPIS ---
st.markdown("#### 🏛️ Campus Infrastructure & Accessibility Metrics")
kpi_c1, kpi_c2, kpi_c3 = st.columns(3)

with kpi_c1:
    st.markdown(
        f"""
        <div class="ui-card">
            <div class="ui-card-title">Campus Locations</div>
            <div class="ui-card-value">{acc_summary["total_locations"]}</div>
            <div class="ui-card-desc">Ground (Floor 0) & First Floor (Floor 1) Nodes</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_c2:
    st.markdown(
        f"""
        <div class="ui-card">
            <div class="ui-card-title">Total Pathways</div>
            <div class="ui-card-value">{acc_summary["total_pathways"]}</div>
            <div class="ui-card-desc">{acc_summary["accessible_pathways"]} Accessible · {acc_summary["inaccessible_pathways"]} Inaccessible (Stairs)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_c3:
    network_pct = acc_summary["network_accessibility_percentage"]
    st.markdown(
        f"""
        <div class="ui-card">
            <div class="ui-card-title">Network Accessibility Rate</div>
            <div class="ui-card-value">{network_pct}%</div>
            <div class="ui-card-desc">Average Heuristic Score: {acc_summary["average_pathway_score"]} / 100</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- SECOND ROW: OPERATIONAL OBSTACLE STATUS KPIS ---
st.markdown("#### ⚠️ Operational Obstacle & Hazard Status")
obs_c1, obs_c2, obs_c3 = st.columns(3)

with obs_c1:
    active_color = "#e63946" if active_count > 0 else "#2d6a4f"
    active_status_text = "Affecting Active Routing" if active_count > 0 else "All Pathways Operational"
    st.markdown(
        f"""
        <div class="ui-card" style="border-top: 3px solid {active_color};">
            <div class="ui-card-title">Active Verified Obstacles</div>
            <div class="ui-card-value" style="color: {active_color};">{active_count}</div>
            <div class="ui-card-desc">{active_status_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with obs_c2:
    pending_color = "#e76f51" if pending_count > 0 else "#4b6354"
    st.markdown(
        f"""
        <div class="ui-card" style="border-top: 3px solid {pending_color};">
            <div class="ui-card-title">Pending Obstacle Reports</div>
            <div class="ui-card-value" style="color: {pending_color};">{pending_count}</div>
            <div class="ui-card-desc">Filed & Awaiting Administrative Verification</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with obs_c3:
    st.markdown(
        f"""
        <div class="ui-card" style="border-top: 3px solid #52b788;">
            <div class="ui-card-title">Resolved Reports</div>
            <div class="ui-card-value" style="color: #2d6a4f;">{resolved_count}</div>
            <div class="ui-card-desc">Repairs Completed & Pathway Access Restored</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# --- CHARTS SECTION ---
c_left, c_right = st.columns(2)

with c_left:
    st.subheader("🚶 Pathway Accessibility Breakdown")
    # Real data from actual classification counts in graph
    class_counts = acc_summary["classification_counts"]
    df_pathways = pd.DataFrame(
        [
            {"Classification": cat, "Count": count}
            for cat, count in class_counts.items()
            if count > 0 or cat in ("Fully Accessible", "Not Wheelchair Accessible")
        ]
    )

    color_map = {
        "Fully Accessible": "#2d6a4f",
        "Accessible with Assistance": "#52b788",
        "Not Wheelchair Accessible": "#e63946",
        "Temporarily Blocked": "#d90429",
        "Unknown Accessibility": "#adb5bd",
    }

    fig_pathways = px.pie(
        df_pathways,
        names="Classification",
        values="Count",
        hole=0.52,
        color="Classification",
        color_discrete_map=color_map,
    )
    fig_pathways.update_layout(
        margin=dict(t=15, b=15, l=15, r=15),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#1b4332"),
        ),
        height=320,
        annotations=[
            dict(
                text=f"<b>{acc_summary['total_pathways']}</b><br>Paths",
                x=0.5,
                y=0.5,
                font_size=16,
                font_color="#1b4332",
                showarrow=False,
            )
        ],
    )
    st.plotly_chart(fig_pathways, use_container_width=True)

with c_right:
    st.subheader("⚠️ Obstacle Reports Distribution")

    # Empty-state check: If no reports exist in SQLite database, show clean professional empty-state
    if obs_stats["total_reports"] == 0:
        st.markdown(
            """
            <div style="background-color: #ffffff; border: 1px dashed #b7e4c7; border-radius: 10px; padding: 42px 20px; text-align: center; margin-top: 10px;">
                <div style="font-size: 2.5rem; margin-bottom: 8px;">🛡️</div>
                <div style="font-weight: 700; color: #1b4332; font-size: 1.05rem;">No Obstacle Reports Recorded</div>
                <div style="color: #4b6354; font-size: 0.88rem; max-width: 380px; margin: 6px auto 0 auto; line-height: 1.45;">
                    All 17 surveyed campus pathways are currently operating under baseline conditions. When hazards or maintenance closures are filed, their status distribution will display here.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        status_counts = obs_stats["status_counts"]
        df_status = pd.DataFrame(
            [{"Status": s, "Reports": count} for s, count in status_counts.items()]
        )

        status_color_map = {
            "Pending": "#f4a261",
            "Verified": "#e63946",
            "Resolved": "#2d6a4f",
            "Rejected": "#6c757d",
        }

        fig_status = px.bar(
            df_status,
            x="Status",
            y="Reports",
            color="Status",
            color_discrete_map=status_color_map,
            text="Reports",
        )
        max_y = max(1, max(status_counts.values()))
        fig_status.update_layout(
            margin=dict(t=25, b=25, l=45, r=20),
            height=320,
            showlegend=False,
            yaxis=dict(
                title="Number of Reports",
                dtick=1,
                tick0=0,
                range=[0, max_y + 1],
                gridcolor="#f0f7f3",
                title_font=dict(size=12, color="#4b6354"),
                tickfont=dict(size=11, color="#1b4332"),
            ),
            xaxis=dict(
                title="",
                tickfont=dict(size=12, color="#1b4332", family="sans-serif"),
            ),
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
        )
        st.plotly_chart(fig_status, use_container_width=True)

st.markdown("---")

# --- ACCESSIBILITY INFRASTRUCTURE SUMMARY & QUICK ACTIONS ---
inf_col, action_col = st.columns([3, 2])

with inf_col:
    st.subheader("🏢 Accessibility Infrastructure Features")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Elevator Transitions", acc_summary["elevator_pathways"])
    with col_b:
        st.metric("Dedicated Ramps", acc_summary["ramp_pathways"])
    with col_c:
        st.metric("Stairway Connectors", acc_summary["stairs_pathways"])

    st.markdown(
        """
        <div class="disclaimer-banner">
            <b>Algorithmic Heuristic Notice:</b> Accessibility scores and classifications are calculated
            heuristically to assist routing decisions. They do not constitute official building-code or ADA regulatory certifications.
        </div>
        """,
        unsafe_allow_html=True,
    )

with action_col:
    st.subheader("⚡ Quick Actions")
    st.write("Jump straight to key workflows:")
    if st.button("🧭 Plan an Accessible Route", use_container_width=True):
        st.switch_page("pages/navigation.py")
    if st.button("🗺️ Explore Interactive Campus Map", use_container_width=True):
        st.switch_page("pages/campus_map.py")
    if st.button("⚠️ View Active Obstacle Reports", use_container_width=True):
        st.switch_page("pages/obstacle_reports.py")

st.markdown("---")

# --- RECENT OBSTACLE REPORTS ---
st.subheader("📋 Recent Obstacle & Hazard Reports")
if all_reports:
    df_recent = pd.DataFrame(all_reports[:5])[
        ["report_id", "obstacle_category", "severity", "status", "reported_at", "reporter_name"]
    ]
    df_recent.columns = ["Report ID", "Category", "Severity", "Status", "Reported At", "Reporter"]
    st.dataframe(df_recent, use_container_width=True, hide_index=True)
else:
    st.info("No obstacle reports have been filed yet. All pathways are currently operating under baseline conditions.")
