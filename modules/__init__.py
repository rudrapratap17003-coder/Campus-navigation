"""Core business logic and domain modules for Accessible Campus Navigator."""

from modules.accessibility import (
    AccessibilityClassification,
    AccessibilityEngine,
    LocationAccessibilityAssessment,
    PathAccessibilityAssessment,
    RouteAccessibilityAssessment,
)
from modules.campus_map import CampusDataValidationError, CampusMap, load_campus_map
from modules.indoor_map import (
    calculate_display_coordinates,
    create_indoor_map_figure,
    detect_cross_floor_transitions,
    get_connections_for_floor,
    get_floors_in_campus,
    get_locations_for_floor,
)
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder, RouteResult, RouteStep
from modules.ui_theme import (
    apply_custom_theme,
    get_app_services,
    get_current_user,
    has_role,
    is_authenticated,
    login_user,
    logout_user,
    render_sidebar_footer,
    render_sidebar_info,
    render_sidebar_user_pill,
)

__all__ = [
    "CampusMap",
    "CampusDataValidationError",
    "load_campus_map",
    "RouteFinder",
    "RouteResult",
    "RouteStep",
    "AccessibilityEngine",
    "AccessibilityClassification",
    "PathAccessibilityAssessment",
    "LocationAccessibilityAssessment",
    "RouteAccessibilityAssessment",
    "ObstacleManager",
    "get_app_services",
    "get_current_user",
    "login_user",
    "logout_user",
    "is_authenticated",
    "has_role",
    "apply_custom_theme",
    "render_sidebar_info",
    "render_sidebar_user_pill",
    "render_sidebar_footer",
    "get_floors_in_campus",
    "get_locations_for_floor",
    "get_connections_for_floor",
    "detect_cross_floor_transitions",
    "calculate_display_coordinates",
    "create_indoor_map_figure",
]
