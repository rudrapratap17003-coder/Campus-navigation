"""Accessibility Page - Systemic accessibility assessment, classifications, and infrastructure audits."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.accessibility import AccessibilityClassification
from modules.ui_theme import apply_custom_theme, get_app_services

apply_custom_theme()
services = get_app_services()

cmap = services["campus_map"]
acc_engine = services["accessibility_engine"]
summary = acc_engine.get_accessibility_summary()

st.title("♿ Accessibility Intelligence & Infrastructure Audit")
st.write(
    "Comprehensive accessibility evaluation across campus routes, pathway classifications, "
    "and assistive infrastructure."
)

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
st.subheader("📚 Standardized Accessibility Classification Framework")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """
        <div class="ui-card" style="border-left: 5px solid #2d6a4f;">
            <div style="font-weight: 700; color: #2d6a4f; margin-bottom: 4px;">🟢 Fully Accessible</div>
            <div style="font-size: 0.85rem; color: #4a5568;">
                Step-free, flat, or equipped with code-compliant access ramps or elevators. Completely barrier-free for independent wheelchair users.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """
        <div class="ui-card" style="border-left: 5px solid #f4a261;">
            <div style="font-weight: 700; color: #e76f51; margin-bottom: 4px;">🟡 Accessible with Assistance</div>
            <div style="font-size: 0.85rem; color: #4a5568;">
                Passable for wheelchairs, but features steep ramp gradients, heavy manual doors, or long continuous runs requiring assistance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        """
        <div class="ui-card" style="border-left: 5px solid #e63946;">
            <div style="font-weight: 700; color: #e63946; margin-bottom: 4px;">🔴 Not Wheelchair Accessible</div>
            <div style="font-size: 0.85rem; color: #4a5568;">
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
        <div class="ui-card" style="border-left: 5px solid #d90429;">
            <div style="font-weight: 700; color: #d90429; margin-bottom: 4px;">⛔ Temporarily Blocked</div>
            <div style="font-size: 0.85rem; color: #4a5568;">
                Pathway is currently closed or blocked due to active maintenance, construction work, or hazard reports.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col5:
    st.markdown(
        """
        <div class="ui-card" style="border-left: 5px solid #adb5bd;">
            <div style="font-weight: 700; color: #6c757d; margin-bottom: 4px;">⚪ Unknown Accessibility</div>
            <div style="font-size: 0.85rem; color: #4a5568;">
                Accessibility status is unverified or missing required physical attribute surveys in the dataset.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# --- NETWORK ACCESSIBILITY SUMMARY ---
st.subheader("📊 Campus Infrastructure Overview")
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Overall Accessibility Score", f"{summary['average_pathway_score']}/100")
with m2:
    st.metric("Accessible Pathways", f"{summary['accessible_pathways']} / {summary['total_pathways']}")
with m3:
    st.metric("Elevator Connectors", summary["elevator_pathways"])
with m4:
    st.metric("Access Ramps", summary["ramp_pathways"])

st.markdown("---")

# --- DETAILED PATHWAYS TABLE ---
st.subheader("🔍 Complete Pathway Accessibility Inventory")

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
st.subheader("🎯 Single Location Accessibility Inspector")
loc_options = {
    f"[{loc['id']}] {loc['name']} (Floor {loc['floor']})": loc["id"]
    for loc in cmap.get_all_locations()
}
selected_loc_label = st.selectbox("Inspect Location:", options=list(loc_options.keys()))
inspected_id = loc_options[selected_loc_label]

loc_assessment = acc_engine.check_location_accessibility(inspected_id)

col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric("Location Score", f"{loc_assessment.score}/100")
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
