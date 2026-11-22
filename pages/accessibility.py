"""Accessibility Page - Systemic accessibility assessment, classifications, and infrastructure audits."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.accessibility import AccessibilityClassification
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

apply_custom_theme()
services = get_app_services()

st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">♿ Accessibility Intelligence & Infrastructure Audit</div>
        <div class="hero-subtitle">
            Comprehensive heuristic accessibility evaluation across all surveyed campus pathways,
            architectural connectors, and assistive mobility infrastructure.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Dataset Selector
c_acc1, c_acc2 = st.columns([2.6, 1.4])
with c_acc1:
    acc_env_choice = st.radio(
        "🏛️ Target Campus Model:",
        options=[
            "JAIN Global Campus & 5-Floor FET Building (79 Locations, 106 Pathways)",
            "Schematic Benchmark Model (15 Locations, 17 Pathways)",
        ],
        index=0,
        horizontal=True,
        key="accessibility_env_choice",
    )
is_jain = "JAIN" in acc_env_choice

from modules.jain_digital_twin import load_jain_campus_map
from modules.accessibility import AccessibilityEngine
cmap = load_jain_campus_map() if is_jain else services["campus_map"]
acc_engine = AccessibilityEngine(cmap)
summary = acc_engine.get_accessibility_summary()

# Mandatory Disclaimer
st.markdown(
    """
    <div class="disclaimer-banner">
        <b>⚖️ Heuristic Rating Disclaimer:</b> The accessibility scores (0–100) and classifications displayed here
        are algorithmic heuristics designed strictly for route selection and navigation planning.
        They do <b>not</b> constitute official, certified architectural, building-code, or ADA compliance ratings.
    </div>
    """,
    unsafe_allow_html=True,
)

# --- CLASSIFICATION TAXONOMY CARDS ---
st.markdown("### 📚 Standardized Accessibility Classification Framework")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """
        <div class="ui-card" style="border-left: 4px solid #35D99A;">
            <div style="font-weight: 700; color: #35D99A; margin-bottom: 6px; font-size: 1rem;">🟢 Fully Accessible</div>
            <div style="font-size: 0.84rem; color: #9CAFA5; line-height: 1.5;">
                Step-free, flat, or equipped with code-compliant access ramps or elevators. Completely barrier-free for independent wheelchair users.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """
        <div class="ui-card" style="border-left: 4px solid #F5B942;">
            <div style="font-weight: 700; color: #F5B942; margin-bottom: 6px; font-size: 1rem;">🟡 Accessible with Assistance</div>
            <div style="font-size: 0.84rem; color: #9CAFA5; line-height: 1.5;">
                Passable for wheelchairs, but features steep ramp gradients, heavy manual doors, or long continuous runs requiring assistance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        """
        <div class="ui-card" style="border-left: 4px solid #F87171;">
            <div style="font-weight: 700; color: #F87171; margin-bottom: 6px; font-size: 1rem;">🔴 Not Wheelchair Accessible</div>
            <div style="font-size: 0.84rem; color: #9CAFA5; line-height: 1.5;">
                Contains physical steps or staircases without an elevator or ramp alternative. Impassable for wheeled mobility devices.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

col4, col5 = st.columns(2)
with col4:
    st.markdown(
        """
        <div class="ui-card" style="border-left: 4px solid #EF4444;">
            <div style="font-weight: 700; color: #EF4444; margin-bottom: 6px; font-size: 1rem;">⛔ Temporarily Blocked</div>
            <div style="font-size: 0.84rem; color: #9CAFA5; line-height: 1.5;">
                Pathway is currently closed or impassable due to active maintenance, construction work, or verified hazard reports.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col5:
    st.markdown(
        """
        <div class="ui-card" style="border-left: 4px solid #9CAFA5;">
            <div style="font-weight: 700; color: #9CAFA5; margin-bottom: 6px; font-size: 1rem;">⚪ Unknown Accessibility</div>
            <div style="font-size: 0.84rem; color: #9CAFA5; line-height: 1.5;">
                Accessibility status is unverified or missing required physical attribute surveys in the dataset.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# --- NETWORK ACCESSIBILITY SUMMARY ---
st.markdown("### 📊 Campus Infrastructure Overview")
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Overall Accessibility Score", f"{summary['average_pathway_score']} / 100")
with m2:
    st.metric("Accessible Pathways", f"{summary['accessible_pathways']} / {summary['total_pathways']}")
with m3:
    st.metric("Elevator Connectors", f"{summary['elevator_pathways']} Hubs")
with m4:
    st.metric("Dedicated Access Ramps", f"{summary['ramp_pathways']} Ramps")

st.markdown("---")

# --- DETAILED PATHWAYS TABLE ---
st.markdown("### 🔍 Complete Pathway Accessibility Inventory")

pathway_records = []
for u, v, data in cmap.graph.edges(data=True):
    assessment = acc_engine.check_path_accessibility(u, v, data)
    u_name = cmap.get_location(u)["name"]
    v_name = cmap.get_location(v)["name"]
    pathway_records.append(
        {
            "Connection": f"{u} ↔ {v}",
            "Locations": f"{u_name} ↔ {v_name}",
            "Distance (m)": data.get("distance"),
            "Time (s)": data.get("estimated_time"),
            "Classification": assessment.classification,
            "Score": assessment.score,
            "Wheelchair Friendly": "Yes" if assessment.wheelchair_accessible else "No",
            "Has Ramp": "Yes" if assessment.has_ramp else "No",
            "Has Elevator": "Yes" if assessment.has_elevator else "No",
            "Has Stairs": "Yes" if assessment.has_stairs else "No",
            "Status": assessment.status.capitalize(),
        }
    )

df_pathways = pd.DataFrame(pathway_records)
st.dataframe(df_pathways, use_container_width=True, hide_index=True)

st.markdown("---")

# --- INDIVIDUAL LOCATION INSPECTOR ---
st.markdown("### 🎯 Single Location Accessibility Inspector")
loc_options = {
    f"[{loc['id']}] {loc['name']} (Floor {loc['floor']})": loc["id"]
    for loc in cmap.get_all_locations()
}
selected_loc_label = st.selectbox("Select Target Location to Inspect:", options=list(loc_options.keys()))
inspected_id = loc_options[selected_loc_label]

loc_assessment = acc_engine.check_location_accessibility(inspected_id)

col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric("Location Score", f"{loc_assessment.score} / 100")
with col_info2:
    st.metric("Classification", loc_assessment.classification)
with col_info3:
    st.metric(
        "Accessible Connections",
        f"{loc_assessment.accessible_connections} / {loc_assessment.total_connections}",
    )

amenities = []
if loc_assessment.has_accessible_restroom:
    amenities.append("♿ Accessible Restroom Facility")
if loc_assessment.is_elevator_hub:
    amenities.append("🛗 Multi-Floor Elevator Hub")
if loc_assessment.has_ramp_access:
    amenities.append("♿ Ramp-Equipped Entryway")

if amenities:
    st.success("Special Amenities Present: " + " · ".join(amenities))
else:
    st.info("Standard indoor campus node without dedicated mobility specialty fixtures.")

if loc_assessment.warnings:
    for w in loc_assessment.warnings:
        st.warning(f"⚠️ {w}")
