"""Accessible Campus Navigator - Streamlit Application Entrypoint.

Orchestrates multi-page routing, shared session services, and dark-forest-green theme.
"""

from __future__ import annotations

import streamlit as st

from modules.ui_theme import (
    apply_custom_theme,
    get_app_services,
    render_sidebar_footer,
    render_sidebar_info,
)

# Configure global page parameters
st.set_page_config(
    page_title="Accessible Campus Navigator",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize shared singleton state and inject custom stylesheet
get_app_services()
apply_custom_theme()
render_sidebar_info()

# Define navigation structure
dashboard_page = st.Page(
    "pages/dashboard.py",
    title="Dashboard",
    icon="📊",
    default=True,
)
nav_route_page = st.Page(
    "pages/navigation.py",
    title="Find Accessible Route",
    icon="🧭",
)
map_page = st.Page(
    "pages/campus_map.py",
    title="Campus Map",
    icon="🗺️",
)
accessibility_page = st.Page(
    "pages/accessibility.py",
    title="Accessibility Overview",
    icon="♿",
)
obstacles_page = st.Page(
    "pages/obstacle_reports.py",
    title="Obstacle Reports",
    icon="⚠️",
)

# Initialize multi-page router
pg = st.navigation(
    {
        "Overview": [dashboard_page],
        "Navigation": [nav_route_page, map_page],
        "Accessibility & Operations": [accessibility_page, obstacles_page],
    }
)

render_sidebar_footer()

# Run the selected page
pg.run()
