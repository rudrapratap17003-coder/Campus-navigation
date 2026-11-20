"""Dashboard Page - High-level overview of campus accessibility metrics, pathways, and obstacles."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from modules.ui_theme import (
    ACCENT_GREEN,
    ERROR,
    INFO,
    PRIMARY_GREEN,
    SECONDARY_TEXT,
    WARNING,
    WHITE,
    apply_custom_theme,
    apply_plotly_dark_theme,
    get_app_services,
    render_kpi_card,
)

apply_custom_theme()
services = get_app_services()

cmap = services["campus_map"]
acc_engine = services["accessibility_engine"]
obs_manager = services["obstacle_manager"]

# Fetch actual data from live campus graph and SQLite database
acc_summary = acc_engine.get_accessibility_summary()
obs_stats = obs_manager.get_obstacle_statistics()
all_reports = obs_manager.get_all_reports()

active_count = obs_stats["active_obstacles_count"]
pending_count = obs_stats["status_counts"].get("Pending", 0)
resolved_count = obs_stats["status_counts"].get("Resolved", 0)

# --- HERO WELCOME BANNER ---
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">🧭 Campus Accessibility & Navigation Intelligence</div>
        <div class="hero-subtitle">
            Real-time multi-floor pedestrian intelligence platform empowering students, staff, and visitors
            with barrier-free route calculations, topological indoor maps, and live community hazard management.
        </div>
        <div class="hero-chips">
            <span class="hero-chip">🟢 Step-Free Dijkstra & BFS</span>
            <span class="hero-chip">🏢 Multi-Level Indoor Cartography</span>
            <span class="hero-chip">🛡️ Active Barrier Detours</span>
            <span class="hero-chip">🔒 RBAC & OWASP Hashing</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- TOP ROW: CAMPUS INFRASTRUCTURE KPIS ---
st.markdown("### 🏛️ Infrastructure & Network Coverage")
kpi_c1, kpi_c2, kpi_c3 = st.columns(3)

with kpi_c1:
    st.markdown(
        render_kpi_card(
            title="Campus Locations",
            value=acc_summary["total_locations"],
            desc="Ground (Floor 0) & First Floor (Floor 1) Spatial Nodes",
            border_accent=PRIMARY_GREEN,
            value_color=WHITE,
        ),
        unsafe_allow_html=True,
    )

with kpi_c2:
    st.markdown(
        render_kpi_card(
            title="Total Pathways",
            value=acc_summary["total_pathways"],
            desc=f"{acc_summary['accessible_pathways']} Accessible · {acc_summary['inaccessible_pathways']} Inaccessible (Stairs)",
            border_accent=ACCENT_GREEN,
            value_color=WHITE,
        ),
        unsafe_allow_html=True,
    )

with kpi_c3:
    network_pct = acc_summary["network_accessibility_percentage"]
    st.markdown(
        render_kpi_card(
            title="Network Accessibility Rate",
            value=f"{network_pct}%",
            desc=f"Average Heuristic Score: {acc_summary['average_pathway_score']} / 100",
            border_accent=PRIMARY_GREEN,
            value_color=ACCENT_GREEN,
        ),
        unsafe_allow_html=True,
    )

# --- SECOND ROW: OPERATIONAL OBSTACLE STATUS KPIS ---
st.markdown("### ⚠️ Active Obstacles & Maintenance Status")
obs_c1, obs_c2, obs_c3 = st.columns(3)

with obs_c1:
    active_color = ERROR if active_count > 0 else PRIMARY_GREEN
    active_status_text = "Affecting Live Routing Detours" if active_count > 0 else "All Corridors Fully Operational"
    st.markdown(
        render_kpi_card(
            title="Active Verified Obstacles",
            value=active_count,
            desc=active_status_text,
            border_accent=active_color,
            value_color=active_color,
        ),
        unsafe_allow_html=True,
    )

with obs_c2:
    pending_color = WARNING if pending_count > 0 else SECONDARY_TEXT
    st.markdown(
        render_kpi_card(
            title="Pending Obstacle Reports",
            value=pending_count,
            desc="Submitted by Users · Awaiting Staff Inspection",
            border_accent=pending_color,
            value_color=pending_color,
        ),
        unsafe_allow_html=True,
    )

with obs_c3:
    st.markdown(
        render_kpi_card(
            title="Resolved Obstacles",
            value=resolved_count,
            desc="Repairs Completed · Pathway Access Fully Restored",
            border_accent=ACCENT_GREEN,
            value_color=ACCENT_GREEN,
        ),
        unsafe_allow_html=True,
    )

st.markdown("---")

# --- CHARTS SECTION ---
st.markdown("### 📈 Visual Analytics & Pathway Distribution")
c_left, c_right = st.columns(2)

with c_left:
    st.markdown("##### 🚶 Pathway Accessibility Breakdown")
    class_counts = acc_summary["classification_counts"]
    df_pathways = pd.DataFrame(
        [
            {"Classification": cat, "Count": count}
            for cat, count in class_counts.items()
            if count > 0 or cat in ("Fully Accessible", "Not Wheelchair Accessible")
        ]
    )

    color_map = {
        "Fully Accessible": PRIMARY_GREEN,
        "Accessible with Assistance": ACCENT_GREEN,
        "Not Wheelchair Accessible": ERROR,
        "Temporarily Blocked": "#DC2626",
        "Unknown Accessibility": SECONDARY_TEXT,
    }

    fig_pathways = px.pie(
        df_pathways,
        names="Classification",
        values="Count",
        hole=0.58,
        color="Classification",
        color_discrete_map=color_map,
    )
    apply_plotly_dark_theme(fig_pathways, height=330)
    fig_pathways.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.12,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color=WHITE),
        ),
        annotations=[
            dict(
                text=f"<b>{acc_summary['total_pathways']}</b><br><span style='font-size:11px;color:#9CAFA5'>Paths</span>",
                x=0.5,
                y=0.5,
                font_size=18,
                font_color=WHITE,
                showarrow=False,
            )
        ],
    )
    st.plotly_chart(fig_pathways, use_container_width=True)

with c_right:
    st.markdown("##### ⚠️ Obstacle Reports Distribution")

    if obs_stats["total_reports"] == 0:
        st.markdown(
            """
            <div class="ui-card" style="text-align: center; padding: 48px 24px;">
                <div style="font-size: 2.6rem; margin-bottom: 8px;">🛡️</div>
                <div style="font-weight: 700; color: #F8FAFC; font-size: 1.1rem;">Zero Active Obstacle Reports</div>
                <div style="color: #9CAFA5; font-size: 0.88rem; max-width: 400px; margin: 8px auto 0 auto; line-height: 1.45;">
                    All 17 surveyed campus pathways are currently operating under baseline conditions. Filed incident reports and maintenance logs will display here.
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
            "Pending": WARNING,
            "Verified": ERROR,
            "Resolved": ACCENT_GREEN,
            "Rejected": SECONDARY_TEXT,
        }

        fig_status = px.bar(
            df_status,
            x="Status",
            y="Reports",
            color="Status",
            color_discrete_map=status_color_map,
            text="Reports",
        )
        apply_plotly_dark_theme(fig_status, height=330)
        max_y = max(1, max(status_counts.values()))
        fig_status.update_layout(
            showlegend=False,
            yaxis=dict(
                title="Number of Reports",
                dtick=1,
                tick0=0,
                range=[0, max_y + 1],
                gridcolor="rgba(53, 217, 154, 0.08)",
                title_font=dict(size=12, color=SECONDARY_TEXT),
                tickfont=dict(size=11, color=WHITE),
            ),
            xaxis=dict(
                title="",
                tickfont=dict(size=12, color=WHITE),
            ),
        )
        st.plotly_chart(fig_status, use_container_width=True)

st.markdown("---")

# --- ACCESSIBILITY INFRASTRUCTURE SUMMARY & QUICK ACTIONS ---
inf_col, action_col = st.columns([3, 2])

with inf_col:
    st.markdown("### 🏢 Assistive Infrastructure Assets")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Elevator Hubs", f"{acc_summary['elevator_pathways']} Links")
    with col_b:
        st.metric("Dedicated Ramps", f"{acc_summary['ramp_pathways']} Ramps")
    with col_c:
        st.metric("Stairway Links", f"{acc_summary['stairs_pathways']} Stairs")

    st.markdown(
        """
        <div class="disclaimer-banner">
            <b>⚖️ Algorithmic Heuristic Notice:</b> Accessibility scores (0–100) and classifications are computed
            heuristically based on surveyed slope, step-free status, and elevator availability. They do not constitute official building-code or ADA regulatory certifications.
        </div>
        """,
        unsafe_allow_html=True,
    )

with action_col:
    st.markdown("### ⚡ Quick Navigation Actions")
    st.write("Instant access to core platform services:")
    if st.button("🧭 Plan an Accessible Route", use_container_width=True):
        st.switch_page("pages/navigation.py")
    if st.button("🗺️ Explore Interactive Campus Map", use_container_width=True):
        st.switch_page("pages/campus_map.py")
    if st.button("⚠️ View Active Obstacle Reports", use_container_width=True):
        st.switch_page("pages/obstacle_reports.py")

st.markdown("---")

# --- RECENT OBSTACLE REPORTS ---
st.markdown("### 📋 Recent Obstacle & Hazard Reports")
if all_reports:
    df_recent = pd.DataFrame(all_reports[:5])[
        ["report_id", "obstacle_category", "severity", "status", "reported_at", "reporter_name"]
    ]
    df_recent.columns = ["Report ID", "Category", "Severity", "Status", "Reported At", "Reporter"]
    st.dataframe(df_recent, use_container_width=True, hide_index=True)
else:
    st.info("No obstacle reports have been filed yet. All pathways are currently operating under baseline conditions.")
