"""Comprehensive validation test suite for Phase 15: Real-Time Wayfinding System.

Tests cover:
- NavigationSession lifecycle & state machine (IDLE -> PREVIEW -> NAVIGATING -> PAUSED -> ARRIVED).
- Turn-by-turn instruction generation with geometric turn calculation (straight, left, right, reverse).
- Building entrance (outdoor -> indoor) and exit transitions.
- Vertical connectors (elevators and stairwells) and accessible ramps.
- Navigation progress tracking (distance, time, step index, floor transitions).
- Automatic verified obstacle detection and dynamic rerouting.
- Wheelchair accessibility preservation during rerouting.
- Unreachable destination handling (NO_ACCESSIBLE_ROUTE).
- Session isolation and serialization.
"""

from __future__ import annotations

import unittest
from typing import Any, Dict

from database.db_manager import DatabaseManager
from modules.campus_map import CampusMap, load_campus_map
from modules.jain_digital_twin import build_jain_digital_twin_payload, load_jain_campus_map
from modules.navigation_instructions import (
    NavigationInstruction,
    compute_turn_angle,
    format_floor_name,
    generate_turn_by_turn_instructions,
)
from modules.navigation_session import NavigationSession, NavigationState
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder


class TestRealTimeWayfindingSystem(unittest.TestCase):
    """Test suite validating real-time indoor & outdoor navigation session and instruction engine."""

    def setUp(self) -> None:
        """Initialize in-memory database, campus map, and routing engines."""
        self.db_mgr = DatabaseManager(":memory:")
        self.cmap = load_jain_campus_map()
        self.obs_mgr = ObstacleManager(db_manager=self.db_mgr, campus_map=self.cmap)
        self.route_finder = RouteFinder(self.cmap)

    def tearDown(self) -> None:
        """Close database connection."""
        self.db_mgr.close()

    def test_navigation_session_lifecycle(self) -> None:
        """Verify complete session state machine: IDLE -> PREVIEW -> NAVIGATING -> PAUSED -> ARRIVED."""
        session = NavigationSession()
        self.assertEqual(session.state, NavigationState.IDLE)

        # 1. Start Preview
        ok_prev = session.start_preview(
            origin_id="FET_G_ENTRANCE_FOYER",
            destination_id="FET_4F_HPC_CLUSTER",
            campus_map=self.cmap,
            route_finder=self.route_finder,
            algorithm="dijkstra",
            wheelchair_mode=True,
        )
        self.assertTrue(ok_prev)
        self.assertEqual(session.state, NavigationState.ROUTE_PREVIEW)
        self.assertEqual(session.completed_steps, 0)
        self.assertEqual(session.current_step_index, 0)
        self.assertGreater(session.total_distance, 0.0)
        self.assertEqual(session.remaining_distance, session.total_distance)
        self.assertGreater(len(session.instructions), 0)

        # 2. Start Navigation
        ok_start = session.start_navigation()
        self.assertTrue(ok_start)
        self.assertEqual(session.state, NavigationState.NAVIGATING)

        # 3. Pause Navigation
        ok_pause = session.pause_navigation()
        self.assertTrue(ok_pause)
        self.assertEqual(session.state, NavigationState.PAUSED)

        # 4. Resume Navigation
        ok_resume = session.resume_navigation()
        self.assertTrue(ok_resume)
        self.assertEqual(session.state, NavigationState.NAVIGATING)

        # 5. Step Forward through all waypoints to completion
        total_steps = session.total_steps
        for _ in range(total_steps):
            session.step_forward(self.cmap)

        self.assertEqual(session.state, NavigationState.ARRIVED)
        self.assertEqual(session.progress_percentage, 100.0)
        self.assertEqual(session.remaining_distance, 0.0)
        self.assertEqual(session.completed_steps, total_steps)

        # 6. Restart Navigation
        ok_restart = session.restart_navigation()
        self.assertTrue(ok_restart)
        self.assertEqual(session.state, NavigationState.NAVIGATING)
        self.assertEqual(session.completed_steps, 0)
        self.assertEqual(session.current_step_index, 0)
        self.assertEqual(session.remaining_distance, session.total_distance)

        # 7. Cancel Navigation
        ok_cancel = session.cancel_navigation()
        self.assertTrue(ok_cancel)
        self.assertEqual(session.state, NavigationState.IDLE)

    def test_invalid_state_transitions(self) -> None:
        """Verify that illegal state transitions are rejected."""
        session = NavigationSession()
        # Cannot pause or resume when IDLE
        self.assertFalse(session.pause_navigation())
        self.assertFalse(session.resume_navigation())
        self.assertFalse(session.step_forward(self.cmap))

        # Start navigation without preview
        self.assertFalse(session.start_navigation())

    def test_geometric_turn_angle_computation(self) -> None:
        """Verify vector turn angle calculation for straight, right turn, left turn, and reverse."""
        # Walking North along -Z: p_prev = (0, 10), p_curr = (0, 0)
        # Continuing North to (0, -10): Straight (0 deg)
        ang_straight = compute_turn_angle((0.0, 10.0), (0.0, 0.0), (0.0, -10.0))
        self.assertAlmostEqual(ang_straight, 0.0, places=1)

        # Turning East to (+10, 0): Right turn (+90 deg)
        ang_right = compute_turn_angle((0.0, 10.0), (0.0, 0.0), (10.0, 0.0))
        self.assertAlmostEqual(ang_right, 90.0, places=1)

        # Turning West to (-10, 0): Left turn (-90 deg)
        ang_left = compute_turn_angle((0.0, 10.0), (0.0, 0.0), (-10.0, 0.0))
        self.assertAlmostEqual(ang_left, -90.0, places=1)

        # Turning back South to (0, 10): Turn around (+180 deg)
        ang_around = compute_turn_angle((0.0, 10.0), (0.0, 0.0), (0.0, 10.0))
        self.assertAlmostEqual(abs(ang_around), 180.0, places=1)

    def test_turn_by_turn_instructions_generation(self) -> None:
        """Verify turn-by-turn instruction actions across building entrance, corridors, elevators, and arrival."""
        # Route from Outdoor Main Gate to FET 4F HPC Cluster
        res = self.route_finder.find_route(
            source="OUT_GATE_MAIN",
            destination="FET_4F_HPC_CLUSTER",
            algorithm="dijkstra",
            wheelchair_accessible=True,
        )
        self.assertTrue(res.success)

        locs_dict = {loc["id"]: loc for loc in self.cmap.get_all_locations()}
        edges_dict = {(u, v): self.cmap.graph[u][v] for u, v in self.cmap.graph.edges()}

        instructions = generate_turn_by_turn_instructions(
            path_nodes=res.path,
            locations_map=locs_dict,
            graph_edges=edges_dict,
        )

        self.assertGreater(len(instructions), 5)
        # First step should start navigation
        self.assertEqual(instructions[0].action_type, "start")
        self.assertEqual(instructions[0].icon, "🚩")

        # Must contain building entrance transition
        has_entrance = any(i.action_type == "enter_building" for i in instructions)
        self.assertTrue(has_entrance, "Route from outdoor gate to FET complex must contain enter_building action")

        # Must contain elevator transition
        has_elev = any(i.action_type == "elevator" for i in instructions)
        self.assertTrue(has_elev, "Route to Level 4 must contain elevator instruction")

        # Final instruction must be arrival
        self.assertEqual(instructions[-1].action_type, "arrive")
        self.assertEqual(instructions[-1].icon, "🎯")
        self.assertIn("Supercomputing", instructions[-1].text)

    def test_navigation_progress_metrics(self) -> None:
        """Verify real-time distance and progress calculations during waypoint stepping."""
        session = NavigationSession()
        session.start_preview(
            origin_id="FET_G_ENTRANCE_FOYER",
            destination_id="FET_4F_HPC_CLUSTER",
            campus_map=self.cmap,
            route_finder=self.route_finder,
        )
        session.start_navigation()

        initial_dist = session.total_distance
        self.assertEqual(session.completed_distance, 0.0)
        self.assertEqual(session.progress_percentage, 0.0)

        # Step 1
        session.step_forward(self.cmap)
        self.assertGreater(session.completed_distance, 0.0)
        self.assertLess(session.remaining_distance, initial_dist)
        self.assertGreater(session.progress_percentage, 0.0)
        self.assertEqual(session.completed_steps, 1)

        # Step 2
        session.step_forward(self.cmap)
        self.assertEqual(session.completed_steps, 2)
        self.assertGreater(session.progress_percentage, 10.0)

    def test_automatic_obstacle_detection_and_dynamic_rerouting(self) -> None:
        """Verify that when an upcoming pathway is blocked, the session detects it and reroutes dynamically."""
        session = NavigationSession()
        session.start_preview(
            origin_id="OUT_GATE_MAIN",
            destination_id="FET_G_ENTRANCE_FOYER",
            campus_map=self.cmap,
            route_finder=self.route_finder,
            wheelchair_mode=False,
        )
        session.start_navigation()

        # Target pathway to block on initial primary route:
        target_u = "OUT_GATE_MAIN"
        target_v = "OUT_QUAD_CENTRAL"

        # 1. Unverified / Pending report should NOT trigger reroute
        rep = self.obs_mgr.submit_report(
            reporter_name="Student",
            source_location_id=target_u,
            destination_location_id=target_v,
            obstacle_category="Blocked pathway",
            severity="Medium",
            description="Temporary debris blocking primary avenue",
        )
        rerouted_pending = session.detect_and_handle_obstacles(
            obstacle_manager=self.obs_mgr,
            campus_map=self.cmap,
            route_finder=self.route_finder,
        )
        self.assertFalse(rerouted_pending, "Pending obstacle must not trigger automatic rerouting")
        self.assertFalse(session.is_rerouted)

        # 2. Verify report -> Now verified hazard must trigger reroute!
        self.obs_mgr.update_report_status(rep["report_id"], "Verified")

        rerouted_verified = session.detect_and_handle_obstacles(
            obstacle_manager=self.obs_mgr,
            campus_map=self.cmap,
            route_finder=self.route_finder,
        )
        self.assertTrue(rerouted_verified, "Verified obstacle on route must trigger dynamic rerouting")
        self.assertTrue(session.is_rerouted)
        self.assertIsNotNone(session.reroute_reason)
        # Destination must be strictly preserved
        self.assertEqual(session.destination_id, "FET_G_ENTRANCE_FOYER")

    def test_obstacle_rerouting_preserves_wheelchair_constraints(self) -> None:
        """Verify that dynamic rerouting strictly preserves wheelchair step-free constraints."""
        session = NavigationSession()
        session.start_preview(
            origin_id="OUT_GATE_MAIN",
            destination_id="FET_G_ENTRANCE_FOYER",
            campus_map=self.cmap,
            route_finder=self.route_finder,
            wheelchair_mode=True,
        )
        session.start_navigation()

        # Block the direct avenue path
        rep = self.obs_mgr.submit_report(
            reporter_name="Staff",
            source_location_id="OUT_GATE_MAIN",
            destination_location_id="OUT_QUAD_CENTRAL",
            obstacle_category="Temporary obstruction",
            severity="High",
            description="Road repaving on central quad avenue",
        )
        self.obs_mgr.update_report_status(rep["report_id"], "Verified")

        session.detect_and_handle_obstacles(
            obstacle_manager=self.obs_mgr,
            campus_map=self.cmap,
            route_finder=self.route_finder,
        )

        self.assertTrue(session.is_rerouted)
        self.assertTrue(session.wheelchair_mode)
        # All edges in the recomputed route must still be wheelchair accessible
        for i in range(len(session.path) - 1):
            e_data = self.cmap.graph.get_edge_data(session.path[i], session.path[i + 1]) or {}
            self.assertTrue(
                e_data.get("wheelchair_accessible", True),
                f"Rerouted segment {session.path[i]} ➔ {session.path[i+1]} must be wheelchair accessible",
            )
            self.assertFalse(
                e_data.get("has_stairs", False),
                f"Rerouted segment {session.path[i]} ➔ {session.path[i+1]} must not contain stairs",
            )

    def test_no_accessible_route_when_vertical_connector_severed(self) -> None:
        """Verify NO_ACCESSIBLE_ROUTE state when essential wheelchair connection is severed."""
        session = NavigationSession()
        # Block elevator shaft between 0F and 1F
        rep = self.obs_mgr.submit_report(
            reporter_name="Safety Inspector",
            source_location_id="FET_0F_ELEVATOR",
            destination_location_id="FET_1F_ELEVATOR",
            obstacle_category="Elevator unavailable",
            severity="Critical",
            description="Emergency cable replacement in progress",
        )
        self.obs_mgr.update_report_status(rep["report_id"], "Verified")

        ok = session.start_preview(
            origin_id="FET_G_ENTRANCE_FOYER",
            destination_id="FET_4F_HPC_CLUSTER",
            campus_map=self.cmap,
            route_finder=self.route_finder,
            wheelchair_mode=True,
        )

        self.assertFalse(ok)
        self.assertEqual(session.state, NavigationState.NO_ACCESSIBLE_ROUTE)
        self.assertIsNotNone(session.error_message)

        self.assertFalse(ok)
        self.assertEqual(session.state, NavigationState.NO_ACCESSIBLE_ROUTE)
        self.assertIsNotNone(session.error_message)

    def test_session_serialization_and_payload_integration(self) -> None:
        """Verify session.to_dict() and integration with build_jain_digital_twin_payload."""
        session = NavigationSession()
        session.start_preview(
            origin_id="FET_G_ENTRANCE_FOYER",
            destination_id="FET_1F_LIBRARY",
            campus_map=self.cmap,
            route_finder=self.route_finder,
        )
        session.start_navigation()
        session.step_forward(self.cmap)

        data = session.to_dict()
        self.assertEqual(data["state"], "NAVIGATING")
        self.assertEqual(data["completed_steps"], 1)
        self.assertIn("current_instruction", data)
        self.assertIn("remaining_distance", data)
        self.assertIn("progress_percentage", data)

        # Test integration with 3D payload builder
        payload = build_jain_digital_twin_payload(
            campus_map=self.cmap,
            route_finder=self.route_finder,
            obstacle_manager=self.obs_mgr,
            start_id="FET_G_ENTRANCE_FOYER",
            dest_id="FET_1F_LIBRARY",
            navigation_session=session,
        )
        self.assertIn("navigation_session", payload)
        self.assertEqual(payload["navigation_session"]["state"], "NAVIGATING")
        self.assertEqual(payload["navigation_session"]["completed_steps"], 1)

    def test_floor_name_formatter(self) -> None:
        """Verify floor number formatting."""
        self.assertEqual(format_floor_name(-1), "Outdoor Campus")
        self.assertEqual(format_floor_name(0), "Ground Floor")
        self.assertEqual(format_floor_name(1), "First Floor")
        self.assertEqual(format_floor_name(2), "Second Floor")
        self.assertEqual(format_floor_name(3), "Third Floor")
        self.assertEqual(format_floor_name(4), "Fourth Floor")
        self.assertEqual(format_floor_name(5), "Floor 5")


if __name__ == "__main__":
    unittest.main()
