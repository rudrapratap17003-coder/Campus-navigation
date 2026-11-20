"""Unit tests for SQLite database management, ObstacleManager, and navigation graph synchronization."""

from pathlib import Path
import tempfile
import unittest

from database.db_manager import DatabaseError, DatabaseManager
from modules.accessibility import AccessibilityClassification, AccessibilityEngine
from modules.campus_map import load_campus_map
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder


class TestObstacleManager(unittest.TestCase):
    """Test suite covering obstacle reporting, SQLite persistence, verification, and route avoidance."""

    def setUp(self) -> None:
        """Create an isolated in-memory test database and fresh campus map for each test."""
        self.data_file = Path(__file__).resolve().parent.parent / "data" / "campus_map.json"
        self.campus_map = load_campus_map(self.data_file)
        self.db = DatabaseManager(":memory:")
        self.manager = ObstacleManager(db_manager=self.db, campus_map=self.campus_map)
        self.route_finder = RouteFinder(self.campus_map)
        self.accessibility_engine = AccessibilityEngine(self.campus_map)

    def tearDown(self) -> None:
        """Close test database connection."""
        self.db.close()

    def test_successful_report_submission(self) -> None:
        """Verify successful submission of a valid obstacle report."""
        report = self.manager.submit_report(
            obstacle_category="Elevator unavailable",
            severity="High",
            description="Elevator door sensor failing on ground floor",
            source_location_id="LOC_04",
            destination_location_id="LOC_10",
            reporter_name="Student Council",
        )

        self.assertIsNotNone(report["report_id"])
        self.assertEqual(report["status"], "Pending")
        self.assertEqual(report["severity"], "High")
        self.assertEqual(report["obstacle_category"], "Elevator unavailable")
        self.assertEqual(report["reporter_name"], "Student Council")
        self.assertEqual(report["target_type"], "pathway")

        # Verify saved in SQLite
        saved = self.db.get_report_by_id(report["report_id"])
        self.assertIsNotNone(saved)
        self.assertEqual(saved["report_id"], report["report_id"])
        self.assertEqual(saved["description"], "Elevator door sensor failing on ground floor")

    def test_invalid_report_rejection(self) -> None:
        """Verify validation errors for illegal categories, severities, or empty descriptions."""
        # Invalid category
        with self.assertRaises(ValueError) as ctx:
            self.manager.submit_report(
                obstacle_category="Non-Existent Category",
                severity="Low",
                description="Sample",
                location_id="LOC_01",
            )
        self.assertIn("Invalid obstacle_category", str(ctx.exception))

        # Invalid severity
        with self.assertRaises(ValueError) as ctx:
            self.manager.submit_report(
                obstacle_category="Broken ramp",
                severity="SuperCritical",
                description="Sample",
                location_id="LOC_01",
            )
        self.assertIn("Invalid severity", str(ctx.exception))

        # Empty description
        with self.assertRaises(ValueError) as ctx:
            self.manager.submit_report(
                obstacle_category="Broken ramp",
                severity="Low",
                description="   ",
                location_id="LOC_01",
            )
        self.assertIn("description cannot be empty", str(ctx.exception))

        # Missing target (no location and no pathway)
        with self.assertRaises(ValueError) as ctx:
            self.manager.submit_report(
                obstacle_category="Broken ramp",
                severity="Low",
                description="Sample description",
            )
        self.assertIn("must specify either a location_id or both", str(ctx.exception))

        # Self-loop pathway
        with self.assertRaises(ValueError) as ctx:
            self.manager.submit_report(
                obstacle_category="Broken ramp",
                severity="Low",
                description="Sample description",
                source_location_id="LOC_01",
                destination_location_id="LOC_01",
            )
        self.assertIn("Self-loop", str(ctx.exception))

    def test_invalid_pathway_references(self) -> None:
        """Verify rejection of non-existent locations or non-existent connections."""
        # Non-existent node
        with self.assertRaises(ValueError) as ctx:
            self.manager.submit_report(
                obstacle_category="Blocked pathway",
                severity="Medium",
                description="Debris on walkway",
                source_location_id="LOC_01",
                destination_location_id="LOC_GHOST_999",
            )
        self.assertIn("does not exist in the campus network graph", str(ctx.exception))

        # Non-existent edge between valid nodes (LOC_01 and LOC_15 have no direct edge)
        with self.assertRaises(ValueError) as ctx:
            self.manager.submit_report(
                obstacle_category="Blocked pathway",
                severity="Medium",
                description="Blocked path",
                source_location_id="LOC_01",
                destination_location_id="LOC_15",
            )
        self.assertIn("does not exist in campus map", str(ctx.exception))

    def test_retrieving_and_filtering_reports(self) -> None:
        """Verify retrieval by location, status, and all reports."""
        r1 = self.manager.submit_report(
            obstacle_category="Broken ramp",
            severity="Medium",
            description="Ramp railing loose",
            source_location_id="LOC_01",
            destination_location_id="LOC_02",
        )
        r2 = self.manager.submit_report(
            obstacle_category="Construction work",
            severity="Critical",
            description="Paving work in lobby",
            location_id="LOC_02",
        )

        all_reports = self.manager.get_all_reports()
        self.assertEqual(len(all_reports), 2)

        # Filter by location (LOC_02 appears in both r1 and r2)
        loc2_reports = self.manager.get_reports_by_location("LOC_02")
        self.assertEqual(len(loc2_reports), 2)

        # Filter by status
        pending_reports = self.manager.get_reports_by_status("Pending")
        self.assertEqual(len(pending_reports), 2)

        # Verify r1
        self.manager.verify_report(r1["report_id"])
        verified_reports = self.manager.get_reports_by_status("Verified")
        self.assertEqual(len(verified_reports), 1)
        self.assertEqual(verified_reports[0]["report_id"], r1["report_id"])

    def test_pending_and_rejected_reports_do_not_block_routes(self) -> None:
        """Verify requirement: Pending and Rejected reports must NOT block pathways."""
        # Initially, direct path between LOC_09 and LOC_08 is open
        res_initial = self.route_finder.find_shortest_distance("LOC_09", "LOC_08")
        self.assertEqual(res_initial.path, ["LOC_09", "LOC_08"])

        # 1. Submit pending report
        rep = self.manager.submit_report(
            obstacle_category="Blocked pathway",
            severity="High",
            description="Fallen tree branch across pathway",
            source_location_id="LOC_09",
            destination_location_id="LOC_08",
        )
        self.assertEqual(rep["status"], "Pending")

        # Route must NOT be blocked by pending report
        res_pending = self.route_finder.find_shortest_distance("LOC_09", "LOC_08")
        self.assertEqual(res_pending.path, ["LOC_09", "LOC_08"])

        # 2. Reject the report
        self.manager.reject_report(rep["report_id"], rejection_reason="Branch was cleared by groundskeeper")
        updated_rep = self.manager.get_report(rep["report_id"])
        self.assertEqual(updated_rep["status"], "Rejected")
        self.assertIn("cleared", updated_rep["resolution_notes"])

        # Route must STILL NOT be blocked
        res_rejected = self.route_finder.find_shortest_distance("LOC_09", "LOC_08")
        self.assertEqual(res_rejected.path, ["LOC_09", "LOC_08"])

    def test_verified_blocked_paths_excluded_from_navigation(self) -> None:
        """Verify requirement: Verified blocked pathway is avoided by Dijkstra, BFS, and flagged by AccessibilityEngine."""
        # Route from LOC_09 to LOC_08 (direct: LOC_09 -> LOC_08, 14m)
        rep = self.manager.submit_report(
            obstacle_category="Blocked pathway",
            severity="Critical",
            description="Deep trench dug for cable replacement",
            source_location_id="LOC_09",
            destination_location_id="LOC_08",
        )

        # Verify the report -> marks edge as blocked
        self.manager.verify_report(rep["report_id"])
        active_obs = self.manager.get_active_obstacles()
        self.assertEqual(len(active_obs), 1)

        # Dijkstra must detour: LOC_09 -> LOC_03 -> LOC_08 (33m)
        dijkstra_res = self.route_finder.find_shortest_distance("LOC_09", "LOC_08")
        self.assertTrue(dijkstra_res.success)
        self.assertEqual(dijkstra_res.path, ["LOC_09", "LOC_03", "LOC_08"])
        self.assertNotIn(["LOC_09", "LOC_08"], [dijkstra_res.path[:2]])

        # BFS must detour: LOC_09 -> LOC_03 -> LOC_08 (2 hops instead of direct 1 hop)
        bfs_res = self.route_finder.find_bfs_route("LOC_09", "LOC_08")
        self.assertTrue(bfs_res.success)
        self.assertEqual(bfs_res.path, ["LOC_09", "LOC_03", "LOC_08"])

        # AccessibilityEngine must classify the blocked pathway correctly
        path_eval = self.accessibility_engine.check_path_accessibility("LOC_09", "LOC_08")
        self.assertEqual(
            path_eval.classification, AccessibilityClassification.TEMPORARILY_BLOCKED.value
        )
        self.assertEqual(path_eval.score, 0.0)

    def test_restoring_pathways_after_resolution(self) -> None:
        """Verify requirement: Resolving an obstacle restores original operational status and route access."""
        rep = self.manager.submit_report(
            obstacle_category="Elevator unavailable",
            severity="Critical",
            description="Elevator undergoing routine cable maintenance",
            source_location_id="LOC_04",
            destination_location_id="LOC_10",
        )

        # 1. Verify: elevator blocked
        self.manager.verify_report(rep["report_id"])
        edge_data_blocked = self.campus_map.graph.get_edge_data("LOC_04", "LOC_10")
        self.assertEqual(edge_data_blocked["status"], "blocked")

        # Wheelchair route from Floor 0 to Floor 1 is now unreachable (stairs are inaccessible)
        wheelchair_blocked = self.route_finder.find_wheelchair_route("LOC_02", "LOC_14")
        self.assertFalse(wheelchair_blocked.success)

        # 2. Resolve: elevator restored
        self.manager.resolve_report(
            rep["report_id"],
            resolution_notes="Maintenance completed, safety certificate signed.",
        )
        resolved_rep = self.manager.get_report(rep["report_id"])
        self.assertEqual(resolved_rep["status"], "Resolved")
        self.assertIn("certificate", resolved_rep["resolution_notes"])

        # Check graph edge status restored to 'open'
        edge_data_restored = self.campus_map.graph.get_edge_data("LOC_04", "LOC_10")
        self.assertEqual(edge_data_restored["status"], "open")
        # Check original accessibility attributes preserved
        self.assertTrue(edge_data_restored["wheelchair_accessible"])
        self.assertTrue(edge_data_restored["has_elevator"])
        self.assertEqual(edge_data_restored["distance"], 4.5)

        # Wheelchair navigation works again!
        wheelchair_restored = self.route_finder.find_wheelchair_route("LOC_02", "LOC_14")
        self.assertTrue(wheelchair_restored.success)
        self.assertIn("LOC_04", wheelchair_restored.path)
        self.assertIn("LOC_10", wheelchair_restored.path)

    def test_database_persistence(self) -> None:
        """Verify data persistence across separate DatabaseManager instances on disk."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_db_path = Path(temp_dir) / "persistent_test.db"

            # Instance 1: write report
            db1 = DatabaseManager(temp_db_path)
            mgr1 = ObstacleManager(db_manager=db1, campus_map=self.campus_map)
            r = mgr1.submit_report(
                obstacle_category="Damaged flooring",
                severity="Low",
                description="Loose tile in corridor",
                location_id="LOC_02",
                reporter_name="Inspector Jane",
            )
            rep_id = r["report_id"]
            mgr1.verify_report(rep_id)
            db1.close()

            # Instance 2: reopen same file
            db2 = DatabaseManager(temp_db_path)
            mgr2 = ObstacleManager(db_manager=db2, campus_map=self.campus_map)
            fetched = mgr2.get_report(rep_id)

            self.assertIsNotNone(fetched)
            self.assertEqual(fetched["report_id"], rep_id)
            self.assertEqual(fetched["status"], "Verified")
            self.assertEqual(fetched["reporter_name"], "Inspector Jane")
            self.assertEqual(fetched["description"], "Loose tile in corridor")
            db2.close()

    def test_duplicate_or_invalid_report_updates(self) -> None:
        """Verify handling of invalid updates, non-existent report IDs, and missing resolution notes."""
        # Update non-existent report
        with self.assertRaises(ValueError) as ctx:
            self.manager.update_report_status("NON_EXISTENT_REP_999", "Verified")
        self.assertIn("was not found", str(ctx.exception))

        # Invalid target status
        r = self.manager.submit_report(
            obstacle_category="Temporary obstruction",
            severity="Low",
            description="Trash bin blocking door",
            location_id="LOC_03",
        )
        with self.assertRaises(ValueError) as ctx:
            self.manager.update_report_status(r["report_id"], "INVALID_STATUS_XYZ")
        self.assertIn("Invalid status", str(ctx.exception))

        # Resolving without resolution notes
        with self.assertRaises(ValueError) as ctx:
            self.manager.resolve_report(r["report_id"], resolution_notes="   ")
        self.assertIn("Resolution notes are required", str(ctx.exception))

    def test_obstacle_statistics(self) -> None:
        """Verify aggregated obstacle reporting metrics."""
        self.manager.submit_report(
            obstacle_category="Broken ramp",
            severity="High",
            description="Cracked surface",
            source_location_id="LOC_01",
            destination_location_id="LOC_02",
        )
        r2 = self.manager.submit_report(
            obstacle_category="Elevator unavailable",
            severity="Critical",
            description="Power outage",
            source_location_id="LOC_04",
            destination_location_id="LOC_10",
        )
        self.manager.verify_report(r2["report_id"])

        stats = self.manager.get_obstacle_statistics()
        self.assertEqual(stats["total_reports"], 2)
        self.assertEqual(stats["status_counts"]["Pending"], 1)
        self.assertEqual(stats["status_counts"]["Verified"], 1)
        self.assertEqual(stats["active_obstacles_count"], 1)
        self.assertEqual(stats["severity_counts"]["High"], 1)
        self.assertEqual(stats["severity_counts"]["Critical"], 1)
        self.assertEqual(stats["category_counts"]["Broken ramp"], 1)
        self.assertEqual(stats["category_counts"]["Elevator unavailable"], 1)


if __name__ == "__main__":
    unittest.main()
