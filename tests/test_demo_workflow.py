"""Academic demonstration workflow verification test suite for Accessible Campus Navigator."""

from __future__ import annotations

import unittest

from database.db_manager import DatabaseManager
from modules.accessibility import AccessibilityEngine
from modules.campus_map import CampusMap, load_campus_map
from modules.indoor_map import (
    detect_cross_floor_transitions,
    get_floors_in_campus,
    get_locations_for_floor,
)
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder


class TestDemonstrationWorkflow(unittest.TestCase):
    """Verifies the complete 8-step demonstration sequence required for academic evaluation."""

    def setUp(self) -> None:
        """Create clean test fixtures with in-memory database and campus map."""
        self.db = DatabaseManager(":memory:")
        self.campus_map = load_campus_map()
        self.acc_engine = AccessibilityEngine(self.campus_map)
        self.obs_manager = ObstacleManager(db_manager=self.db, campus_map=self.campus_map)
        self.route_finder = RouteFinder(self.campus_map)

        # Seed demonstration accounts
        self.admin = self.db.create_user(
            full_name="Demonstration Administrator",
            username="demo_admin",
            password="DemoAdmin2026!",
            role="Administrator",
        )
        self.staff = self.db.create_user(
            full_name="Demonstration Field Staff",
            username="demo_staff",
            password="DemoStaff2026!",
            role="Field Staff",
            actor_user=self.admin,
        )
        self.student = self.db.create_user(
            full_name="Demonstration Student",
            username="demo_student",
            password="DemoStudent2026!",
            role="Student",
        )

    def tearDown(self) -> None:
        """Clean up database connection."""
        self.db.close()

    def test_complete_eight_step_demonstration_workflow(self) -> None:
        """Execute and validate all 8 sequential steps of the academic demonstration scenario."""

        # ---------------------------------------------------------------------
        # STEP 1: Student Login & Exploration
        # ---------------------------------------------------------------------
        auth_student = self.db.authenticate_user("demo_student", "DemoStudent2026!")
        self.assertIsNotNone(auth_student)
        assert auth_student is not None
        self.assertEqual(auth_student["role"], "Student")
        self.assertEqual(auth_student["account_status"], "Active")

        # Student inspects baseline accessibility dashboard metrics
        summary = self.acc_engine.get_accessibility_summary()
        self.assertEqual(summary["total_locations"], 15)
        self.assertEqual(summary["total_pathways"], 17)
        self.assertGreater(summary["network_accessibility_percentage"], 90.0)

        # ---------------------------------------------------------------------
        # STEP 2: Accessible Route Planning (Cross-Floor)
        # ---------------------------------------------------------------------
        origin = "LOC_01"       # Ground Floor Main Entrance
        destination = "LOC_14"  # First Floor Computer Science Lab

        # A. BFS Routing (Minimizing edge transitions)
        bfs_route = self.route_finder.find_route(
            origin, destination, algorithm="bfs", wheelchair_accessible=True
        )
        self.assertTrue(bfs_route.success)
        self.assertGreater(len(bfs_route.path), 2)

        # B. Dijkstra Shortest-Distance Routing
        dijkstra_dist = self.route_finder.find_route(
            origin, destination, algorithm="dijkstra", optimize_for="distance", wheelchair_accessible=True
        )
        self.assertTrue(dijkstra_dist.success)
        self.assertGreater(dijkstra_dist.total_distance, 0)
        self.assertGreater(dijkstra_dist.total_time, 0)

        # C. Wheelchair Constraint Enforcement (avoiding vertical stairs edge LOC_05->LOC_11, using elevator LOC_04/LOC_10)
        self.assertIn("LOC_04", dijkstra_dist.path)  # Ground floor elevator
        self.assertIn("LOC_10", dijkstra_dist.path)  # First floor elevator
        self.assertNotIn("LOC_05", dijkstra_dist.path)  # Ground floor stairs avoided
        self.assertFalse(any(step.has_stairs for step in dijkstra_dist.steps))  # No stairs in route
        self.assertTrue(any(step.has_elevator for step in dijkstra_dist.steps))  # Elevator utilized

        # D. Compare with unrestricted routing (which may use stairs)
        unrestricted_route = self.route_finder.find_route(
            origin, destination, algorithm="dijkstra", optimize_for="distance", wheelchair_accessible=False
        )
        self.assertTrue(unrestricted_route.success)
        eval_wheelchair = self.acc_engine.evaluate_route_accessibility(dijkstra_dist)
        self.assertEqual(eval_wheelchair.overall_classification, "Fully Accessible")
        self.assertEqual(eval_wheelchair.num_inaccessible_connections, 0)
        self.assertTrue(dijkstra_dist.is_accessible)

        # ---------------------------------------------------------------------
        # STEP 3: Interactive Indoor Map Spatial Verification
        # ---------------------------------------------------------------------
        floors = get_floors_in_campus(self.campus_map)
        self.assertEqual(floors, [0, 1])

        # Floor separation
        ground_locs = get_locations_for_floor(self.campus_map, 0)
        first_locs = get_locations_for_floor(self.campus_map, 1)
        self.assertEqual(len(ground_locs), 9)
        self.assertEqual(len(first_locs), 6)

        # Elevator cross-floor transition detection
        transitions = detect_cross_floor_transitions(dijkstra_dist.path, self.campus_map)
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0]["connector_type"], "Elevator")
        self.assertEqual(transitions[0]["from_id"], "LOC_04")
        self.assertEqual(transitions[0]["to_id"], "LOC_10")
        self.assertTrue(transitions[0]["wheelchair_accessible"])

        # ---------------------------------------------------------------------
        # STEP 4: Obstacle Reporting as Student
        # ---------------------------------------------------------------------
        rep = self.obs_manager.submit_report(
            obstacle_category="Blocked pathway",
            severity="High",
            description="Flooring maintenance barricade across entrance corridor",
            source_location_id="LOC_01",
            destination_location_id="LOC_02",
            reporter_name=auth_student["full_name"],
        )
        rep_id = rep["report_id"]
        self.assertEqual(rep["status"], "Pending")

        # Verify Pending report does NOT block pathway
        self.assertEqual(self.campus_map.graph["LOC_01"]["LOC_02"]["status"], "open")
        initial_route = self.route_finder.find_route("LOC_01", "LOC_02", algorithm="dijkstra")
        self.assertEqual(initial_route.path, ["LOC_01", "LOC_02"])

        # ---------------------------------------------------------------------
        # STEP 5: Field Staff Verification
        # ---------------------------------------------------------------------
        auth_staff = self.db.authenticate_user("demo_staff", "DemoStaff2026!")
        self.assertIsNotNone(auth_staff)
        assert auth_staff is not None
        self.assertEqual(auth_staff["role"], "Field Staff")

        # Staff verifies obstacle report
        verified_rep = self.obs_manager.verify_report(rep_id, actor_user=auth_staff)
        self.assertEqual(verified_rep["status"], "Verified")
        # Pathway on live graph becomes blocked
        self.assertEqual(self.campus_map.graph["LOC_01"]["LOC_02"]["status"], "blocked")

        # ---------------------------------------------------------------------
        # STEP 6: Dynamic Route Recalculation & Avoidance
        # ---------------------------------------------------------------------
        detour_route = self.route_finder.find_route("LOC_01", "LOC_02", algorithm="dijkstra")
        # If detour is calculated, it must not traverse the blocked segment
        if detour_route.success:
            pairs = list(zip(detour_route.path[:-1], detour_route.path[1:]))
            self.assertNotIn(("LOC_01", "LOC_02"), pairs)
            self.assertNotIn(("LOC_02", "LOC_01"), pairs)

        # ---------------------------------------------------------------------
        # STEP 7: Obstacle Resolution & Restoration
        # ---------------------------------------------------------------------
        # Resolution without notes must fail
        with self.assertRaises(ValueError):
            self.obs_manager.resolve_report(rep_id, resolution_notes="", actor_user=auth_staff)

        # Valid resolution with maintenance notes
        resolved_rep = self.obs_manager.resolve_report(
            rep_id,
            resolution_notes="Barricades removed; flooring inspected and cleared for pedestrian use.",
            actor_user=auth_staff,
        )
        self.assertEqual(resolved_rep["status"], "Resolved")
        # Pathway operational status restored to open
        self.assertEqual(self.campus_map.graph["LOC_01"]["LOC_02"]["status"], "open")

        # Recalculated route returns to direct optimal connection
        restored_route = self.route_finder.find_route("LOC_01", "LOC_02", algorithm="dijkstra")
        self.assertTrue(restored_route.success)
        self.assertEqual(restored_route.path, ["LOC_01", "LOC_02"])

        # ---------------------------------------------------------------------
        # STEP 8: Administrator Governance & RBAC Audit
        # ---------------------------------------------------------------------
        auth_admin = self.db.authenticate_user("demo_admin", "DemoAdmin2026!")
        self.assertIsNotNone(auth_admin)
        assert auth_admin is not None
        self.assertEqual(auth_admin["role"], "Administrator")

        # Verify user governance statistics
        user_stats = self.db.get_user_statistics()
        self.assertEqual(user_stats["total_users"], 3)
        self.assertEqual(user_stats["role_counts"]["Administrator"], 1)
        self.assertEqual(user_stats["role_counts"]["Field Staff"], 1)
        self.assertEqual(user_stats["role_counts"]["Student"], 1)

        # Verify administrative audit trail captured every milestone
        audit_records = self.db.get_audit_logs(limit=50)
        logged_actions = [a["action"] for a in audit_records]
        self.assertIn("CREATE_USER", logged_actions)
        self.assertIn("VERIFY_OBSTACLE", logged_actions)
        self.assertIn("RESOLVE_OBSTACLE", logged_actions)

        # Verify Student cannot perform administrative operations
        with self.assertRaises(PermissionError):
            self.obs_manager.verify_report(rep_id, actor_user=auth_student)
        with self.assertRaises(PermissionError):
            self.db.update_user_role(auth_student["user_id"], "Administrator", actor_user=auth_student)


if __name__ == "__main__":
    unittest.main()
