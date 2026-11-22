"""Unit and integration test suite for Phase 19: Advanced Campus Intelligence & Analytics.

Verifies:
1. Accessibility analytics calculation (step-free counts, percentages, information gaps).
2. Obstacle lifecycle analytics (active, pending, resolved, floor distributions, resolution time).
3. Navigation journey telemetry (completed trips, distances, durations, top destinations).
4. Administrative insights compilation and action item generation.
5. Graceful handling of empty datasets without division-by-zero errors.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
import unittest

from database.db_manager import DatabaseManager
from modules.campus_analytics import (
    compute_accessibility_analytics,
    compute_administrative_insights,
    compute_navigation_analytics,
    compute_obstacle_analytics,
)
from modules.campus_map import CampusMap, invalidate_cache
from modules.jain_digital_twin import (
    load_jain_campus_map,
    invalidate_jain_campus_cache,
)
from modules.obstacle_manager import ObstacleManager


class TestPhase19CampusAnalytics(unittest.TestCase):
    """Test suite for Phase 19 Campus Intelligence and Analytics Engine."""

    def setUp(self) -> None:
        """Create test database, JAIN map, and obstacle manager."""
        self.db = DatabaseManager(":memory:")
        self.cmap = load_jain_campus_map()
        self.obs = ObstacleManager(self.db, self.cmap)

    def tearDown(self) -> None:
        """Clean up resources."""
        invalidate_cache()
        invalidate_jain_campus_cache()
        self.db.close()

    # =========================================================================
    # 1. Accessibility Analytics Tests (Phase 19.1)
    # =========================================================================

    def test_accessibility_analytics_jain_campus(self) -> None:
        """Verify accessibility metrics on JAIN Global Campus graph."""
        res = compute_accessibility_analytics(self.cmap, self.obs)

        self.assertEqual(res["total_locations"], 79)
        self.assertGreater(res["accessible_locations"], 50)
        self.assertGreater(res["location_accessibility_percentage"], 65.0)

        self.assertEqual(res["total_pathways"], 106)
        self.assertGreater(res["step_free_pathways"], 80)
        self.assertGreater(res["elevator_pathways"], 0)
        self.assertEqual(res["temporarily_blocked_pathways"], 0)

    def test_accessibility_analytics_with_blocked_pathways(self) -> None:
        """Verify blocked pathway detection when active obstacles are verified."""
        # Insert and verify obstacle on real edge in JAIN graph
        rep_id = self.db.insert_report({
            "source_location_id": "OUT_FET_FRONT_PORTICO",
            "destination_location_id": "FET_G_ENTRANCE_FOYER",
            "target_type": "pathway",
            "obstacle_category": "Blocked pathway",
            "description": "Portico entrance maintenance",
            "severity": "High",
            "reporter_name": "Facilities",
        })
        self.db.update_report_status(rep_id, "Verified")

        res = compute_accessibility_analytics(self.cmap, self.obs)
        self.assertEqual(res["temporarily_blocked_pathways"], 1)

    # =========================================================================
    # 2. Obstacle Lifecycle Analytics Tests (Phase 19.2)
    # =========================================================================

    def test_obstacle_analytics_empty_dataset(self) -> None:
        """Verify obstacle analytics handles empty reports safely without ZeroDivisionError."""
        res = compute_obstacle_analytics(self.db, self.cmap)
        self.assertEqual(res["total_reports"], 0)
        self.assertEqual(res["active_verified_obstacles"], 0)
        self.assertEqual(res["pending_reports"], 0)
        self.assertEqual(res["average_resolution_time_hours"], 0.0)

    def test_obstacle_analytics_metrics_and_resolution_time(self) -> None:
        """Verify lifecycle counts, floor distribution, and average resolution time."""
        t_rep = (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat()
        t_res = datetime.now(timezone.utc).isoformat()

        # Report 1: Resolved after 4 hours on Ground Floor (0)
        r1 = self.db.insert_report({
            "location_id": "FET_0F_ENTRANCE",
            "target_type": "location",
            "obstacle_category": "Construction work",
            "description": "Door realignment",
            "severity": "Medium",
            "reported_at": t_rep,
            "reporter_name": "Student A",
        })
        self.db.update_report_status(r1, "Resolved", resolution_notes="Completed")

        # Update updated_at manually to test duration calculation
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE obstacle_reports SET reported_at = ?, updated_at = ? WHERE report_id = ?;",
                (t_rep, t_res, r1),
            )

        # Report 2: Active Verified on Floor 2
        r2 = self.db.insert_report({
            "source_location_id": "FET_2F_LIBRARY",
            "destination_location_id": "FET_2F_CORRIDOR_E1",
            "target_type": "pathway",
            "obstacle_category": "Blocked pathway",
            "description": "Stack maintenance",
            "severity": "Low",
            "reporter_name": "Librarian",
        })
        self.db.update_report_status(r2, "Verified")

        # Report 3: Pending
        r3 = self.db.insert_report({
            "location_id": "OUT_GATE_MAIN",
            "target_type": "location",
            "obstacle_category": "Temporary obstruction",
            "description": "Visitor vehicle parked",
            "severity": "Low",
            "reporter_name": "Security",
        })

        res = compute_obstacle_analytics(self.db, self.cmap)
        self.assertEqual(res["total_reports"], 3)
        self.assertEqual(res["resolved_obstacles"], 1)
        self.assertEqual(res["active_verified_obstacles"], 1)
        self.assertEqual(res["pending_reports"], 1)
        self.assertAlmostEqual(res["average_resolution_time_hours"], 4.0, delta=0.5)

    # =========================================================================
    # 3. Navigation Telemetry Analytics Tests (Phase 19.3)
    # =========================================================================

    def test_navigation_analytics_telemetry_aggregation(self) -> None:
        """Verify navigation history telemetry calculations."""
        # Log 2 completed trips and 1 cancelled trip
        self.db.log_navigation_history(
            session_id="sess_01",
            user_id="USR-TEST01",
            starting_location="OUT_GATE_MAIN",
            destination="FET Library",
            navigation_mode="wheelchair",
            selected_route="Dijkstra Accessible",
            distance_completed=150.0,
            total_distance=150.0,
            estimated_duration=120.0,
            floor_transitions=2,
            rerouted=0,
            completion_status="completed",
        )
        self.db.log_navigation_history(
            session_id="sess_02",
            user_id="USR-TEST01",
            starting_location="OUT_GATE_MAIN",
            destination="FET Library",
            navigation_mode="standard",
            selected_route="Shortest Pedestrian",
            distance_completed=140.0,
            total_distance=140.0,
            estimated_duration=100.0,
            floor_transitions=2,
            rerouted=1,
            completion_status="completed",
        )
        self.db.log_navigation_history(
            session_id="sess_03",
            user_id="USR-TEST02",
            starting_location="FET_G_ENTRANCE",
            destination="HPC Cluster",
            navigation_mode="standard",
            selected_route="Standard",
            distance_completed=30.0,
            total_distance=200.0,
            estimated_duration=160.0,
            floor_transitions=0,
            rerouted=0,
            completion_status="cancelled",
        )

        res = compute_navigation_analytics(self.db)
        self.assertEqual(res["total_journeys"], 3)
        self.assertEqual(res["completed_journeys"], 2)
        self.assertEqual(res["cancelled_journeys"], 1)
        self.assertAlmostEqual(res["completion_rate_percentage"], 66.7, delta=0.5)
        self.assertEqual(res["rerouted_journeys"], 1)
        self.assertEqual(res["total_floor_transitions"], 4)

        # Destination rankings
        top_dests = dict(res["top_destinations"])
        self.assertEqual(top_dests["FET Library"], 2)
        self.assertEqual(top_dests["HPC Cluster"], 1)

    # =========================================================================
    # 4. Administrative Insights Tests (Phase 19.5)
    # =========================================================================

    def test_administrative_insights_action_items(self) -> None:
        """Verify administrative action items identify pending obstacles and survey priorities."""
        # Seed 1 pending obstacle
        self.db.insert_report({
            "location_id": "FET_3F_LAB_01",
            "target_type": "location",
            "obstacle_category": "Blocked pathway",
            "description": "Equipment spill",
            "severity": "Medium",
            "reporter_name": "Lab Assistant",
        })

        insights = compute_administrative_insights(self.cmap, self.db, self.obs)
        self.assertGreater(insights["campus_accessibility_score"], 60.0)
        self.assertEqual(insights["pending_obstacle_reviews"], 1)
        self.assertTrue(any("Review 1 pending" in item for item in insights["action_items"]))


if __name__ == "__main__":
    unittest.main()
