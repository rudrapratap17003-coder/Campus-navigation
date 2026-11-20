"""Dynamic obstacle reporting, lifecycle management, and graph synchronization engine."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import secrets
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import networkx as nx

from database.db_manager import DatabaseError, DatabaseManager
from modules.campus_map import CampusMap, load_campus_map


class ObstacleManager:
    """Manages the full lifecycle of campus accessibility obstacle reports and synchronizes graph availability."""

    ALLOWED_CATEGORIES: Tuple[str, ...] = (
        "Blocked pathway",
        "Broken ramp",
        "Elevator unavailable",
        "Construction work",
        "Damaged flooring",
        "Temporary obstruction",
        "Other accessibility issue",
    )

    ALLOWED_SEVERITIES: Tuple[str, ...] = (
        "Low",
        "Medium",
        "High",
        "Critical",
    )

    ALLOWED_STATUSES: Tuple[str, ...] = (
        "Pending",
        "Verified",
        "Resolved",
        "Rejected",
    )

    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        campus_map: Optional[Union[CampusMap, nx.Graph]] = None,
    ) -> None:
        """Initialize ObstacleManager with database and campus graph connections.

        Args:
            db_manager: DatabaseManager instance for persistence. If None, default instance is created.
            campus_map: CampusMap instance or nx.Graph. If None, default CampusMap is loaded.
        """
        self.db: DatabaseManager = db_manager if db_manager is not None else DatabaseManager()

        if campus_map is None:
            self.campus_map: Optional[CampusMap] = load_campus_map()
            self.graph: nx.Graph = self.campus_map.graph
        elif isinstance(campus_map, CampusMap):
            self.campus_map = campus_map
            self.graph = campus_map.graph
        elif isinstance(campus_map, nx.Graph):
            self.campus_map = None
            self.graph = campus_map
        else:
            raise TypeError("campus_map must be an instance of CampusMap or nx.Graph.")

        # Preserved original state storage (never permanently overwrite raw JSON attributes)
        # Key: tuple(sorted([u, v])) -> Dict containing original status, etc.
        self._original_edge_states: Dict[Tuple[str, str], Dict[str, Any]] = {}
        # Key: node_id -> Dict containing original status, etc.
        self._original_node_states: Dict[str, Dict[str, Any]] = {}

        # Tracking active reports per edge/node: Key -> Set[report_id]
        self._edge_active_reports: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
        self._node_active_reports: Dict[str, Set[str]] = defaultdict(set)

        # Synchronize any existing active verified reports from database into the graph
        self.sync_active_obstacles_with_graph()

    def _normalize_edge_key(self, u: str, v: str) -> Tuple[str, str]:
        """Normalize an undirected edge key symmetrically."""
        return tuple(sorted([u, v]))

    def _validate_report_inputs(
        self,
        obstacle_category: str,
        severity: str,
        description: str,
        location_id: Optional[str] = None,
        source_location_id: Optional[str] = None,
        destination_location_id: Optional[str] = None,
    ) -> str:
        """Validate report attributes against schema constraints and graph integrity.

        Returns:
            Determined target_type ('location' or 'pathway').

        Raises:
            ValueError: If any input fails validation.
        """
        if not obstacle_category or obstacle_category not in self.ALLOWED_CATEGORIES:
            raise ValueError(
                f"Invalid obstacle_category '{obstacle_category}'. Must be one of: {', '.join(self.ALLOWED_CATEGORIES)}."
            )

        if not severity or severity not in self.ALLOWED_SEVERITIES:
            raise ValueError(
                f"Invalid severity '{severity}'. Must be one of: {', '.join(self.ALLOWED_SEVERITIES)}."
            )

        if not description or not str(description).strip():
            raise ValueError("Report description cannot be empty.")

        is_pathway = bool(source_location_id and destination_location_id)
        is_location = bool(location_id)

        if not is_pathway and not is_location:
            raise ValueError(
                "Report must specify either a location_id or both source_location_id and destination_location_id."
            )

        if is_pathway:
            src = str(source_location_id)
            dst = str(destination_location_id)
            if src == dst:
                raise ValueError(f"Self-loop pathway obstacle ({src} -> {dst}) is invalid.")

            if src not in self.graph:
                raise ValueError(
                    f"Source location '{src}' does not exist in the campus network graph."
                )
            if dst not in self.graph:
                raise ValueError(
                    f"Destination location '{dst}' does not exist in the campus network graph."
                )
            if not self.graph.has_edge(src, dst):
                raise ValueError(
                    f"Pathway connection between '{src}' and '{dst}' does not exist in campus map."
                )
            return "pathway"

        loc = str(location_id)
        if loc not in self.graph:
            raise ValueError(f"Location ID '{loc}' does not exist in the campus network graph.")
        return "location"

    def submit_report(
        self,
        obstacle_category: str,
        severity: str,
        description: str,
        location_id: Optional[str] = None,
        source_location_id: Optional[str] = None,
        destination_location_id: Optional[str] = None,
        reporter_name: Optional[str] = None,
        report_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Submit a new obstacle report into the database with validation.

        Args:
            obstacle_category: One of ALLOWED_CATEGORIES.
            severity: One of ALLOWED_SEVERITIES.
            description: Clear text describing the obstruction.
            location_id: Optional location ID for a point obstruction.
            source_location_id: Optional pathway source endpoint.
            destination_location_id: Optional pathway destination endpoint.
            reporter_name: Optional reporter name or identifier (defaults to 'Anonymous').
            report_id: Optional custom report ID.

        Returns:
            Dictionary representation of the saved obstacle report.
        """
        target_type = self._validate_report_inputs(
            obstacle_category=obstacle_category,
            severity=severity,
            description=description,
            location_id=location_id,
            source_location_id=source_location_id,
            destination_location_id=destination_location_id,
        )

        now_iso = datetime.now(timezone.utc).isoformat()
        if not report_id:
            time_part = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            report_id = f"REP-{time_part}-{secrets.token_hex(2).upper()}"

        report_data = {
            "report_id": report_id,
            "location_id": location_id,
            "source_location_id": source_location_id,
            "destination_location_id": destination_location_id,
            "target_type": target_type,
            "obstacle_category": obstacle_category,
            "description": description.strip(),
            "severity": severity,
            "reported_at": now_iso,
            "reporter_name": reporter_name.strip() if reporter_name else "Anonymous",
            "status": "Pending",  # Pending reports do not automatically block pathways
            "resolution_notes": None,
            "updated_at": now_iso,
        }

        self.db.insert_report(report_data)
        return report_data

    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single report by its unique ID."""
        return self.db.get_report_by_id(report_id)

    def get_all_reports(self) -> List[Dict[str, Any]]:
        """Retrieve all recorded obstacle reports."""
        return self.db.get_all_reports()

    def get_reports_by_location(self, location_id: str) -> List[Dict[str, Any]]:
        """Retrieve all reports associated with a specific location."""
        return self.db.get_reports_by_location(location_id)

    def get_reports_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Retrieve reports filtered by status (Pending, Verified, Resolved, Rejected)."""
        if status not in self.ALLOWED_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of: {', '.join(self.ALLOWED_STATUSES)}."
            )
        return self.db.get_reports_by_status(status)

    def get_active_obstacles(self) -> List[Dict[str, Any]]:
        """Retrieve all verified, active obstacles."""
        return self.db.get_active_reports()

    def update_report_status(
        self,
        report_id: str,
        status: str,
        resolution_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update report status and synchronize graph operational state accordingly.

        Args:
            report_id: Unique identifier of the report.
            status: Target status ('Pending', 'Verified', 'Resolved', 'Rejected').
            resolution_notes: Optional resolution notes or rejection reason.

        Returns:
            Updated report dictionary.

        Raises:
            ValueError: If report_id is not found or status is invalid.
        """
        if status not in self.ALLOWED_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of: {', '.join(self.ALLOWED_STATUSES)}."
            )

        report = self.db.get_report_by_id(report_id)
        if not report:
            raise ValueError(f"Report with ID '{report_id}' was not found.")

        previous_status = report["status"]
        success = self.db.update_report_status(report_id, status, resolution_notes)
        if not success:
            raise DatabaseError(f"Failed to update report status for '{report_id}'.")

        updated_report = self.db.get_report_by_id(report_id)
        assert updated_report is not None

        # Synchronize live graph availability based on status transitions
        if status == "Verified" and previous_status != "Verified":
            self.apply_obstacle_to_graph(updated_report)
        elif previous_status == "Verified" and status in ("Resolved", "Rejected", "Pending"):
            self.remove_obstacle_from_graph(updated_report)

        return updated_report

    def verify_report(self, report_id: str) -> Dict[str, Any]:
        """Confirm and verify an obstacle report, marking the affected pathway/location as blocked."""
        return self.update_report_status(report_id, "Verified")

    def resolve_report(self, report_id: str, resolution_notes: str) -> Dict[str, Any]:
        """Resolve an obstacle report, restoring the pathway's original operational availability."""
        if not resolution_notes or not str(resolution_notes).strip():
            raise ValueError("Resolution notes are required when resolving an obstacle report.")
        return self.update_report_status(report_id, "Resolved", resolution_notes.strip())

    def reject_report(self, report_id: str, rejection_reason: Optional[str] = None) -> Dict[str, Any]:
        """Reject an invalid or unsubstantiated report, ensuring it does not block navigation."""
        notes = (
            rejection_reason.strip()
            if rejection_reason
            else "Report was reviewed and rejected as invalid or duplicate."
        )
        return self.update_report_status(report_id, "Rejected", notes)

    def apply_obstacle_to_graph(self, report: Dict[str, Any]) -> None:
        """Apply temporary blocked operational status to the live campus graph without data loss."""
        rep_id = report["report_id"]
        target_type = report.get("target_type")

        if target_type == "pathway":
            src = report.get("source_location_id")
            dst = report.get("destination_location_id")
            if not src or not dst or not self.graph.has_edge(src, dst):
                return

            edge_key = self._normalize_edge_key(src, dst)
            # Store original operational status if not already saved
            if edge_key not in self._original_edge_states:
                edge_data = self.graph.get_edge_data(src, dst) or {}
                self._original_edge_states[edge_key] = {
                    "status": edge_data.get("status", "open")
                }

            # Apply blocked status to graph edge
            self.graph[src][dst]["status"] = "blocked"
            self._edge_active_reports[edge_key].add(rep_id)

        elif target_type == "location":
            loc_id = report.get("location_id")
            if not loc_id or loc_id not in self.graph:
                return

            if loc_id not in self._original_node_states:
                self._original_node_states[loc_id] = {
                    "status": self.graph.nodes[loc_id].get("status", "open")
                }

            self.graph.nodes[loc_id]["status"] = "blocked"
            self._node_active_reports[loc_id].add(rep_id)

            # Also temporarily block all incident edges connected to the unavailable node
            for neighbor in list(self.graph.neighbors(loc_id)):
                edge_key = self._normalize_edge_key(loc_id, neighbor)
                if edge_key not in self._original_edge_states:
                    edge_data = self.graph.get_edge_data(loc_id, neighbor) or {}
                    self._original_edge_states[edge_key] = {
                        "status": edge_data.get("status", "open")
                    }
                self.graph[loc_id][neighbor]["status"] = "blocked"
                self._edge_active_reports[edge_key].add(rep_id)

    def remove_obstacle_from_graph(self, report: Dict[str, Any]) -> None:
        """Remove an obstacle from the graph and restore original operational status if no other reports remain."""
        rep_id = report["report_id"]
        target_type = report.get("target_type")

        if target_type == "pathway":
            src = report.get("source_location_id")
            dst = report.get("destination_location_id")
            if not src or not dst:
                return

            edge_key = self._normalize_edge_key(src, dst)
            if rep_id in self._edge_active_reports.get(edge_key, set()):
                self._edge_active_reports[edge_key].remove(rep_id)

            # If no other active verified reports affect this edge, restore original status
            if len(self._edge_active_reports.get(edge_key, set())) == 0:
                original = self._original_edge_states.pop(edge_key, {"status": "open"})
                if self.graph.has_edge(src, dst):
                    self.graph[src][dst]["status"] = original.get("status", "open")

        elif target_type == "location":
            loc_id = report.get("location_id")
            if not loc_id:
                return

            if rep_id in self._node_active_reports.get(loc_id, set()):
                self._node_active_reports[loc_id].remove(rep_id)

            if len(self._node_active_reports.get(loc_id, set())) == 0:
                original_node = self._original_node_states.pop(loc_id, {"status": "open"})
                if loc_id in self.graph:
                    self.graph.nodes[loc_id]["status"] = original_node.get("status", "open")

            # Restore incident edges if no other reports block them
            if loc_id in self.graph:
                for neighbor in list(self.graph.neighbors(loc_id)):
                    edge_key = self._normalize_edge_key(loc_id, neighbor)
                    if rep_id in self._edge_active_reports.get(edge_key, set()):
                        self._edge_active_reports[edge_key].remove(rep_id)
                    if len(self._edge_active_reports.get(edge_key, set())) == 0:
                        if edge_key in self._original_edge_states:
                            original_edge = self._original_edge_states.pop(
                                edge_key, {"status": "open"}
                            )
                            if self.graph.has_edge(loc_id, neighbor):
                                self.graph[loc_id][neighbor]["status"] = original_edge.get(
                                    "status", "open"
                                )

    def sync_active_obstacles_with_graph(self) -> None:
        """Query all verified active reports and apply their temporary blocked state to the campus graph."""
        active_reports = self.get_active_obstacles()
        for report in active_reports:
            self.apply_obstacle_to_graph(report)

    def get_active_blocked_edges(self) -> Set[Tuple[str, str]]:
        """Return the set of all currently blocked edge tuples (bidirectional)."""
        blocked_set: Set[Tuple[str, str]] = set()
        for (u, v), reports in self._edge_active_reports.items():
            if reports:
                blocked_set.add((u, v))
                blocked_set.add((v, u))
        return blocked_set

    def get_active_blocked_nodes(self) -> Set[str]:
        """Return the set of all currently blocked node IDs."""
        return {node_id for node_id, reports in self._node_active_reports.items() if reports}

    def get_obstacle_statistics(self) -> Dict[str, Any]:
        """Retrieve aggregated obstacle reporting statistics."""
        return self.db.get_statistics()
