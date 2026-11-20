"""Campus Map Page - Schematic connectivity visualization, floor filters, and location directory."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.ui_theme import apply_custom_theme, get_app_services

apply_custom_theme()
services = get_app_services()

cmap = services["campus_map"]
locations = cmap.get_all_locations()
graph = cmap.graph

st.title("🗺️ Schematic Campus Connectivity Visualization")
st.write(
    "Topological graph layout of campus locations, walkable connections, elevators, "
    "and access ramps for navigation testing."
)

# Mandatory Coordinate Disclaimer
st.warning(
    "⚠️ **Schematic Connectivity Layout Notice:** The node positions displayed below are "
    "**illustrative graph-layout coordinates** designed strictly for schematic connectivity "
    "and topological pathfinding visualization. They are **not geographically surveyed coordinates** "
    "and do **not** claim architectural scale or blueprint accuracy. Full architectural CAD floor plans "
    "and indoor GIS integration will be introduced in Phase 8."
)

# --- FLOOR FILTER & METRICS ---
col_fl, col_cat = st.columns([1, 2])
with col_fl:
    selected_floor = st.radio(
        "Select Floor View:",
        options=["All Floors", "Ground Floor (Floor 0)", "First Floor (Floor 1)"],
        index=0,
        horizontal=True,
    )

floor_filter = None
if selected_floor == "Ground Floor (Floor 0)":
    floor_filter = 0
elif selected_floor == "First Floor (Floor 1)":
    floor_filter = 1

# Filter locations based on floor selection
filtered_locs = [
    loc for loc in locations if floor_filter is None or loc["floor"] == floor_filter
]
filtered_node_ids = {loc["id"] for loc in filtered_locs}

# --- PLOTLY GRAPH VISUALIZATION ---
st.subheader("📍 Schematic Network Topology")

fig = go.Figure()

# Draw edges
for u, v, data in graph.edges(data=True):
    # Only draw if both endpoints are in filtered view (or inter-floor if all floors)
    if u in filtered_node_ids and v in filtered_node_ids:
        u_node = cmap.get_location(u)
        v_node = cmap.get_location(v)
        if not u_node or not v_node:
            continue

        x0, y0 = u_node["x"], u_node["y"]
        x1, y1 = v_node["x"], v_node["y"]

        # Color edge based on accessibility and status
        status = data.get("status", "open")
        is_acc = data.get("wheelchair_accessible", True)
        has_stairs = data.get("has_stairs", False)
        has_elevator = data.get("has_elevator", False)
        has_ramp = data.get("has_ramp", False)

        if status in ("blocked", "closed"):
            line_color = "#e63946"
            dash = "dash"
            edge_type = "Blocked Pathway"
        elif has_stairs and not is_acc:
            line_color = "#e76f51"
            dash = "dot"
            edge_type = "Stairs (Inaccessible)"
        elif has_elevator:
            line_color = "#2a9d8f"
            dash = "solid"
            edge_type = "Elevator Transition"
        elif has_ramp:
            line_color = "#40916c"
            dash = "solid"
            edge_type = "Access Ramp"
        else:
            line_color = "#52b788"
            dash = "solid"
            edge_type = "Accessible Corridor"

        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(color=line_color, width=3, dash=dash),
                hoverinfo="text",
                text=f"{edge_type}: {u_node['name']} ↔ {v_node['name']}<br>Traversable Distance: {data.get('distance')}m",
                showlegend=False,
            )
        )

# Draw nodes
df_nodes = pd.DataFrame(filtered_locs)
category_colors = {
    "entrance": "#1b4332",
    "lobby": "#2d6a4f",
    "elevator": "#2a9d8f",
    "stairs": "#e76f51",
    "restroom": "#457b9d",
    "classroom": "#3a86ff",
    "auditorium": "#8338ec",
    "cafeteria": "#f4a261",
    "lab": "#06d6a0",
    "library": "#118ab2",
    "office": "#073b4c",
}

for cat in df_nodes["category"].unique():
    cat_df = df_nodes[df_nodes["category"] == cat]
    color = category_colors.get(cat, "#4a5568")

    fig.add_trace(
        go.Scatter(
            x=cat_df["x"],
            y=cat_df["y"],
            mode="markers+text",
            marker=dict(size=16, color=color, line=dict(width=2, color="#ffffff")),
            text=cat_df["id"],
            textposition="top center",
            name=cat.capitalize(),
            hoverinfo="text",
            hovertext=[
                f"<b>[{row['id']}] {row['name']}</b><br>Floor: {row['floor']}<br>Building: {row['building']}<br>Category: {row['category'].capitalize()}<br>Layout Position: ({row['x']}, {row['y']})"
                for _, row in cat_df.iterrows()
            ],
        )
    )

fig.update_layout(
    height=480,
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(title="Schematic X Coordinate", showgrid=True, zeroline=False),
    yaxis=dict(title="Schematic Y Coordinate", showgrid=True, zeroline=False, scaleanchor="x"),
    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    plot_bgcolor="#fcfdfd",
)

st.plotly_chart(fig, use_container_width=True)

# Legend hint
st.caption(
    "🟢 Green: Accessible Corridors / Ramps | 🔵 Teal: Elevators | 🟠 Orange Dotted: Stairs | 🔴 Red Dashed: Blocked | Circles: Location Nodes"
)

st.markdown("---")

# --- LOCATIONS DIRECTORY TABLE ---
st.subheader("📋 Campus Locations Directory")
df_display = df_nodes[["id", "name", "building", "floor", "category", "x", "y"]].copy()
df_display.columns = ["ID", "Location Name", "Building", "Floor", "Category", "X (Layout)", "Y (Layout)"]
st.dataframe(df_display, use_container_width=True, hide_index=True)
