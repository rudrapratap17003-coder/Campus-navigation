"""Comprehensive validation test suite for Phase 16: Campus Data Accuracy, Digital Twin Realism & Navigation Intelligence.

Tests cover:
- Category A: Campus data integrity (79 locations, 106 connections, unique IDs, positive distances/times).
- Category B: Data verification classification (VERIFIED, IMAGE_DERIVED, APPROXIMATE, UNVERIFIED).
- Category C: Spatial vertical alignment (invariance of elevator and cardinal stairwells across 5 floors).
- Category D: Destination search intelligence (abbreviations, aliases, departments, categories, floor grouping, autocomplete).
- Category E: Room-to-room navigation accuracy & wheelchair accessibility constraints.
- Category F: Direction and orientation intelligence (bearings, 8 cardinal directions, turn angles).
- Category G: Navigation session reliability & edge cases (cancel, restart, reroute, unreachable).
- Category H: Persistent navigation history in SQLite & user isolation.
- Category I: Administrative governance & audit trail logging.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Dict, List

from database.db_manager import DatabaseManager
from modules.campus_map import CampusMap, load_campus_map
from modules.destination_search import (
    DestinationSearchResult,
    get_search_suggestions,
    group_destinations_by_building_and_floor,
    search_destinations,
)
from modules.jain_digital_twin import (
    FLOOR_NAMES,
    build_jain_digital_twin_payload,
    get_jain_multi_route_comparison,
    load_jain_campus_map,
)
from modules.navigation_instructions import (
    CARDINAL_DIRECTIONS,
    NavigationInstruction,
    compute_bearing_and_cardinal,
    compute_turn_angle,
    format_floor_name,
    generate_turn_by_turn_instructions,
)
from modules.navigation_session import NavigationSession, NavigationState
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder


class TestPhase16DataAccuracyAndIntelligence(unittest.TestCase):
    """Test suite validating Phase 16 campus data accuracy, orientation, and navigation intelligence."""

    def setUp(self) -> None:
        """Initialize in-memory database and campus map instance."""
        self.db_mgr = DatabaseManager(":memory:")
        self.cmap = load_jain_campus_map()
        self.obs_mgr = ObstacleManager(db_manager=self.db_mgr, campus_map=self.cmap)
        self.rf = RouteFinder(self.cmap)

    def tearDown(self) -> None:
        """Close database connection."""
        self.db_mgr.close()

    # =========================================================================
    # CATEGORY A: Campus Data Integrity
    # =========================================================================

    def test_campus_data_counts(self) -> None:
        """Verify exactly 79 locations and 106 connections exist in campus graph."""
        locations = self.cmap.get_all_locations()
        self.assertEqual(len(locations), 79, "Expected exactly 79 campus locations.")
        self.assertEqual(self.cmap.graph.number_of_nodes(), 79, "Expected 79 nodes in NetworkX graph.")
        self.assertEqual(self.cmap.graph.number_of_edges(), 106, "Expected 106 undirected edges in graph.")

    def test_all_connections_have_valid_endpoints_and_metrics(self) -> None:
        """Verify all connections have valid endpoints, unique IDs, positive distance, and time."""
        loc_ids = set(self.cmap.locations.keys())
        conn_ids = set()

        for u, v, data in self.cmap.graph.edges(data=True):
            self.assertIn(u, loc_ids, f"Source node '{u}' not in locations.")
            self.assertIn(v, loc_ids, f"Destination node '{v}' not in locations.")
            self.assertGreater(data.get("distance", 0.0), 0.0, f"Distance between {u} and {v} must be > 0.")
            self.assertGreater(data.get("estimated_time", 0.0), 0.0, f"Time between {u} and {v} must be > 0.")

            conn_id = data.get("id")
            self.assertIsNotNone(conn_id, f"Connection between {u} and {v} missing ID.")
            self.assertNotIn(conn_id, conn_ids, f"Duplicate connection ID '{conn_id}'.")
            conn_ids.add(conn_id)

    # =========================================================================
    # CATEGORY B: Data Verification & Confidence Framework
    # =========================================================================

    def test_location_verification_framework(self) -> None:
        """Verify location verification classifications, sources, and confidence metadata."""
        locations = self.cmap.get_all_locations()
        verified_count = 0
        image_derived_count = 0

        for loc in locations:
            status = loc.get("verification_status")
            self.assertIn(
                status,
                {"VERIFIED", "IMAGE_DERIVED", "APPROXIMATE", "UNVERIFIED"},
                f"Location {loc['id']} has invalid verification status: {status}",
            )
            self.assertIn("verification_source", loc, f"Location {loc['id']} missing verification_source.")
            self.assertIn("confidence_level", loc, f"Location {loc['id']} missing confidence_level.")
            self.assertIn("last_verified", loc, f"Location {loc['id']} missing last_verified.")
            self.assertIn("verification_notes", loc, f"Location {loc['id']} missing verification_notes.")

            if status == "VERIFIED":
                verified_count += 1
            elif status == "IMAGE_DERIVED":
                image_derived_count += 1

        # Check Main Entrance is VERIFIED
        main_gate = self.cmap.get_location("OUT_GATE_MAIN")
        self.assertIsNotNone(main_gate)
        self.assertEqual(main_gate.get("verification_status"), "VERIFIED")
        self.assertEqual(main_gate.get("confidence_level"), "High")

        self.assertEqual(verified_count, 1)
        self.assertEqual(image_derived_count, 78)

    def test_connection_verification_framework(self) -> None:
        """Verify pathway verification classifications: 16 outdoor APPROXIMATE, 90 indoor IMAGE_DERIVED."""
        approximate_count = 0
        image_derived_count = 0

        for u, v, data in self.cmap.graph.edges(data=True):
            status = data.get("verification_status")
            self.assertIn(
                status,
                {"VERIFIED", "IMAGE_DERIVED", "APPROXIMATE", "UNVERIFIED"},
                f"Connection {u} -> {v} has invalid status: {status}",
            )
            self.assertIn("measurement_source", data, f"Connection {u} -> {v} missing measurement_source.")
            self.assertIn("confidence_level", data, f"Connection {u} -> {v} missing confidence_level.")

            if status == "APPROXIMATE":
                approximate_count += 1
            elif status == "IMAGE_DERIVED":
                image_derived_count += 1

        self.assertEqual(approximate_count, 16, "Expected exactly 16 outdoor connections marked APPROXIMATE.")
        self.assertEqual(image_derived_count, 90, "Expected exactly 90 indoor connections marked IMAGE_DERIVED.")

    # =========================================================================
    # CATEGORY C: Spatial Vertical Alignment Invariance
    # =========================================================================

    def test_elevator_vertical_alignment_invariance(self) -> None:
        """Verify elevator shaft coordinates are perfectly invariant (X=-6.0, Y=18.0) across all 5 tiers."""
        elevator_ids = [
            "FET_0F_ELEVATOR",
            "FET_1F_ELEVATOR",
            "FET_2F_ELEVATOR",
            "FET_3F_ELEVATOR",
            "FET_4F_ELEVATOR",
        ]
        target_x = -6.0
        target_y = 18.0

        for elev_id in elevator_ids:
            loc = self.cmap.get_location(elev_id)
            self.assertIsNotNone(loc, f"Elevator node '{elev_id}' missing.")
            self.assertAlmostEqual(
                float(loc.get("x", 0.0)),
                target_x,
                places=3,
                msg=f"Elevator '{elev_id}' X displacement detected.",
            )
            self.assertAlmostEqual(
                float(loc.get("y", 0.0)),
                target_y,
                places=3,
                msg=f"Elevator '{elev_id}' Y displacement detected.",
            )

    def test_cardinal_stairwells_vertical_alignment_invariance(self) -> None:
        """Verify 4 cardinal stairwells are invariant across Floors 0 through 4."""
        stair_specs = {
            "SOUTH": (6.0, 20.0),
            "NORTH": (0.0, -22.0),
            "EAST": (22.0, 0.0),
            "WEST": (-22.0, 0.0),
        }
        floors = ["0F", "1F", "2F", "3F", "4F"]

        for direction, (expected_x, expected_y) in stair_specs.items():
            for fl in floors:
                node_id = f"FET_{fl}_STAIRS_{direction}"
                loc = self.cmap.get_location(node_id)
                self.assertIsNotNone(loc, f"Stairwell '{node_id}' missing.")
                self.assertAlmostEqual(
                    float(loc.get("x", 0.0)),
                    expected_x,
                    places=3,
                    msg=f"Stairwell '{node_id}' X displacement.",
                )
                self.assertAlmostEqual(
                    float(loc.get("y", 0.0)),
                    expected_y,
                    places=3,
                    msg=f"Stairwell '{node_id}' Y displacement.",
                )

    # =========================================================================
    # CATEGORY D: Destination Search Intelligence
    # =========================================================================

    def test_search_destinations_queries(self) -> None:
        """Verify search intelligence across room names, departments, categories, and aliases."""
        test_queries = [
            ("AI Lab", "FET_1F_CS_LAB_101"),
            ("HPC", "FET_4F_HPC_CLUSTER"),
            ("Library", "FET_1F_LIBRARY"),
            ("Robotics", "FET_3F_ROBOTICS_LAB"),
            ("Seminar Hall", "FET_G_SEMINAR_01"),
            ("Mechanical Lab", "FET_G_MECH_LAB"),
        ]

        for query, expected_id in test_queries:
            results = search_destinations(query, self.cmap, limit=5)
            self.assertGreater(len(results), 0, f"Expected results for query '{query}'.")
            found_ids = [r.location_id for r in results]
            self.assertIn(expected_id, found_ids, f"Expected '{expected_id}' for query '{query}'.")

    def test_search_destinations_case_insensitivity_and_filtering(self) -> None:
        """Verify case-insensitivity and department/floor filtering in destination search."""
        # Case insensitivity
        res_lower = search_destinations("hpc cluster", self.cmap)
        res_upper = search_destinations("HPC CLUSTER", self.cmap)
        self.assertEqual(len(res_lower), len(res_upper))
        self.assertEqual(res_lower[0].location_id, res_upper[0].location_id)

        # Floor filtering
        res_fl4 = search_destinations("lab", self.cmap, floor_filter=4)
        for r in res_fl4:
            self.assertEqual(r.floor, 4)

        # Category filtering
        res_facility = search_destinations("sports", self.cmap, category_filter="sports")
        self.assertTrue(all(r.category == "sports" for r in res_facility))

    def test_group_destinations_and_suggestions(self) -> None:
        """Verify building/floor grouping and autocomplete search suggestions."""
        locs = self.cmap.get_all_locations()
        grouped = group_destinations_by_building_and_floor(locs)
        self.assertIn("FET Engineering", grouped)
        self.assertIn("Campus Grounds", grouped)
        self.assertIn("Fourth Floor", grouped["FET Engineering"])

        suggestions = get_search_suggestions("comp", self.cmap)
        self.assertGreater(len(suggestions), 0)

    # =========================================================================
    # CATEGORY E: Navigation Accuracy & Accessibility Constraints
    # =========================================================================

    def test_wheelchair_routing_avoids_stairs_and_uses_elevators(self) -> None:
        """Verify wheelchair route strictly avoids stairs and utilizes elevator vertical connectors."""
        route = self.rf.find_route(
            source="OUT_GATE_MAIN",
            destination="FET_4F_HPC_CLUSTER",
            algorithm="dijkstra",
            wheelchair_accessible=True,
        )
        self.assertIsNotNone(route)
        self.assertTrue(route.success)
        self.assertTrue(route.is_accessible)

        # Confirm elevator is used and vertical stairs are strictly avoided
        has_elevator = any(s.has_elevator for s in route.steps)
        has_stairs = any(s.has_stairs for s in route.steps)
        self.assertTrue(has_elevator, "Wheelchair multi-floor route must utilize elevator.")
        self.assertFalse(has_stairs, "Wheelchair route must strictly avoid stair segments.")

    def test_room_to_room_same_floor_navigation(self) -> None:
        """Verify room-to-room navigation between facilities on the same floor."""
        route = self.rf.find_route(
            source="FET_3F_ROBOTICS_LAB",
            destination="FET_3F_AVIONICS_LAB",
            algorithm="dijkstra",
            wheelchair_accessible=True,
        )
        self.assertIsNotNone(route)
        self.assertTrue(route.success)
        # All nodes should be on Floor 3
        for node_id in route.path:
            loc = self.cmap.get_location(node_id)
            self.assertEqual(int(loc.get("floor", 0)), 3)

    # =========================================================================
    # CATEGORY F: Direction and Orientation Intelligence
    # =========================================================================

    def test_bearing_and_cardinal_calculations(self) -> None:
        """Verify bearing (0-360) and cardinal direction calculations."""
        # North (-Z)
        u = {"x": 0.0, "y": 0.0}
        v_north = {"x": 0.0, "y": -10.0}
        deg_n, card_n = compute_bearing_and_cardinal(u, v_north)
        self.assertAlmostEqual(deg_n, 0.0, delta=1.0)
        self.assertEqual(card_n, "North (N)")

        # East (+X)
        v_east = {"x": 10.0, "y": 0.0}
        deg_e, card_e = compute_bearing_and_cardinal(u, v_east)
        self.assertAlmostEqual(deg_e, 90.0, delta=1.0)
        self.assertEqual(card_e, "East (E)")

        # South (+Z)
        v_south = {"x": 0.0, "y": 10.0}
        deg_s, card_s = compute_bearing_and_cardinal(u, v_south)
        self.assertAlmostEqual(deg_s, 180.0, delta=1.0)
        self.assertEqual(card_s, "South (S)")

        # West (-X)
        v_west = {"x": -10.0, "y": 0.0}
        deg_w, card_w = compute_bearing_and_cardinal(u, v_west)
        self.assertAlmostEqual(deg_w, 270.0, delta=1.0)
        self.assertEqual(card_w, "West (W)")

    def test_instructions_contain_headings_and_disclosures(self) -> None:
        """Verify turn-by-turn instructions include headings, cardinal orientations, and disclosures."""
        route = self.rf.find_route(
            source="FET_G_ENTRANCE_FOYER",
            destination="FET_G_SEMINAR_01",
            algorithm="dijkstra",
            wheelchair_accessible=True,
        )
        self.assertTrue(route.success)

        locs_dict = {loc["id"]: loc for loc in self.cmap.get_all_locations()}
        edges_dict = {(u, v): self.cmap.graph[u][v] for u, v in self.cmap.graph.edges()}

        instructions = generate_turn_by_turn_instructions(route.path, locs_dict, edges_dict)
        self.assertGreater(len(instructions), 0)

        for instr in instructions:
            self.assertIsNotNone(instr.orientation_disclosure)
            self.assertIn("Compass bearings", instr.orientation_disclosure)
            if instr.heading_deg is not None and instr.cardinal_direction != "Arrived":
                self.assertGreaterEqual(instr.heading_deg, 0.0)
                self.assertLessEqual(instr.heading_deg, 360.0)
                self.assertIn(instr.cardinal_direction, CARDINAL_DIRECTIONS)

    # =========================================================================
    # CATEGORY G: NavigationSession Reliability & Edge Cases
    # =========================================================================

    def test_navigation_session_cancel_restart_edge_cases(self) -> None:
        """Verify session cancellation, restart, and state management."""
        session = NavigationSession(user_id="test_user")
        session.start_preview(
            origin_id="FET_G_ENTRANCE_FOYER",
            destination_id="FET_1F_LIBRARY",
            campus_map=self.cmap,
            route_finder=self.rf,
        )
        self.assertEqual(session.state, NavigationState.ROUTE_PREVIEW)

        session.start_navigation(db_manager=self.db_mgr)
        self.assertEqual(session.state, NavigationState.NAVIGATING)

        # Step forward
        session.step_forward(self.cmap, db_manager=self.db_mgr)
        self.assertEqual(session.completed_steps, 1)

        # Cancel mid-navigation
        session.cancel_navigation(db_manager=self.db_mgr)
        self.assertEqual(session.state, NavigationState.IDLE)

        # Restart
        session.start_preview(
            origin_id="FET_G_ENTRANCE_FOYER",
            destination_id="FET_1F_LIBRARY",
            campus_map=self.cmap,
            route_finder=self.rf,
        )
        session.start_navigation(db_manager=self.db_mgr)
        session.restart_navigation()
        self.assertEqual(session.completed_steps, 0)
        self.assertEqual(session.progress_percentage, 0.0)

    # =========================================================================
    # CATEGORY H: Persistent Navigation History in SQLite
    # =========================================================================

    def test_navigation_history_persistence_and_user_isolation(self) -> None:
        """Verify SQLite persistence of navigation history and strict user isolation."""
        # Record session for user_a
        session_data_a = {
            "session_id": "sess_001",
            "user_id": "user_a",
            "origin_id": "OUT_GATE_MAIN",
            "origin_name": "Main Entrance Gate",
            "destination_id": "FET_G_ENTRANCE_FOYER",
            "destination_name": "FET Entrance Foyer",
            "algorithm": "dijkstra",
            "wheelchair_mode": True,
            "total_distance": 120.0,
            "total_time": 90.0,
            "total_steps": 3,
            "status": "ARRIVED",
            "is_rerouted": False,
            "created_at": "2026-11-22 10:00:00",
            "completed_at": "2026-11-22 10:01:30",
        }
        ok_a = self.db_mgr.record_navigation_session(session_data_a)
        self.assertTrue(ok_a)

        # Record session for user_b
        session_data_b = {
            "session_id": "sess_002",
            "user_id": "user_b",
            "origin_id": "FET_G_ENTRANCE_FOYER",
            "origin_name": "FET Entrance Foyer",
            "destination_id": "FET_4F_HPC_CLUSTER",
            "destination_name": "HPC Cluster Lab",
            "algorithm": "dijkstra",
            "wheelchair_mode": True,
            "total_distance": 250.0,
            "total_time": 180.0,
            "total_steps": 6,
            "status": "ARRIVED",
            "is_rerouted": False,
            "created_at": "2026-11-22 10:05:00",
            "completed_at": "2026-11-22 10:08:00",
        }
        ok_b = self.db_mgr.record_navigation_session(session_data_b)
        self.assertTrue(ok_b)

        # Query user_a history: should contain sess_001 and NOT sess_002
        hist_a = self.db_mgr.get_navigation_history(user_id="user_a")
        self.assertEqual(len(hist_a), 1)
        self.assertEqual(hist_a[0]["session_id"], "sess_001")

        # Query user_b history: should contain sess_002 and NOT sess_001
        hist_b = self.db_mgr.get_navigation_history(user_id="user_b")
        self.assertEqual(len(hist_b), 1)
        self.assertEqual(hist_b[0]["session_id"], "sess_002")

        # Verify stats aggregation
        stats_a = self.db_mgr.get_navigation_stats(user_id="user_a")
        self.assertEqual(stats_a["total_sessions"], 1)
        self.assertEqual(stats_a["completed_sessions"], 1)
        self.assertEqual(stats_a["completion_rate"], 100.0)
        self.assertEqual(stats_a["total_distance_navigated"], 120.0)

    # =========================================================================
    # CATEGORY I: Administrative Governance & Audit Trail
    # =========================================================================

    def test_administrative_verification_update_and_audit_logging(self) -> None:
        """Verify Administrator can update verification status and non-admin is blocked."""
        # Non-admin attempt must fail
        ok_nonadmin, msg_nonadmin = self.db_mgr.update_campus_verification(
            entity_type="location",
            entity_id="FET_G_SEMINAR_HALL",
            status="VERIFIED",
            source="Student observation",
            notes="Looked accessible",
            user_role="Student",
            user_id="student_user",
        )
        self.assertFalse(ok_nonadmin)
        self.assertIn("Permission denied", msg_nonadmin)

        # Administrator attempt must succeed
        ok_admin, msg_admin = self.db_mgr.update_campus_verification(
            entity_type="location",
            entity_id="FET_G_SEMINAR_HALL",
            status="VERIFIED",
            source="On-site physical validation audit",
            notes="Measured door widths (>34 in) and confirmed ramp entry.",
            user_role="Administrator",
            user_id="admin_01",
        )
        self.assertTrue(ok_admin)
        self.assertIn("successfully updated", msg_admin)

        # Verify audit trail record was written
        audit_records = self.db_mgr.get_audit_logs(limit=5)
        self.assertGreater(len(audit_records), 0)
        latest_audit = audit_records[0]
        self.assertEqual(latest_audit["action"], "UPDATE_CAMPUS_VERIFICATION")
        self.assertEqual(latest_audit["target_id"], "FET_G_SEMINAR_HALL")
        self.assertEqual(latest_audit["user_id"], "admin_01")


if __name__ == "__main__":
    unittest.main()
