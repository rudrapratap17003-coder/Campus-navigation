"""Phase 29 End-to-End User Acceptance Testing (UAT) Test Suite.

Validates complete real-world user journeys:
1. Scenario 1: First-time student navigation (Main Gate to Library).
2. Scenario 2: Student finding specialized labs (Destination search, keyword suggestions, multi-floor guidance).
3. Scenario 3: Wheelchair user navigation (Strict step-free pathfinding, elevator guidance, graceful no-route handling).
4. Scenario 4: Obstacle reporting lifecycle (Submit -> Pending -> Staff Verification -> Route Reroute -> Resolution -> Route Restoration).
5. Scenario 5: Administrator governance, role-based access control (RBAC), and immutable audit trail integrity.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from database.db_manager import DatabaseManager, SecurityLockoutError
from modules.accessibility import AccessibilityEngine
from modules.campus_map import CampusMap, load_campus_map
from modules.destination_search import get_search_suggestions, search_destinations
from modules.jain_digital_twin import load_jain_campus_map
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder


class TestPhase29FinalUAT(unittest.TestCase):
    """Comprehensive End-to-End User Acceptance Test Suite for Phase 29."""

    @classmethod
    def setUpClass(cls) -> None:
        """Initialize in-memory database and campus graph models."""
        cls.db = DatabaseManager(":memory:")
        cls.jain_map = load_jain_campus_map()
        cls.jain_rf = RouteFinder(cls.jain_map)
        cls.jain_acc = AccessibilityEngine(cls.jain_map)

        cls.benchmark_map = load_campus_map()
        cls.benchmark_rf = RouteFinder(cls.benchmark_map)
        cls.benchmark_acc = AccessibilityEngine(cls.benchmark_map)

        cls.obs_mgr = ObstacleManager(db_manager=cls.db, campus_map=cls.benchmark_map)

        # Seed realistic test accounts
        cls.student_user = cls.db.create_user(
            full_name="Alex River (Student)",
            username="alex_student",
            password="StudentPassword2026!",
            role="Student",
            account_status="Active",
        )
        cls.staff_user = cls.db.create_user(
            full_name="Morgan Davis (Field Staff)",
            username="morgan_staff",
            password="StaffPassword2026!",
            role="Field Staff",
            account_status="Active",
        )
        cls.admin_user = cls.db.create_user(
            full_name="Dr. Taylor Reed (Admin)",
            username="taylor_admin",
            password="AdminPassword2026!",
            role="Administrator",
            account_status="Active",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Close database connection cleanly."""
        cls.db.close()

    # =========================================================================
    # SCENARIO 1: FIRST-TIME STUDENT JOURNEY
    # =========================================================================
    def test_scenario_1_first_time_student_journey(self) -> None:
        """Scenario 1: First-time student enters campus and navigates to the Central Library."""
        # 1. Verify destination search can find the Central Library
        matches = search_destinations("Library", self.jain_map)
        self.assertTrue(len(matches) > 0, "Destination search must find campus library.")
        lib_match = matches[0]
        self.assertIn("LIBRARY", lib_match.location_id)
        self.assertEqual(lib_match.floor, 1)

        # 2. Student calculates route from Main Campus Entrance Gate to Library
        route = self.jain_rf.find_route(
            source="OUT_GATE_MAIN",
            destination=lib_match.location_id,
            algorithm="dijkstra",
            optimize_for="distance",
            wheelchair_accessible=True,
        )

        self.assertTrue(route.success, "First-time student route to library must succeed.")
        self.assertGreater(route.total_distance, 0.0)
        self.assertGreater(len(route.path), 1)
        self.assertEqual(route.path[0], "OUT_GATE_MAIN")
        self.assertEqual(route.path[-1], lib_match.location_id)

        # 3. Verify turn-by-turn instruction sequence has readable guidance
        self.assertGreater(len(route.steps), 0)
        for step in route.steps:
            self.assertIsNotNone(step.instruction)
            self.assertGreater(len(step.instruction), 5)
            self.assertGreater(step.distance, 0)
            self.assertGreater(step.estimated_time, 0)

        # 4. Verify step transitions across floors use elevator
        eval_res = self.jain_acc.evaluate_route_accessibility(route)
        self.assertIn(eval_res.overall_classification, ("Fully Accessible", "Accessible with Assistance"))
        self.assertTrue(eval_res.has_elevator, "Route to 1st Floor must use an elevator transition.")

    # =========================================================================
    # SCENARIO 2: STUDENT FINDING SPECIALIZED LABORATORY
    # =========================================================================
    def test_scenario_2_student_finding_laboratory(self) -> None:
        """Scenario 2: Student searching for HPC or Robotics Lab across multiple floors."""
        # 1. Search for 'HPC'
        hpc_matches = search_destinations("HPC", self.jain_map)
        self.assertTrue(len(hpc_matches) > 0, "Search for 'HPC' must return High-Performance Computing Lab.")
        hpc_loc = hpc_matches[0]
        self.assertEqual(hpc_loc.floor, 4, "HPC Cluster is located on Fourth Floor (Level 4).")

        # 2. Search for 'Robotics'
        robotics_matches = search_destinations("Robotics", self.jain_map)
        self.assertTrue(len(robotics_matches) > 0, "Search for 'Robotics' must return Robotics Lab.")
        robotics_loc = robotics_matches[0]
        self.assertEqual(robotics_loc.floor, 3, "Robotics Lab is on Third Floor.")

        # 3. Test suggestions for partial query 'chem'
        suggestions = get_search_suggestions("chem", self.jain_map)
        self.assertTrue(len(suggestions) > 0)

        # 4. Route from Ground Floor Entrance to Fourth Floor HPC Lab
        route_hpc = self.jain_rf.find_route(
            source="FET_G_ENTRANCE_FOYER",
            destination="FET_4F_HPC_CLUSTER",
            algorithm="dijkstra",
            optimize_for="distance",
            wheelchair_accessible=True,
        )
        self.assertTrue(route_hpc.success)
        self.assertEqual(route_hpc.path[0], "FET_G_ENTRANCE_FOYER")
        self.assertEqual(route_hpc.path[-1], "FET_4F_HPC_CLUSTER")

        # Verify vertical transition has elevator instructions
        elevator_steps = [s for s in route_hpc.steps if s.has_elevator]
        self.assertTrue(len(elevator_steps) > 0, "Must include elevator step to 4th floor.")

    # =========================================================================
    # SCENARIO 3: WHEELCHAIR USER ACCESSIBLE ROUTING & NO-ROUTE HANDLING
    # =========================================================================
    def test_scenario_3_wheelchair_user_and_barrier_handling(self) -> None:
        """Scenario 3: Wheelchair user requiring step-free route and graceful no-route handling."""
        # 1. Standard route between floors with wheelchair mode enabled avoids stairs
        wc_route = self.benchmark_rf.find_wheelchair_route("LOC_01", "LOC_12")
        self.assertTrue(wc_route.success)
        self.assertTrue(wc_route.is_accessible)

        # Verify stairs are strictly excluded
        steps = wc_route.steps
        self.assertFalse(any(s.has_stairs for s in steps), "Wheelchair route must NEVER contain stairs.")
        self.assertTrue(any(s.has_elevator for s in steps), "Wheelchair route between floors must use elevator.")

        # 2. Test graceful handling when NO accessible route exists
        # Temporarily disconnect the elevator edge (LOC_04 <-> LOC_10)
        temp_map = load_campus_map()
        temp_rf = RouteFinder(temp_map)
        temp_map.graph.remove_edge("LOC_04", "LOC_10")  # Remove elevator connector

        # Attempt wheelchair routing between Floor 0 and Floor 1
        blocked_route = temp_rf.find_route(
            source="LOC_01",
            destination="LOC_12",
            algorithm="dijkstra",
            wheelchair_accessible=True,
        )

        self.assertFalse(blocked_route.success, "Should fail when no step-free route is physically possible.")
        self.assertIsNotNone(blocked_route.error_message)
        self.assertIn("No accessible route found", blocked_route.error_message)

    # =========================================================================
    # SCENARIO 4: OBSTACLE REPORTING LIFECYCLE
    # =========================================================================
    def test_scenario_4_obstacle_lifecycle_and_rerouting(self) -> None:
        """Scenario 4: Complete obstacle lifecycle: report -> pending -> verify -> reroute -> resolve -> restore."""
        # 1. Calculate baseline unblocked route between LOC_09 and LOC_08
        initial_route = self.benchmark_rf.find_route("LOC_09", "LOC_08")
        self.assertTrue(initial_route.success)
        self.assertEqual(len(initial_route.path), 2)  # Direct link LOC_09 -> LOC_08

        # 2. Student logs an obstacle report
        rep = self.obs_mgr.submit_report(
            obstacle_category="Blocked pathway",
            severity="High",
            description="Wet floor waxing and barrier tape across main corridor.",
            source_location_id="LOC_09",
            destination_location_id="LOC_08",
            reporter_name=self.student_user["full_name"],
        )
        self.assertEqual(rep["status"], "Pending")

        # 3. Confirm pending report does NOT block the graph yet
        pending_route = self.benchmark_rf.find_route("LOC_09", "LOC_08")
        self.assertTrue(pending_route.success)
        self.assertEqual(len(pending_route.path), 2)

        # 4. Field staff verifies the report -> Status becomes Verified, edge blocked in graph
        verified_rep = self.obs_mgr.verify_report(rep["report_id"], actor_user=self.staff_user)
        self.assertEqual(verified_rep["status"], "Verified")

        # 5. Route calculation automatically detours around the blocked pathway
        rerouted = self.benchmark_rf.find_route("LOC_09", "LOC_08")
        self.assertTrue(rerouted.success)
        self.assertGreater(len(rerouted.path), 2, "Route must take a detour around the blocked edge.")
        # Ensure the blocked segment (LOC_09, LOC_08) is not in the path
        for i in range(len(rerouted.path) - 1):
            pair = (rerouted.path[i], rerouted.path[i + 1])
            self.assertNotIn(pair, [("LOC_09", "LOC_08"), ("LOC_08", "LOC_09")])

        # 6. Field staff resolves the obstacle with mandatory resolution notes
        resolved_rep = self.obs_mgr.resolve_report(
            rep["report_id"],
            resolution_notes="Waxing completed and floor dried; barriers removed.",
            actor_user=self.staff_user,
        )
        self.assertEqual(resolved_rep["status"], "Resolved")

        # 7. Pathway is restored and normal direct route is available again
        restored_route = self.benchmark_rf.find_route("LOC_09", "LOC_08")
        self.assertTrue(restored_route.success)
        self.assertEqual(len(restored_route.path), 2)

    # =========================================================================
    # SCENARIO 5: ADMINISTRATOR GOVERNANCE & SECURITY AUDIT
    # =========================================================================
    def test_scenario_5_administrator_governance_and_rbac(self) -> None:
        """Scenario 5: Administrator governance, role modification, and security controls."""
        # 1. Admin checks user directory and obstacle statistics
        user_stats = self.db.get_user_statistics()
        self.assertGreaterEqual(user_stats["total_users"], 3)
        self.assertIn("Student", user_stats["role_counts"])
        self.assertIn("Field Staff", user_stats["role_counts"])
        self.assertIn("Administrator", user_stats["role_counts"])

        # 2. Verify student cannot verify or resolve obstacles (Permission check)
        rep2 = self.obs_mgr.submit_report(
            obstacle_category="Construction work",
            severity="Medium",
            description="Scaffolding installation.",
            source_location_id="LOC_01",
            destination_location_id="LOC_02",
        )
        with self.assertRaises(PermissionError):
            self.obs_mgr.verify_report(rep2["report_id"], actor_user=self.student_user)

        with self.assertRaises(PermissionError):
            self.obs_mgr.resolve_report(rep2["report_id"], resolution_notes="Done", actor_user=self.student_user)

        # 3. Admin successfully updates user role
        update_ok = self.db.update_user_role(
            user_id=self.student_user["user_id"],
            new_role="Field Staff",
            actor_user=self.admin_user,
        )
        self.assertTrue(update_ok)
        updated_user = self.db.get_user_by_id(self.student_user["user_id"])
        self.assertEqual(updated_user["role"], "Field Staff")

        # Reset role back to Student
        reset_ok = self.db.update_user_role(
            user_id=self.student_user["user_id"],
            new_role="Student",
            actor_user=self.admin_user,
        )
        self.assertTrue(reset_ok)

        # 4. Verify immutable audit log records the administrative events
        audit_logs = self.db.get_audit_logs(limit=10)
        self.assertTrue(len(audit_logs) > 0)
        actions = [log["action"] for log in audit_logs]
        self.assertTrue(any("ROLE" in a or "OBSTACLE" in a for a in actions))


if __name__ == "__main__":
    unittest.main()
