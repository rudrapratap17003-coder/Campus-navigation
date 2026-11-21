"""Accessible Campus Navigator - Streamlit Application Entrypoint.

Orchestrates multi-page routing, shared session services, and dark-forest-green theme.
"""

from __future__ import annotations

import streamlit as st

from modules.ui_theme import (
    apply_custom_theme,
    get_app_services,
    get_current_user,
    render_sidebar_footer,
    render_sidebar_info,
    render_sidebar_user_pill,
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
render_sidebar_user_pill()

# Identify authenticated user role
current_user = get_current_user()
user_role = current_user.get("role") if current_user else None

# Define page components
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
three_d_map_page = st.Page(
    "pages/3d_campus_map.py",
    title="3D Campus Map",
    icon="🏢",
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
auth_page = st.Page(
    "pages/login.py",
    title="Account & Sign In" if current_user else "Sign In / Register",
    icon="🔐",
)
admin_page = st.Page(
    "pages/admin_management.py",
    title="Administrative Console",
    icon="🛡️",
)

# Dynamically construct role-aware navigation structure
if user_role == "Administrator":
    nav_structure = {
        "Overview": [dashboard_page],
        "Navigation": [nav_route_page, map_page, three_d_map_page],
        "Accessibility & Operations": [accessibility_page, obstacles_page],
        "System Administration": [admin_page, auth_page],
    }
elif user_role in ("Field Staff", "Student"):
    nav_structure = {
        "Overview": [dashboard_page],
        "Navigation": [nav_route_page, map_page, three_d_map_page],
        "Accessibility & Operations": [accessibility_page, obstacles_page],
        "Account": [auth_page],
    }
else:
    # Unauthenticated / Guest Mode
    nav_structure = {
        "Account Access": [auth_page],
        "Overview": [dashboard_page],
        "Navigation": [nav_route_page, map_page, three_d_map_page],
        "Accessibility": [accessibility_page, obstacles_page],
    }

# Initialize multi-page router
pg = st.navigation(nav_structure)

render_sidebar_footer()

# Run the selected page
pg.run()
