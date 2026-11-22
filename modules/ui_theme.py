"""Custom styling, shared themes, and centralized session state management for Streamlit UI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

import streamlit as st

from database.db_manager import DatabaseManager
from modules.accessibility import AccessibilityEngine
from modules.campus_map import CampusMap, load_campus_map
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder

# Color Palette Constants
PRIMARY_BG = "#07130F"
SECONDARY_BG = "#0D1F18"
CARD_BG = "#122820"
PRIMARY_GREEN = "#16A36A"
ACCENT_GREEN = "#35D99A"
SOFT_MINT = "#A7F3D0"
WHITE = "#F8FAFC"
SECONDARY_TEXT = "#9CAFA5"
WARNING = "#F5B942"
ERROR = "#F87171"
INFO = "#60A5FA"

__all__ = [
    "PRIMARY_BG",
    "SECONDARY_BG",
    "CARD_BG",
    "PRIMARY_GREEN",
    "ACCENT_GREEN",
    "SOFT_MINT",
    "WHITE",
    "SECONDARY_TEXT",
    "WARNING",
    "ERROR",
    "INFO",
    "get_app_services",
    "get_current_user",
    "login_user",
    "logout_user",
    "is_authenticated",
    "has_role",
    "apply_custom_theme",
    "apply_plotly_dark_theme",
    "render_kpi_card",
    "render_badge",
    "render_sidebar_info",
    "render_sidebar_user_pill",
    "render_sidebar_footer",
]


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
    """Clear authenticated user record and wipe all sensitive session-state variables."""
    st.session_state.current_user = None
    # Purge any transient user-specific or sensitive keys
    for k in list(st.session_state.keys()):
        if k.startswith(("user_", "auth_", "login_", "admin_")):
            st.session_state.pop(k, None)


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
    """Inject polished dark-forest-green, glassmorphism CSS styling and animations."""
    st.markdown(
        """
        <style>
        /* =====================================================================
           GLOBAL RESET & DARK GLASSMORPHISM BASE
           ===================================================================== */
        .stApp {
            background-color: #07130F !important;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(22, 163, 106, 0.08) 0%, transparent 60%),
                radial-gradient(circle at 100% 100%, rgba(13, 31, 24, 0.7) 0%, transparent 50%) !important;
            color: #F8FAFC !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        }

        /* Smooth fade-in motion for main block container */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(12px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .main .block-container {
            animation: fadeInUp 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
            max-width: 1200px !important;
            padding-top: 1.8rem !important;
            padding-bottom: 3.2rem !important;
        }

        /* Respect user preference for reduced motion */
        @media (prefers-reduced-motion: reduce) {
            *, .main .block-container, .ui-card, .step-box, [data-testid="stMetric"], .action-card {
                animation: none !important;
                transition: none !important;
            }
        }

        /* Headings & Text */
        h1, h2, h3, h4, h5, h6 {
            color: #F8FAFC !important;
            font-weight: 700 !important;
            letter-spacing: -0.4px !important;
        }
        p, span, label, div {
            color: #F8FAFC;
        }
        .text-muted {
            color: #9CAFA5 !important;
        }
        hr {
            border-color: rgba(53, 217, 154, 0.15) !important;
            margin: 1.8rem 0 !important;
        }

        /* =====================================================================
           SIDEBAR STYLING
           ===================================================================== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0D1F18 0%, #07130F 100%) !important;
            border-right: 1px solid rgba(53, 217, 154, 0.12) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
            color: #F8FAFC !important;
        }
        section[data-testid="stSidebar"] hr {
            border-color: rgba(53, 217, 154, 0.14) !important;
        }
        [data-testid="stSidebarNav"] a {
            border-radius: 8px !important;
            margin: 2px 8px !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stSidebarNav"] a:hover {
            background-color: rgba(53, 217, 154, 0.08) !important;
            transform: translateX(3px) !important;
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: linear-gradient(90deg, rgba(22, 163, 106, 0.25) 0%, rgba(53, 217, 154, 0.05) 100%) !important;
            border-left: 3px solid #35D99A !important;
            font-weight: 600 !important;
        }

        /* =====================================================================
           GLASSMORPHISM CARDS & CONTAINERS
           ===================================================================== */
        .ui-card {
            background: rgba(18, 40, 32, 0.72) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(53, 217, 154, 0.16) !important;
            border-radius: 14px !important;
            padding: 18px 22px !important;
            box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.45), inset 0 1px 1px rgba(167, 243, 208, 0.08) !important;
            margin-bottom: 14px !important;
            transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s ease, border-color 0.25s ease !important;
        }
        .ui-card:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 12px 28px -4px rgba(0, 0, 0, 0.6), 0 0 16px rgba(22, 163, 106, 0.2) !important;
            border-color: rgba(53, 217, 154, 0.35) !important;
        }
        .ui-card-title {
            font-size: 0.78rem !important;
            color: #9CAFA5 !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.8px !important;
            margin-bottom: 6px !important;
        }
        .ui-card-value {
            font-size: 2.1rem !important;
            font-weight: 700 !important;
            color: #F8FAFC !important;
            line-height: 1.15 !important;
            letter-spacing: -0.5px !important;
        }
        .ui-card-desc {
            font-size: 0.82rem !important;
            color: #9CAFA5 !important;
            margin-top: 6px !important;
            line-height: 1.4 !important;
        }

        /* Hero Banner */
        .hero-banner {
            background: linear-gradient(135deg, rgba(18, 40, 32, 0.9) 0%, rgba(13, 31, 24, 0.75) 100%) !important;
            border: 1px solid rgba(53, 217, 154, 0.25) !important;
            border-radius: 16px !important;
            padding: 24px 28px !important;
            margin-bottom: 22px !important;
            box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5), inset 0 1px 2px rgba(167, 243, 208, 0.15) !important;
        }
        .hero-title {
            font-size: 1.75rem !important;
            font-weight: 800 !important;
            color: #F8FAFC !important;
            margin-bottom: 6px !important;
            letter-spacing: -0.5px !important;
        }
        .hero-subtitle {
            font-size: 0.95rem !important;
            color: #9CAFA5 !important;
            line-height: 1.5 !important;
            max-width: 820px !important;
        }
        .hero-chips {
            margin-top: 14px !important;
        }
        .hero-chip {
            display: inline-block !important;
            background: rgba(53, 217, 154, 0.12) !important;
            color: #35D99A !important;
            border: 1px solid rgba(53, 217, 154, 0.25) !important;
            padding: 4px 10px !important;
            border-radius: 6px !important;
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            margin-right: 8px !important;
            margin-bottom: 4px !important;
        }

        /* Quick Action Navigation Cards */
        .action-card {
            background: rgba(18, 40, 32, 0.65) !important;
            border: 1px solid rgba(53, 217, 154, 0.18) !important;
            border-radius: 14px !important;
            padding: 18px 20px !important;
            margin-bottom: 12px !important;
            transition: all 0.22s ease !important;
        }
        .action-card:hover {
            transform: translateY(-2px) !important;
            border-color: #35D99A !important;
            box-shadow: 0 8px 20px rgba(22, 163, 106, 0.25) !important;
        }
        .action-card-icon {
            font-size: 1.6rem !important;
            margin-bottom: 8px !important;
        }
        .action-card-title {
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            color: #F8FAFC !important;
        }
        .action-card-desc {
            font-size: 0.8rem !important;
            color: #9CAFA5 !important;
            margin-top: 4px !important;
            line-height: 1.35 !important;
        }

        /* =====================================================================
           BUTTONS & FORM CONTROLS
           ===================================================================== */
        div.stButton > button {
            background: linear-gradient(135deg, #16A36A 0%, #117a4e 100%) !important;
            color: #F8FAFC !important;
            border: 1px solid rgba(53, 217, 154, 0.3) !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 9px 20px !important;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #19b375 0%, #16A36A 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 18px rgba(22, 163, 106, 0.4) !important;
            border-color: #35D99A !important;
        }
        div.stButton > button:active {
            transform: scale(0.98) !important;
        }

        /* Streamlit native metric overrides */
        [data-testid="stMetric"] {
            background: rgba(18, 40, 32, 0.65) !important;
            border: 1px solid rgba(53, 217, 154, 0.14) !important;
            border-radius: 12px !important;
            padding: 14px 18px !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
            transition: transform 0.2s ease, border-color 0.2s ease !important;
        }
        [data-testid="stMetric"]:hover {
            border-color: rgba(53, 217, 154, 0.3) !important;
            transform: translateY(-2px) !important;
        }
        [data-testid="stMetricValue"] {
            color: #F8FAFC !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricLabel"] {
            color: #9CAFA5 !important;
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }

        /* Form Inputs & Selects */
        div[data-baseweb="input"], div[data-baseweb="select"] {
            background-color: rgba(13, 31, 24, 0.8) !important;
            border: 1px solid rgba(53, 217, 154, 0.2) !important;
            border-radius: 10px !important;
            color: #F8FAFC !important;
        }
        div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
            border-color: #35D99A !important;
            box-shadow: 0 0 0 2px rgba(53, 217, 154, 0.25) !important;
        }

        /* =====================================================================
           STEP BOXES, BADGES & NOTICES
           ===================================================================== */
        .step-box {
            background: rgba(18, 40, 32, 0.72) !important;
            border: 1px solid rgba(53, 217, 154, 0.16) !important;
            border-left: 4px solid #35D99A !important;
            border-radius: 12px !important;
            padding: 14px 18px !important;
            margin-bottom: 12px !important;
            transition: transform 0.2s ease, border-color 0.2s ease !important;
        }
        .step-box:hover {
            transform: translateX(4px) !important;
            border-color: rgba(53, 217, 154, 0.35) !important;
        }
        .step-header {
            font-weight: 700 !important;
            color: #F8FAFC !important;
            font-size: 0.95rem !important;
        }
        .step-instruction {
            color: #A7F3D0 !important;
            font-size: 0.9rem !important;
            margin-top: 4px !important;
        }
        .step-meta {
            font-size: 0.8rem !important;
            color: #9CAFA5 !important;
            margin-top: 6px !important;
        }

        /* Disclaimer Notice */
        .disclaimer-banner {
            background: rgba(13, 31, 24, 0.7) !important;
            border: 1px solid rgba(53, 217, 154, 0.18) !important;
            border-left: 4px solid #16A36A !important;
            border-radius: 10px !important;
            padding: 14px 18px !important;
            font-size: 0.85rem !important;
            color: #9CAFA5 !important;
            line-height: 1.5 !important;
            margin: 16px 0 !important;
        }

        /* Status & Taxonomy Badges */
        .badge {
            display: inline-block !important;
            padding: 3px 10px !important;
            border-radius: 6px !important;
            font-size: 0.74rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.3px !important;
        }
        .badge-pending {
            background: rgba(245, 185, 66, 0.15) !important;
            color: #F5B942 !important;
            border: 1px solid rgba(245, 185, 66, 0.3) !important;
        }
        .badge-verified {
            background: rgba(248, 113, 113, 0.15) !important;
            color: #F87171 !important;
            border: 1px solid rgba(248, 113, 113, 0.3) !important;
        }
        .badge-resolved {
            background: rgba(53, 217, 154, 0.15) !important;
            color: #35D99A !important;
            border: 1px solid rgba(53, 217, 154, 0.3) !important;
        }
        .badge-rejected {
            background: rgba(156, 175, 165, 0.15) !important;
            color: #9CAFA5 !important;
            border: 1px solid rgba(156, 175, 165, 0.3) !important;
        }
        .badge-info {
            background: rgba(96, 165, 250, 0.15) !important;
            color: #60A5FA !important;
            border: 1px solid rgba(96, 165, 250, 0.3) !important;
        }

        /* Streamlit expander and table styling */
        .streamlit-expanderHeader {
            background-color: rgba(18, 40, 32, 0.5) !important;
            border-radius: 10px !important;
            color: #F8FAFC !important;
        }

        /* =====================================================================
           RESPONSIVE VIEWPORT BREAKPOINTS (360px to 1920px+)
           ===================================================================== */
        /* Mobile Breakpoint: 360px to 480px (Phones) */
        @media (max-width: 480px) {
            .main .block-container {
                padding-left: 0.8rem !important;
                padding-right: 0.8rem !important;
                padding-top: 1.0rem !important;
            }
            .ui-card {
                padding: 12px 14px !important;
                margin-bottom: 10px !important;
            }
            .ui-card-value {
                font-size: 1.45rem !important;
            }
            .ui-card-title {
                font-size: 0.72rem !important;
            }
            div.stButton > button {
                width: 100% !important;
                padding: 8px 14px !important;
                font-size: 0.88rem !important;
            }
            .step-box {
                padding: 10px 12px !important;
            }
            .step-header {
                font-size: 0.88rem !important;
            }
            .step-instruction {
                font-size: 0.82rem !important;
            }
        }

        /* Tablet Breakpoint: 481px to 768px */
        @media (min-width: 481px) and (max-width: 768px) {
            .main .block-container {
                padding-left: 1.2rem !important;
                padding-right: 1.2rem !important;
                padding-top: 1.2rem !important;
            }
            .ui-card {
                padding: 16px 18px !important;
            }
            .ui-card-value {
                font-size: 1.7rem !important;
            }
        }

        /* Laptop Breakpoint: 769px to 1024px */
        @media (min-width: 769px) and (max-width: 1024px) {
            .main .block-container {
                max-width: 960px !important;
            }
        }

        /* Standard Desktop Breakpoint: 1025px to 1440px */
        @media (min-width: 1025px) and (max-width: 1440px) {
            .main .block-container {
                max-width: 1200px !important;
            }
        }

        /* High-Resolution Wide Displays: 1441px to 1920px+ */
        @media (min-width: 1441px) {
            .main .block-container {
                max-width: 1400px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_plotly_dark_theme(fig: Any, height: Optional[int] = None) -> Any:
    """Apply unified dark green glassmorphism styling to a Plotly figure."""
    layout_args: Dict[str, Any] = {
        "paper_bgcolor": "rgba(0, 0, 0, 0)",
        "plot_bgcolor": "rgba(0, 0, 0, 0)",
        "font": dict(
            family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif",
            color="#F8FAFC",
            size=12,
        ),
        "margin": dict(t=25, b=25, l=25, r=25),
    }
    if height is not None:
        layout_args["height"] = height
    fig.update_layout(**layout_args)
    fig.update_xaxes(
        gridcolor="rgba(53, 217, 154, 0.08)",
        zerolinecolor="rgba(53, 217, 154, 0.12)",
        tickfont=dict(color="#9CAFA5"),
        title_font=dict(color="#F8FAFC"),
    )
    fig.update_yaxes(
        gridcolor="rgba(53, 217, 154, 0.08)",
        zerolinecolor="rgba(53, 217, 154, 0.12)",
        tickfont=dict(color="#9CAFA5"),
        title_font=dict(color="#F8FAFC"),
    )
    return fig


def render_kpi_card(
    title: str,
    value: Union[str, int, float],
    desc: str,
    border_accent: Optional[str] = None,
    value_color: Optional[str] = None,
) -> str:
    """Generate HTML string for a polished glassmorphism KPI card."""
    border_style = f"border-top: 3px solid {border_accent};" if border_accent else ""
    val_style = f"color: {value_color};" if value_color else "color: #F8FAFC;"
    return f"""
    <div class="ui-card" style="{border_style}">
        <div class="ui-card-title">{title}</div>
        <div class="ui-card-value" style="{val_style}">{value}</div>
        <div class="ui-card-desc">{desc}</div>
    </div>
    """


def render_badge(text: str, badge_type: str = "info") -> str:
    """Generate HTML string for a colored badge."""
    return f'<span class="badge badge-{badge_type}">{text}</span>'


def render_sidebar_info() -> None:
    """Render common project info and logo brand in the sidebar."""
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; padding: 12px 0 16px 0;">
                <div style="font-size: 2.3rem; margin-bottom: 4px; filter: drop-shadow(0 0 10px rgba(53, 217, 154, 0.3));">🧭</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.3px;">Accessible Campus</div>
                <div style="font-size: 0.76rem; color: #35D99A; letter-spacing: 1.2px; font-weight: 600; margin-top: 2px;">NAVIGATOR PRO</div>
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
                "Administrator": ("#8b5cf6", "🛡️ Administrator"),
                "Field Staff": ("#d97706", "🛠️ Field Staff"),
                "Student": ("#16a36a", "🎓 Campus User"),
            }
            bg_color, role_label = role_colors.get(role, ("#16a36a", role))

            st.markdown(
                f"""
                <div style="background: rgba(18, 40, 32, 0.75); border: 1px solid rgba(53, 217, 154, 0.2); border-radius: 10px; padding: 12px 14px; margin-bottom: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.3);">
                    <div style="font-size: 0.72rem; color: #9CAFA5; text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600;">Signed In As</div>
                    <div style="font-weight: 700; color: #F8FAFC; font-size: 0.95rem; margin-top: 2px;">{user.get('full_name')}</div>
                    <div style="font-size: 0.8rem; color: #35D99A; margin-bottom: 8px;">@{user.get('username')}</div>
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
                <div style="background: rgba(18, 40, 32, 0.5); border: 1px dashed rgba(53, 217, 154, 0.25); border-radius: 10px; padding: 12px 14px; margin-bottom: 12px; text-align: center;">
                    <div style="font-size: 0.85rem; font-weight: 600; color: #F8FAFC;">Guest Browsing Mode</div>
                    <div style="font-size: 0.75rem; color: #9CAFA5; margin-top: 4px;">Sign in to report obstacles or access staff tools</div>
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
            <div style="font-size: 0.74rem; color: #9CAFA5; line-height: 1.5; padding: 0 4px;">
                <b style="color: #35D99A;">Campus Navigator Pro</b><br>
                <b>Platform:</b> Streamlit & Python 3.14<br>
                <b>Security:</b> RBAC & PBKDF2 (600k) 🔒<br>
                <b>Status:</b> All Engines Operational ✅
            </div>
            """,
            unsafe_allow_html=True,
        )
