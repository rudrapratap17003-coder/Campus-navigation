"""Campus Intelligence and Accessibility Analytics Engine.

Provides evidence-based analytics, spatial distributions, obstacle metrics,
navigation telemetry, and administrative insights across the JAIN Global Campus
and FET 5-Floor Digital Twin based strictly on verified application records.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

from database.db_manager import DatabaseManager
from modules.campus_map import CampusMap
from modules.obstacle_manager import ObstacleManager


def compute_accessibility_analytics(
    campus_map: CampusMap,
    obstacle_manager: Optional[ObstacleManager] = None,
) -> Dict[str, Any]:
    """Calculate comprehensive accessibility statistics and information gaps across campus network.

    Args:
        campus_map: Active CampusMap instance.
        obstacle_manager: Optional ObstacleManager for live blocked pathway synchronization.

    Returns:
        Structured dictionary with location accessibility, pathway barriers, and gaps.
    """
    locations = campus_map.get_all_locations()
    total_locs = len(locations)

    accessible_locs = 0
    inaccessible_locs = 0
    unknown_locs = 0
    gaps_locs: List[str] = []

    for loc in locations:
        wa = loc.get("wheelchair_accessible")
        if wa is True:
            accessible_locs += 1
        elif wa is False:
            inaccessible_locs += 1
        else:
            unknown_locs += 1
            gaps_locs.append(loc["id"])

    # Pathways analysis
    edges = list(campus_map.graph.edges(data=True))
    total_pathways = len(edges)
    step_free_pathways = 0
    staircase_pathways = 0
    elevator_pathways = 0
    blocked_pathways = 0

    blocked_edges_set = set()
    if obstacle_manager is not None:
        blocked_edges_set = {
            (h.get("source_location_id"), h.get("destination_location_id"))
            for h in obstacle_manager.get_active_obstacles()
            if h.get("source_location_id") and h.get("destination_location_id")
        }

    for u, v, data in edges:
        is_blocked = (
            data.get("status") == "blocked"
            or (u, v) in blocked_edges_set
            or (v, u) in blocked_edges_set
        )
        if is_blocked:
            blocked_pathways += 1

        if data.get("has_elevator", False):
            elevator_pathways += 1
            step_free_pathways += 1
        elif data.get("has_stairs", False):
            staircase_pathways += 1
        elif data.get("wheelchair_accessible", True):
            step_free_pathways += 1

    acc_loc_pct = round((accessible_locs / total_locs * 100), 1) if total_locs > 0 else 0.0
    acc_path_pct = round((step_free_pathways / total_pathways * 100), 1) if total_pathways > 0 else 0.0

    return {
        "total_locations": total_locs,
        "accessible_locations": accessible_locs,
        "inaccessible_locations": inaccessible_locs,
        "unknown_accessibility_locations": unknown_locs,
        "location_accessibility_percentage": acc_loc_pct,
        "total_pathways": total_pathways,
        "step_free_pathways": step_free_pathways,
        "staircase_pathways": staircase_pathways,
        "elevator_pathways": elevator_pathways,
        "temporarily_blocked_pathways": blocked_pathways,
        "pathway_accessibility_percentage": acc_path_pct,
        "information_gaps_count": len(gaps_locs),
        "information_gap_node_ids": gaps_locs,
    }


def compute_obstacle_analytics(
    db_manager: DatabaseManager,
    campus_map: Optional[CampusMap] = None,
) -> Dict[str, Any]:
    """Calculate actual obstacle lifecycle metrics, resolution durations, and floor distributions.

    Args:
        db_manager: DatabaseManager instance.
        campus_map: Optional campus map for node floor mapping.

    Returns:
        Structured obstacle analytics dictionary.
    """
    reports = db_manager.get_all_reports()
    total_reports = len(reports)

    status_counts = {"Pending": 0, "Verified": 0, "Resolved": 0, "Rejected": 0}
    severity_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    floor_distribution: Dict[int, int] = {-1: 0, 0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    pathway_blocks: Dict[str, int] = {}
    resolution_durations_sec: List[float] = []

    loc_floor_map = {}
    if campus_map:
        for loc in campus_map.get_all_locations():
            loc_floor_map[loc["id"]] = int(loc.get("floor", 0))

    for r in reports:
        stt = r.get("status", "Pending")
        status_counts[stt] = status_counts.get(stt, 0) + 1

        sev = r.get("severity", "Medium")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

        # Pathway frequency
        u = r.get("source_location_id")
        v = r.get("destination_location_id")
        if u and v:
            edge_key = f"{min(u, v)} <-> {max(u, v)}"
            pathway_blocks[edge_key] = pathway_blocks.get(edge_key, 0) + 1

        # Floor distribution
        loc_id = r.get("location_id") or u or v
        if loc_id and loc_id in loc_floor_map:
            fl = loc_floor_map[loc_id]
            floor_distribution[fl] = floor_distribution.get(fl, 0) + 1

        # Resolution time calculation
        if stt == "Resolved" and r.get("reported_at") and r.get("updated_at"):
            try:
                t_rep = datetime.fromisoformat(r["reported_at"].replace("Z", "+00:00"))
                t_res = datetime.fromisoformat(r["updated_at"].replace("Z", "+00:00"))
                diff = (t_res - t_rep).total_seconds()
                if diff >= 0:
                    resolution_durations_sec.append(diff)
            except Exception:
                pass

    avg_resolution_hours = 0.0
    if resolution_durations_sec:
        avg_resolution_hours = round(sum(resolution_durations_sec) / len(resolution_durations_sec) / 3600.0, 2)

    top_blocked = sorted(pathway_blocks.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_reports": total_reports,
        "active_verified_obstacles": status_counts.get("Verified", 0),
        "pending_reports": status_counts.get("Pending", 0),
        "resolved_obstacles": status_counts.get("Resolved", 0),
        "rejected_reports": status_counts.get("Rejected", 0),
        "status_counts": status_counts,
        "severity_counts": severity_counts,
        "floor_distribution": floor_distribution,
        "average_resolution_time_hours": avg_resolution_hours,
        "frequently_blocked_pathways": top_blocked,
    }


def compute_navigation_analytics(db_manager: DatabaseManager) -> Dict[str, Any]:
    """Calculate aggregate navigation telemetry, popular destinations, and completion rates.

    Args:
        db_manager: DatabaseManager instance.

    Returns:
        Structured navigation telemetry analytics dictionary.
    """
    history = db_manager.get_navigation_history(limit=500) if hasattr(db_manager, "get_navigation_history") else []
    total_sessions = len(history)

    completed = 0
    cancelled = 0
    rerouted = 0
    total_dist = 0.0
    total_dur = 0.0
    floor_transitions = 0
    destinations_count: Dict[str, int] = {}
    mode_counts: Dict[str, int] = {"standard": 0, "wheelchair": 0}

    for s in history:
        status = s.get("completion_status", "completed")
        if status == "completed":
            completed += 1
        elif status == "cancelled":
            cancelled += 1

        if s.get("rerouted", 0) > 0:
            rerouted += 1

        total_dist += float(s.get("total_distance", 0.0))
        total_dur += float(s.get("estimated_duration", 0.0))
        floor_transitions += int(s.get("floor_transitions", 0))

        dest = s.get("destination", "Unknown")
        destinations_count[dest] = destinations_count.get(dest, 0) + 1

        mode = str(s.get("navigation_mode", "standard")).lower()
        if "wheelchair" in mode:
            mode_counts["wheelchair"] += 1
        else:
            mode_counts["standard"] += 1

    avg_dist = round(total_dist / total_sessions, 1) if total_sessions > 0 else 0.0
    avg_dur_min = round((total_dur / total_sessions) / 60.0, 1) if total_sessions > 0 else 0.0
    top_destinations = sorted(destinations_count.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_journeys": total_sessions,
        "completed_journeys": completed,
        "cancelled_journeys": cancelled,
        "completion_rate_percentage": round((completed / total_sessions * 100), 1) if total_sessions > 0 else 0.0,
        "rerouted_journeys": rerouted,
        "average_route_distance_m": avg_dist,
        "average_duration_minutes": avg_dur_min,
        "total_floor_transitions": floor_transitions,
        "mode_distribution": mode_counts,
        "top_destinations": top_destinations,
    }


def compute_administrative_insights(
    campus_map: CampusMap,
    db_manager: DatabaseManager,
    obstacle_manager: Optional[ObstacleManager] = None,
) -> Dict[str, Any]:
    """Compile high-level administrative operational insights, data verification progress, and action items.

    Args:
        campus_map: Active CampusMap instance.
        db_manager: DatabaseManager instance.
        obstacle_manager: Optional ObstacleManager.

    Returns:
        Structured administrative intelligence summary.
    """
    acc = compute_accessibility_analytics(campus_map, obstacle_manager)
    obs = compute_obstacle_analytics(db_manager, campus_map)
    nav = compute_navigation_analytics(db_manager)

    # Verification distribution
    verif_counts = {"VERIFIED": 0, "IMAGE_DERIVED": 0, "APPROXIMATE": 0, "UNVERIFIED": 0}
    for loc in campus_map.get_all_locations():
        v = loc.get("verification_status", "IMAGE_DERIVED")
        verif_counts[v] = verif_counts.get(v, 0) + 1

    total_locs = len(campus_map.get_all_locations())
    verified_pct = round(verif_counts["VERIFIED"] / total_locs * 100, 1) if total_locs > 0 else 0.0

    # Operational action items
    action_items: List[str] = []
    if obs["pending_reports"] > 0:
        action_items.append(f"Review {obs['pending_reports']} pending obstacle report(s) submitted by campus users.")
    if obs["active_verified_obstacles"] > 0:
        action_items.append(f"Coordinate field repair for {obs['active_verified_obstacles']} active pathway barrier(s).")
    if acc["information_gaps_count"] > 0:
        action_items.append(f"Audit {acc['information_gaps_count']} node(s) lacking verified wheelchair accessibility criteria.")
    if verified_pct < 20.0:
        action_items.append("Schedule on-site physical survey to upgrade IMAGE_DERIVED floor plan nodes to VERIFIED status.")

    return {
        "campus_accessibility_score": acc["location_accessibility_percentage"],
        "verification_progress_percentage": verified_pct,
        "verification_counts": verif_counts,
        "pending_obstacle_reviews": obs["pending_reports"],
        "active_maintenance_barriers": obs["active_verified_obstacles"],
        "action_items": action_items,
        "accessibility_summary": acc,
        "obstacle_summary": obs,
        "navigation_summary": nav,
    }
