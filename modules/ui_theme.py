"""Custom styling, shared themes, and centralized session state management for Streamlit UI."""

from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from database.db_manager import DatabaseManager
from modules.accessibility import AccessibilityEngine
from modules.campus_map import CampusMap, load_campus_map
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder


def get_app_services() -> Dict[str, Any]:
    """Retrieve or initialize shared singleton service instances stored in st.session_state.

    Ensures that graph mutations (such as dynamic obstacle blocking) are immediately
    reflected across all pages without duplicating graph instances.

    Returns:
        Dictionary containing campus_map, db_manager, obstacle_manager, route_finder, and accessibility_engine.
    """
    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    if "campus_map" not in st.session_state:
        campus_map = load_campus_map()
        db_manager = DatabaseManager()
        obstacle_manager = ObstacleManager(db_manager=db_manager, campus_map=campus_map)
        route_finder = RouteFinder(campus_map)
        accessibility_engine = AccessibilityEngine(campus_map)

        st.session_state.campus_map = campus_map
        st.session_state.db_manager = db_manager
        st.session_state.obstacle_manager = obstacle_manager
        st.session_state.route_finder = route_finder
        st.session_state.accessibility_engine = accessibility_engine

    return {
        "campus_map": st.session_state.campus_map,
        "db_manager": st.session_state.db_manager,
        "obstacle_manager": st.session_state.obstacle_manager,
        "route_finder": st.session_state.route_finder,
        "accessibility_engine": st.session_state.accessibility_engine,
    }


def get_current_user() -> Optional[Dict[str, Any]]:
    """Retrieve currently authenticated user record from session state, or None."""
    return st.session_state.get("current_user")


def login_user(user_dict: Dict[str, Any]) -> None:
    """Store authenticated user record in session state."""
    st.session_state.current_user = user_dict


def logout_user() -> None:
    """Clear authenticated user record from session state."""
    st.session_state.current_user = None


def is_authenticated() -> bool:
    """Check whether a user is currently logged into the session."""
    return st.session_state.get("current_user") is not None


def has_role(roles: Union[str, List[str], Tuple[str, ...]]) -> bool:
    """Check whether the active user possesses any of the specified roles."""
    user = get_current_user()
    if not user:
        return False
    if isinstance(roles, str):
        roles = [roles]
    return user.get("role") in roles


def apply_custom_theme() -> None:
    """Inject polished dark-forest-green and white CSS styling into the Streamlit session."""
    st.markdown(
        """
        <style>
        /* Dark forest-green sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #12291e !important;
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
            color: #e2ece6 !important;
        }
        section[data-testid="stSidebar"] hr {
            border-color: #244835 !important;
        }

        /* Clean metric card styles */
        .ui-card {
            background-color: #ffffff;
            border: 1px solid #e1ebe5;
            border-radius: 10px;
            padding: 16px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            margin-bottom: 12px;
        }
        .ui-card-title {
            font-size: 0.82rem;
            color: #4b6354;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        .ui-card-value {
            font-size: 1.85rem;
            font-weight: 700;
            color: #1b4332;
            line-height: 1.2;
        }
        .ui-card-desc {
            font-size: 0.8rem;
            color: #6c757d;
            margin-top: 4px;
        }

        /* Primary green button */
        div.stButton > button[kind="primary"],
        div.stButton > button:first-child {
            background-color: #2d6a4f !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 8px 18px !important;
            transition: all 0.2s ease !important;
        }
        div.stButton > button[kind="primary"]:hover,
        div.stButton > button:first-child:hover {
            background-color: #1b4332 !important;
            box-shadow: 0 4px 10px rgba(27, 67, 50, 0.2) !important;
        }

        /* Disclaimer notice */
        .disclaimer-banner {
            background-color: #f1f8f4;
            border-left: 4px solid #40916c;
            padding: 12px 18px;
            border-radius: 4px;
            font-size: 0.85rem;
            color: #1b4332;
            margin: 16px 0;
            line-height: 1.4;
        }

        /* Step cards for navigation */
        .step-box {
            background-color: #ffffff;
            border: 1px solid #d8f3dc;
            border-left: 5px solid #2d6a4f;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 10px;
        }
        .step-header {
            font-weight: 600;
            color: #1b4332;
            font-size: 0.95rem;
        }
        .step-instruction {
            color: #2d3748;
            font-size: 0.9rem;
            margin-top: 2px;
        }
        .step-meta {
            font-size: 0.78rem;
            color: #718096;
            margin-top: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_info() -> None:
    """Render common project info and logo brand in the sidebar."""
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; padding: 10px 0 16px 0;">
                <div style="font-size: 2.2rem; margin-bottom: 4px;">🧭</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff;">Accessible Campus</div>
                <div style="font-size: 0.8rem; color: #95d5b2; letter-spacing: 0.8px;">NAVIGATOR</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")


def render_sidebar_user_pill() -> None:
    """Render user profile information, role badge, and session controls in sidebar."""
    user = get_current_user()
    with st.sidebar:
        if user:
            role = user.get("role", "Student")
            role_colors = {
                "Administrator": ("#6f42c1", "🛡️ Administrator"),
                "Field Staff": ("#d97706", "🛠️ Field Staff"),
                "Student": ("#2d6a4f", "🎓 Campus User"),
            }
            bg_color, role_label = role_colors.get(role, ("#2d6a4f", role))

            st.markdown(
                f"""
                <div style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 8px; padding: 10px 14px; margin-bottom: 12px;">
                    <div style="font-size: 0.75rem; color: #95d5b2; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Signed In As</div>
                    <div style="font-weight: 700; color: #ffffff; font-size: 0.95rem; margin-top: 2px;">{user.get('full_name')}</div>
                    <div style="font-size: 0.8rem; color: #b7e4c7; margin-bottom: 6px;">@{user.get('username')}</div>
                    <span style="background-color: {bg_color}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; display: inline-block;">{role_label}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("🚪 Sign Out", key="sidebar_logout_btn", use_container_width=True):
                logout_user()
                st.rerun()
        else:
            st.markdown(
                """
                <div style="background: rgba(255, 255, 255, 0.05); border: 1px dashed rgba(255, 255, 255, 0.2); border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; text-align: center;">
                    <div style="font-size: 0.8rem; color: #b7e4c7;">Guest Browsing Mode</div>
                    <div style="font-size: 0.72rem; color: #95d5b2; margin-top: 2px;">Sign in to report barriers or access staff tools</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("---")


def render_sidebar_footer() -> None:
    """Render version and status footer in the sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            """
            <div style="font-size: 0.75rem; color: #74c69d; line-height: 1.4;">
                <b>Version:</b> 1.2 (Phase 9)<br>
                <b>Platform:</b> Streamlit & Python 3.14<br>
                <b>Security:</b> RBAC & PBKDF2 Enabled 🔒<br>
                <b>Status:</b> All Engines Operational ✅
            </div>
            """,
            unsafe_allow_html=True,
        )
