"""Dashboard Page - High-level overview of campus accessibility metrics, pathways, and obstacles.

Phase 19 Advanced Campus Intelligence & Analytics:
- Supports both JAIN Global Campus (79 locations, 106 pathways, 5 floors) and Schematic Benchmark.
- Displays actual accessibility coverage, obstacle lifecycles, and navigation telemetry.
- Renders floor-by-floor barrier distributions and data verification progress.
- Strictly adheres to evidence-based statistics (no fabricated AI predictions).
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from modules.campus_analytics import (
    compute_accessibility_analytics,
    compute_administrative_insights,
    compute_navigation_analytics,
    compute_obstacle_analytics,
)
from modules.jain_digital_twin import load_jain_campus_map
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

benchmark_cmap = services["campus_map"]
obs_manager = services["obstacle_manager"]
db_manager = services.get("db_manager")

# --- HERO WELCOME BANNER ---
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">🧭 Accessible Campus Navigator</div>
        <div class="hero-subtitle" style="font-size: 1.05rem; font-weight: 500; color: #A7F3D0; margin-bottom: 6px;">
            An intelligent campus wayfinding system designed to make university spaces easier to explore and more accessible for everyone.
        </div>
        <div class="hero-description" style="color: #9CAFA5; font-size: 0.9rem; margin-bottom: 12px;">
            Find destinations, explore campus buildings, discover accessible routes, and report obstacles through a unified digital navigation platform.
        </div>
        <div class="hero-chips">
            <span class="hero-chip">🏛️ JAIN Global Campus</span>
            <span class="hero-chip">🏢 5-Floor FET Digital Twin</span>
            <span class="hero-chip">♿ Heuristic Step-Free Routing</span>
            <span class="hero-chip">⚠️ Dynamic Obstacle Management</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Campus Dataset Selection
with st.container(border=True):
    campus_choice = st.radio(
        "🗺️ Select Campus Dataset for Analytics:",
        options=[
            "🏛️ JAIN Global Campus & FET 5-Floor Digital Twin (79 Nodes, 106 Pathways)",
            "📐 Schematic Benchmark Model (15 Nodes, 17 Pathways)",
        ],
        index=0,
        horizontal=True,
        key="analytics_campus_choice",
    )

is_jain = "JAIN" in campus_choice
active_cmap = services.get("jain_campus_map") if (is_jain and services.get("jain_campus_map")) else (load_jain_campus_map() if is_jain else benchmark_cmap)
obs_manager.sync_obstacles_to_campus_map(active_cmap)

# Calculate live analytics from genuine database records and spatial graph
acc_analytics = compute_accessibility_analytics(active_cmap, obs_manager)
obs_analytics = compute_obstacle_analytics(db_manager, active_cmap)
nav_analytics = compute_navigation_analytics(db_manager)
admin_insights = compute_administrative_insights(active_cmap, db_manager, obs_manager)

# --- TOP ROW: CAMPUS INFRASTRUCTURE & ACCESSIBILITY COVERAGE KPIS ---
st.markdown("### 🏛️ Infrastructure & Accessibility Coverage")
kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)

with kpi_c1:
    st.markdown(
        render_kpi_card(
            title="Campus Locations",
            value=acc_analytics["total_locations"],
            desc=f"{acc_analytics['accessible_locations']} Step-Free Accessible ({acc_analytics['location_accessibility_percentage']}%)",
            border_accent=PRIMARY_GREEN,
            value_color=WHITE,
        ),
        unsafe_allow_html=True,
    )

with kpi_c2:
    st.markdown(
        render_kpi_card(
            title="Campus Pathways",
            value=acc_analytics["total_pathways"],
            desc=f"{acc_analytics['step_free_pathways']} Step-Free ({acc_analytics['pathway_accessibility_percentage']}%) · Avg Score {acc_analytics['average_pathway_score']}/100 · {acc_analytics['ramp_pathways']} Ramps · {acc_analytics['elevator_pathways']} Elevators",
            border_accent=ACCENT_GREEN,
            value_color=WHITE,
        ),
        unsafe_allow_html=True,
    )

with kpi_c3:
    st.markdown(
        render_kpi_card(
            title="Physical Verification",
            value=f"{admin_insights['verification_progress_percentage']}%",
            desc=f"{admin_insights['verification_counts']['VERIFIED']} Physically Audited · {admin_insights['verification_counts']['IMAGE_DERIVED']} Floor-Plan Derived",
            border_accent="#38BDF8",
            value_color="#38BDF8",
        ),
        unsafe_allow_html=True,
    )

with kpi_c4:
    gaps_count = acc_analytics["information_gaps_count"]
    pending_audit = admin_insights["pending_physical_verification_nodes"]
    gaps_color = WARNING if (gaps_count > 0 or pending_audit > 0) else PRIMARY_GREEN
    st.markdown(
        render_kpi_card(
            title="Attribute Gaps / Audit Queue",
            value=f"{gaps_count} / {pending_audit}",
            desc=f"{gaps_count} Missing Attrs · {pending_audit} Pending Physical Survey",
            border_accent=gaps_color,
            value_color=gaps_color,
        ),
        unsafe_allow_html=True,
    )

# --- SECOND ROW: OPERATIONAL OBSTACLE STATUS KPIS ---
st.markdown("### ⚠️ Obstacle Reports & Maintenance Lifecycle")
obs_c1, obs_c2, obs_c3, obs_c4 = st.columns(4)

active_obstacles = obs_analytics["active_verified_obstacles"]
pending_obstacles = obs_analytics["pending_reports"]
resolved_obstacles = obs_analytics["resolved_obstacles"]
avg_res_time = obs_analytics["average_resolution_time_hours"]

with obs_c1:
    act_col = ERROR if active_obstacles > 0 else PRIMARY_GREEN
    st.markdown(
        render_kpi_card(
            title="Active Hazards",
            value=active_obstacles,
            desc="Blocking live routes" if active_obstacles > 0 else "All corridors operational",
            border_accent=act_col,
            value_color=act_col,
        ),
        unsafe_allow_html=True,
    )

with obs_c2:
    pend_col = WARNING if pending_obstacles > 0 else SECONDARY_TEXT
    st.markdown(
        render_kpi_card(
            title="Pending Reports",
            value=pending_obstacles,
            desc="Awaiting staff inspection",
            border_accent=pend_col,
            value_color=pend_col,
        ),
        unsafe_allow_html=True,
    )

with obs_c3:
    st.markdown(
        render_kpi_card(
            title="Resolved Obstacles",
            value=resolved_obstacles,
            desc="Repairs verified & cleared",
            border_accent=ACCENT_GREEN,
            value_color=ACCENT_GREEN,
        ),
        unsafe_allow_html=True,
    )

with obs_c4:
    st.markdown(
        render_kpi_card(
            title="Avg Resolution Time",
            value=f"{avg_res_time} hrs" if avg_res_time > 0 else "N/A",
            desc="From report filing to clearance",
            border_accent="#A78BFA",
            value_color="#A78BFA",
        ),
        unsafe_allow_html=True,
    )

st.markdown("---")

# --- CHARTS ROW 1: SPATIAL DISTRIBUTIONS ---
st.markdown("### 📈 Visual Analytics & Spatial Distributions")
c_ch1, c_ch2 = st.columns(2)

with c_ch1:
    st.markdown("##### 🏢 Obstacle Distribution by Floor Level")
    floor_dist = obs_analytics["floor_distribution"]
    floor_labels = {
        -1: "Outdoor Campus",
        0: "Ground Floor",
        1: "Floor 1",
        2: "Floor 2",
        3: "Floor 3",
        4: "Floor 4",
    }
    total_floor_obs = sum(floor_dist.values())
    if total_floor_obs == 0:
        st.markdown(
            """
            <div class="ui-card" style="text-align: center; padding: 36px 18px;">
                <div style="font-size: 2rem; margin-bottom: 6px;">🏢</div>
                <div style="font-weight: 700; color: #F8FAFC;">No Floor-Specific Obstacles Recorded</div>
                <div style="color: #9CAFA5; font-size: 12px; margin-top: 6px;">
                    No obstacle reports currently reference locations in the selected campus dataset.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        df_floor = pd.DataFrame([
            {"Floor Level": floor_labels.get(fl, f"Level {fl}"), "Obstacles": count}
            for fl, count in floor_dist.items()
        ])
        fig_floor = px.bar(
            df_floor,
            x="Floor Level",
            y="Obstacles",
            color="Obstacles",
            color_continuous_scale=["#16A36A", "#F5B942", "#EF4444"],
            text="Obstacles",
        )
        apply_plotly_dark_theme(fig_floor, height=320)
        fig_floor.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_floor, width="stretch")
        other_cnt = obs_analytics.get("unmapped_other_dataset_reports", 0)
        if other_cnt > 0:
            st.caption(f"ℹ️ Plus {other_cnt} obstacle report(s) belonging to the alternate campus model.")

with c_ch2:
    st.markdown("##### 📋 Obstacle Lifecycle Status Breakdown")
    status_counts = obs_analytics["status_counts"]
    if sum(status_counts.values()) == 0:
        st.markdown(
            """
            <div class="ui-card" style="text-align: center; padding: 36px 18px;">
                <div style="font-size: 2rem; margin-bottom: 6px;">📋</div>
                <div style="font-weight: 700; color: #F8FAFC;">No Obstacle Reports Logged</div>
                <div style="color: #9CAFA5; font-size: 12px; margin-top: 6px;">
                    Lifecycle breakdowns (Pending, Verified, Resolved, Rejected) will appear once reports are filed.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        df_status = pd.DataFrame([
            {"Status": s, "Reports": c}
            for s, c in status_counts.items()
            if c > 0
        ])
        status_colors = {
            "Verified": ERROR,
            "Pending": WARNING,
            "Resolved": ACCENT_GREEN,
            "Rejected": SECONDARY_TEXT,
        }
        fig_status = px.pie(
            df_status,
            names="Status",
            values="Reports",
            hole=0.58,
            color="Status",
            color_discrete_map=status_colors,
        )
        apply_plotly_dark_theme(fig_status, height=320)
        st.plotly_chart(fig_status, width="stretch")

# --- CHARTS ROW 1B: SEVERITY, PATHWAY ACCESSIBILITY & VERIFICATION COVERAGE ---
c_ch3, c_ch4, c_ch5 = st.columns(3)

with c_ch3:
    st.markdown("##### 🚨 Obstacles by Severity")
    sev_counts = obs_analytics["severity_counts"]
    if sum(sev_counts.values()) == 0:
        st.markdown(
            """
            <div class="ui-card" style="text-align: center; padding: 32px 14px;">
                <div style="font-size: 1.8rem; margin-bottom: 6px;">🚨</div>
                <div style="font-weight: 700; color: #F8FAFC;">No Severity Records</div>
                <div style="color: #9CAFA5; font-size: 12px; margin-top: 6px;">
                    No active or historical obstacle reports exist yet.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        df_sev = pd.DataFrame([
            {"Severity": k, "Reports": v}
            for k, v in sev_counts.items()
        ])
        sev_colors = {"Low": ACCENT_GREEN, "Medium": INFO, "High": WARNING, "Critical": ERROR}
        fig_sev = px.bar(
            df_sev,
            x="Severity",
            y="Reports",
            color="Severity",
            color_discrete_map=sev_colors,
            text="Reports",
        )
        apply_plotly_dark_theme(fig_sev, height=300)
        fig_sev.update_layout(showlegend=False)
        st.plotly_chart(fig_sev, width="stretch")

with c_ch4:
    st.markdown("##### ♿ Pathway Accessibility Distribution")
    p_cls_counts = acc_analytics.get("pathway_classification_counts", {})
    if sum(p_cls_counts.values()) == 0:
        st.info("No pathway accessibility records available for the selected dataset.")
    else:
        df_pcls = pd.DataFrame([
            {"Classification": k, "Pathways": v}
            for k, v in p_cls_counts.items()
            if v > 0
        ])
        cls_colors = {
            "Fully Accessible": PRIMARY_GREEN,
            "Accessible with Assistance": WARNING,
            "Not Wheelchair Accessible": ERROR,
            "Temporarily Blocked": "#DC2626",
            "Unknown Accessibility": SECONDARY_TEXT,
        }
        fig_pcls = px.pie(
            df_pcls,
            names="Classification",
            values="Pathways",
            hole=0.55,
            color="Classification",
            color_discrete_map=cls_colors,
        )
        apply_plotly_dark_theme(fig_pcls, height=300)
        st.plotly_chart(fig_pcls, width="stretch")

with c_ch5:
    st.markdown("##### 🔍 Location Verification Coverage")
    v_counts = admin_insights.get("verification_counts", {})
    if sum(v_counts.values()) == 0:
        st.info("No location verification records found.")
    else:
        df_verif = pd.DataFrame([
            {"Status": k, "Locations": v}
            for k, v in v_counts.items()
            if v > 0
        ])
        verif_colors = {
            "VERIFIED": ACCENT_GREEN,
            "IMAGE_DERIVED": INFO,
            "APPROXIMATE": WARNING,
            "UNVERIFIED": SECONDARY_TEXT,
        }
        fig_verif = px.bar(
            df_verif,
            x="Status",
            y="Locations",
            color="Status",
            color_discrete_map=verif_colors,
            text="Locations",
        )
        apply_plotly_dark_theme(fig_verif, height=300)
        fig_verif.update_layout(showlegend=False)
        st.plotly_chart(fig_verif, width="stretch")
        st.caption(
            f"Populated fields: {acc_analytics['populated_fields_percentage']}% · "
            f"Physically audited: {admin_insights['verification_progress_percentage']}%"
        )

# --- CHARTS ROW 2: NAVIGATION TELEMETRY & WAYFINDING KPIS ---
st.markdown("### 🚶 Wayfinding Telemetry & Destination Insights")
c_nav1, c_nav2 = st.columns(2)

with c_nav1:
    st.markdown("##### 🎯 Frequently Selected Destinations")
    top_dests = nav_analytics["top_destinations"]
    if not top_dests:
        st.markdown(
            """
            <div class="ui-card" style="text-align: center; padding: 36px 18px;">
                <div style="font-size: 2rem; margin-bottom: 6px;">🧭</div>
                <div style="font-weight: 700; color: #F8FAFC;">No Historical Navigation Journeys Yet</div>
                <div style="color: #9CAFA5; font-size: 12px; margin-top: 6px;">
                    Journeys calculated and completed on the 3D map will record destination telemetry here.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        df_dests = pd.DataFrame([
            {"Destination": dest, "Trips": count}
            for dest, count in top_dests
        ])
        fig_dests = px.bar(
            df_dests,
            y="Destination",
            x="Trips",
            orientation="h",
            color="Trips",
            color_continuous_scale=["#38BDF8", "#35D99A"],
            text="Trips",
        )
        apply_plotly_dark_theme(fig_dests, height=320)
        fig_dests.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_dests, width="stretch")

with c_nav2:
    st.markdown("##### ⏱️ Navigation Journey Telemetry")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown(
            f"""
            <div style="background: rgba(13, 31, 24, 0.85); border: 1px solid rgba(53, 217, 154, 0.2); border-radius: 8px; padding: 14px; margin-bottom: 12px;">
                <div style="font-size: 11px; color: #9CAFA5; font-weight: 700; text-transform: uppercase;">Total Journeys Logged</div>
                <div style="font-size: 26px; font-weight: 800; color: #F8FAFC; margin-top: 4px;">{nav_analytics['total_journeys']}</div>
                <div style="font-size: 11px; color: #35D99A; margin-top: 2px;">{nav_analytics['completion_rate_percentage']}% Completion Rate</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="background: rgba(13, 31, 24, 0.85); border: 1px solid rgba(53, 217, 154, 0.2); border-radius: 8px; padding: 14px;">
                <div style="font-size: 11px; color: #9CAFA5; font-weight: 700; text-transform: uppercase;">Average Trip Distance</div>
                <div style="font-size: 26px; font-weight: 800; color: #35D99A; margin-top: 4px;">{nav_analytics['average_route_distance_m']} m</div>
                <div style="font-size: 11px; color: #9CAFA5; margin-top: 2px;">~{nav_analytics['average_duration_minutes']} min estimated</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with t2:
        st.markdown(
            f"""
            <div style="background: rgba(13, 31, 24, 0.85); border: 1px solid rgba(53, 217, 154, 0.2); border-radius: 8px; padding: 14px; margin-bottom: 12px;">
                <div style="font-size: 11px; color: #9CAFA5; font-weight: 700; text-transform: uppercase;">Floor Transitions</div>
                <div style="font-size: 26px; font-weight: 800; color: #38BDF8; margin-top: 4px;">{nav_analytics['total_floor_transitions']}</div>
                <div style="font-size: 11px; color: #9CAFA5; margin-top: 2px;">Elevator & Stair shaft hops</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="background: rgba(13, 31, 24, 0.85); border: 1px solid rgba(245, 185, 66, 0.2); border-radius: 8px; padding: 14px;">
                <div style="font-size: 11px; color: #9CAFA5; font-weight: 700; text-transform: uppercase;">Detours / Reroutes</div>
                <div style="font-size: 26px; font-weight: 800; color: #F5B942; margin-top: 4px;">{nav_analytics['rerouted_journeys']}</div>
                <div style="font-size: 11px; color: #9CAFA5; margin-top: 2px;">Automatic barrier bypasses</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --- ADMINISTRATIVE OPERATIONAL DIRECTIVES ---
st.markdown("---")
st.markdown("### 🛡️ Administrative Insights & Priority Directives")
admin_items = admin_insights["action_items"]
if not admin_items:
    st.success("✅ All campus accessibility parameters and obstacle lifecycles are operating within baseline parameters.")
else:
    for item in admin_items:
        st.markdown(
            f"""
            <div style="background: rgba(13, 31, 24, 0.9); border-left: 4px solid #35D99A; border-radius: 6px; padding: 10px 16px; margin-bottom: 8px; font-size: 13px; color: #F8FAFC;">
                ⚡ <b>Action Item:</b> {item}
            </div>
            """,
            unsafe_allow_html=True,
        )

# Explicit Statistical Disclosure complying with Rule 6
st.markdown(
    """
    <div style="font-size: 11px; color: #9CAFA5; text-align: center; margin-top: 24px; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 6px;">
        🔍 <b>Statistical Transparency Notice:</b> All analytics, counts, durations, and spatial frequencies presented above are calculated directly
        from authenticated SQLite database records (<code>obstacle_reports</code>, <code>navigation_history</code>) and the topological graph dataset.
        No synthetic machine-learning predictions or artificial probabilities are simulated.
    </div>
    """,
    unsafe_allow_html=True,
)
