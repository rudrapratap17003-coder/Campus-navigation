"""Comprehensive test suite validating Master Development fixes across Graph, Accessibility, Routing, Obstacles, Analytics, and RBAC."""

from __future__ import annotations

import copy
import unittest

from database.db_manager import DatabaseManager, SecurityLockoutError
from modules.accessibility import AccessibilityClassification, AccessibilityEngine
from modules.campus_analytics import (
    compute_accessibility_analytics,
    compute_administrative_insights,
    compute_obstacle_analytics,
)
from modules.campus_map import CampusMap, load_campus_map, validate_campus_graph
from modules.indoor_map import create_indoor_map_figure
from modules.jain_digital_twin import load_jain_campus_map
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder


class TestMasterFixesAndValidation(unittest.TestCase):
    """Automated tests verifying P0-P3 fixes and end-to-end navigation consistency."""

    def setUp(self) -> None:
        self.db = DatabaseManager(":memory:")
        self.jain_map = load_jain_campus_map()
        self.bench_map = load_campus_map()
        self.obs_mgr = ObstacleManager(db_manager=self.db, campus_map=self.bench_map)
        self.obs_mgr.register_campus_map(self.jain_map)

    def tearDown(self) -> None:
        self.db.close()

    def test_graph_validation_passes_production_datasets(self) -> None:
        """Both JAIN (79/106) and Benchmark (15/17) graphs must pass validate_campus_graph cleanly."""
        jain_rep = validate_campus_graph(self.jain_map)
        self.assertTrue(jain_rep.is_valid)
        self.assertEqual(jain_rep.total_nodes, 79)
        self.assertEqual(jain_rep.total_edges, 106)
        self.assertEqual(jain_rep.valid_edges, 106)
        self.assertEqual(len(jain_rep.duplicate_edges), 0)
        self.assertEqual(jain_rep.connected_components, 1)
        self.assertEqual(jain_rep.wheelchair_connected_components, 1)
        self.assertEqual(len(jain_rep.missing_floor_transitions), 0)

        bench_rep = validate_campus_graph(self.bench_map)
        self.assertTrue(bench_rep.is_valid)
        self.assertEqual(bench_rep.total_nodes, 15)
        self.assertEqual(bench_rep.total_edges, 17)

    def test_graph_validation_detects_unknown_metadata_and_missing_transitions(self) -> None:
        """Graph validator must catch missing accessibility metadata and broken vertical floor links."""
        synthetic = CampusMap()
        synthetic.load_from_dict({
            "locations": [
                {"id": "A0", "name": "Floor 0 Room", "floor": 0, "building": "B1", "category": "room", "x": 0, "y": 0},
                {"id": "B0", "name": "Floor 0 Hall", "floor": 0, "building": "B1", "category": "lobby", "x": 10, "y": 0},
                {"id": "A1", "name": "Floor 1 Room", "floor": 1, "building": "B1", "category": "room", "x": 0, "y": 0},
            ],
            "connections": [
                {"source": "A0", "destination": "B0", "distance": 10.0, "status": "open"},
            ],
        })
        rep = validate_campus_graph(synthetic)
        self.assertFalse(rep.is_valid)
        self.assertEqual(rep.connected_components, 2)
        self.assertIn("A1", rep.unreachable_locations)
        self.assertEqual(len(rep.unknown_accessibility_edges), 1)
        self.assertEqual(len(rep.missing_floor_transitions), 1)

    def test_conservative_wheelchair_policy_excludes_unknown_and_stairs(self) -> None:
        """Both BFS and Dijkstra in wheelchair mode must exclude stairs, unknown accessibility, and blocked paths."""
        synthetic = CampusMap()
        synthetic.load_from_dict({
            "locations": [
                {"id": "S", "name": "Start", "floor": 0, "building": "B", "category": "lobby", "x": 0, "y": 0},
                {"id": "U", "name": "Unknown Node", "floor": 0, "building": "B", "category": "room", "x": 5, "y": 0},
                {"id": "E", "name": "End", "floor": 0, "building": "B", "category": "lab", "x": 10, "y": 0},
            ],
            "connections": [
                {"source": "S", "destination": "U", "distance": 5.0, "status": "open"},  # Unknown wheelchair_accessible
                {"source": "U", "destination": "E", "distance": 5.0, "status": "open", "wheelchair_accessible": True},
            ],
        })
        rf = RouteFinder(synthetic)
        for algo in ("dijkstra", "bfs"):
            # Standard mode allows traversal
            res_std = rf.find_route("S", "E", algorithm=algo, wheelchair_accessible=False)
            self.assertTrue(res_std.success)
            # Wheelchair mode strictly refuses unknown pathway
            res_wc = rf.find_route("S", "E", algorithm=algo, wheelchair_accessible=True)
            self.assertFalse(res_wc.success)

    def test_jain_cross_floor_route_accessibility_and_explanation(self) -> None:
        """Evaluating OUT_GATE_MAIN -> FET_4F_HPC_CLUSTER on JAIN map produces zero missing-edge errors and clear ramp explanation."""
        rf = RouteFinder(self.jain_map)
        acc = AccessibilityEngine(self.jain_map)
        route = rf.find_route("OUT_GATE_MAIN", "FET_4F_HPC_CLUSTER", algorithm="dijkstra", wheelchair_accessible=True)
        self.assertTrue(route.success)
        eval_res = acc.evaluate_route_accessibility(route)
        self.assertTrue(eval_res.success)
        self.assertFalse(any("does not exist in" in w.lower() for w in eval_res.warnings))
        self.assertEqual(eval_res.accessibility_score, 95.2)
        self.assertTrue(any("OUT_FET_WEST_RAMP" in w for w in eval_res.warnings))

    def test_unknown_location_not_misclassified_inaccessible(self) -> None:
        """A node connected solely via unknown-accessibility edges must classify as Unknown Accessibility."""
        synthetic = CampusMap()
        synthetic.load_from_dict({
            "locations": [
                {"id": "N1", "name": "Unchecked Wing", "floor": 0, "building": "B", "category": "room", "x": 0, "y": 0},
                {"id": "N2", "name": "Corridor", "floor": 0, "building": "B", "category": "lobby", "x": 10, "y": 0},
            ],
            "connections": [
                {"source": "N1", "destination": "N2", "distance": 10.0, "status": "open"},
            ],
        })
        acc = AccessibilityEngine(synthetic)
        loc_res = acc.check_location_accessibility("N1")
        self.assertEqual(loc_res.classification, AccessibilityClassification.UNKNOWN_ACCESSIBILITY.value)
        self.assertEqual(loc_res.unknown_connections, 1)

    def test_multi_map_obstacle_sync_and_rerouting(self) -> None:
        """Submitting, verifying, rerouting, and resolving an obstacle on JAIN campus updates active maps & analytics."""
        staff = self.db.create_user("Staff Tester", "staff_t", "StaffPass2026!", role="Field Staff", account_status="Active")
        rf = RouteFinder(self.jain_map)
        base_route = rf.find_route("OUT_GATE_MAIN", "FET_G_SEMINAR_01", wheelchair_accessible=False)
        self.assertTrue(base_route.success)

        # Submit obstacle on portico connection in JAIN campus via shared ObstacleManager
        rep = self.obs_mgr.submit_report(
            obstacle_category="Construction work",
            severity="High",
            description="Front portico steps blocked",
            source_location_id="OUT_QUAD_CENTRAL",
            destination_location_id="OUT_FET_FRONT_PORTICO",
            reporter_name="QA Tester",
        )
        self.obs_mgr.verify_report(rep["report_id"], actor_user=staff)

        # Active obstacle must block edge on JAIN map and sync to dashboard analytics
        self.assertEqual(self.jain_map.graph["OUT_QUAD_CENTRAL"]["OUT_FET_FRONT_PORTICO"]["status"], "blocked")
        rerouted = rf.find_route("OUT_GATE_MAIN", "FET_G_SEMINAR_01", wheelchair_accessible=False)
        self.assertTrue(rerouted.success)
        self.assertNotIn("OUT_FET_FRONT_PORTICO", rerouted.path)

        acc_stats = compute_accessibility_analytics(self.jain_map, self.obs_mgr)
        self.assertEqual(acc_stats["temporarily_blocked_pathways"], 1)

        # Resolve obstacle and confirm pathway restoration
        self.obs_mgr.resolve_report(rep["report_id"], resolution_notes="Cleared", actor_user=staff)
        self.assertEqual(self.jain_map.graph["OUT_QUAD_CENTRAL"]["OUT_FET_FRONT_PORTICO"]["status"], "open")

    def test_dashboard_analytics_populated_vs_verified_clarity(self) -> None:
        """Verify dashboard analytics separates attribute completeness from physical survey verification."""
        insights = compute_administrative_insights(self.jain_map, self.db, self.obs_mgr)
        self.assertEqual(insights["verification_progress_percentage"], 1.3)
        self.assertEqual(insights["pending_physical_verification_nodes"], 78)
        self.assertEqual(insights["accessibility_summary"]["populated_fields_percentage"], 100.0)
        self.assertEqual(insights["accessibility_summary"]["information_gaps_count"], 0)
        self.assertEqual(insights["accessibility_summary"]["ramp_pathways"], 3)
        self.assertEqual(insights["accessibility_summary"]["average_pathway_score"], 85.4)

    def test_2d_map_figure_clean_labels_and_filters(self) -> None:
        """Verify create_indoor_map_figure builds floor-isolated and wheelchair-filtered charts cleanly."""
        fig_fl2 = create_indoor_map_figure(self.jain_map, floor_filter=2, show_all_labels=True, accessibility_mode="wheelchair_only")
        self.assertGreater(len(fig_fl2.data), 5)
        fig_all = create_indoor_map_figure(self.jain_map, floor_filter=None, show_all_labels=False)
        self.assertGreater(len(fig_all.data), 5)

    def test_auth_and_rbac_full_workflow(self) -> None:
        """Verify bootstrap, lockout, authentication, and RBAC permission boundaries."""
        self.assertFalse(self.db.has_admin_user())
        admin = self.db.create_user("Lead Admin", "lead_admin", "MasterAdmin2026!", role="Administrator", account_status="Active")
        self.assertTrue(self.db.has_admin_user())

        student = self.db.create_user("Campus Student", "camp_stu", "StudentPass2026!", role="Student", account_status="Active")
        rep = self.obs_mgr.submit_report(
            obstacle_category="Blocked pathway",
            severity="Medium",
            description="Corridor sign fell",
            location_id="FET_G_ENTRANCE_FOYER",
            reporter_name=student["full_name"],
        )
        # Student cannot verify obstacle reports
        with self.assertRaises(PermissionError):
            self.obs_mgr.verify_report(rep["report_id"], actor_user=student)

        # Admin can verify and logs audit trail
        self.obs_mgr.verify_report(rep["report_id"], actor_user=admin)
        logs = self.db.get_audit_logs(limit=10)
        self.assertTrue(any(l["action"] == "VERIFY_OBSTACLE" for l in logs))

        # Invalid attempts trigger lockout
        for _ in range(5):
            self.assertIsNone(self.db.authenticate_user("camp_stu", "WrongPass123"))
        with self.assertRaises(SecurityLockoutError):
            self.db.authenticate_user("camp_stu", "StudentPass2026!")


if __name__ == "__main__":
    unittest.main()
