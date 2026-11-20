"""Unit tests for AccessibilityEngine, classification, scoring, and route evaluation."""

from pathlib import Path
import unittest

from modules.accessibility import (
    AccessibilityClassification,
    AccessibilityEngine,
    LocationAccessibilityAssessment,
    PathAccessibilityAssessment,
    RouteAccessibilityAssessment,
)
from modules.campus_map import load_campus_map
from modules.route_finder import RouteFinder


class TestAccessibilityEngine(unittest.TestCase):
    """Test suite covering accessibility intelligence, classifications, and scoring heuristics."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load campus graph and initialize AccessibilityEngine and RouteFinder."""
        cls.data_file = Path(__file__).resolve().parent.parent / "data" / "campus_map.json"
        cls.campus_map = load_campus_map(cls.data_file)
        cls.engine = AccessibilityEngine(cls.campus_map)
        cls.finder = RouteFinder(cls.campus_map)

    def test_fully_accessible_path(self) -> None:
        """Verify evaluation of a clean, step-free corridor."""
        assessment = self.engine.check_path_accessibility("LOC_02", "LOC_03")
        self.assertIsInstance(assessment, PathAccessibilityAssessment)
        self.assertEqual(
            assessment.classification, AccessibilityClassification.FULLY_ACCESSIBLE.value
        )
        self.assertEqual(assessment.score, 100.0)
        self.assertTrue(assessment.wheelchair_accessible)
        self.assertFalse(assessment.has_stairs)
        self.assertEqual(assessment.status, "open")

    def test_staircase_restrictions(self) -> None:
        """Verify detection and classification of staircase barriers."""
        # Connection between Ground Floor stairs (LOC_05) and Floor 1 stairs (LOC_11)
        assessment = self.engine.check_path_accessibility("LOC_05", "LOC_11")
        self.assertEqual(
            assessment.classification, AccessibilityClassification.NOT_WHEELCHAIR_ACCESSIBLE.value
        )
        self.assertEqual(assessment.score, 15.0)
        self.assertFalse(assessment.wheelchair_accessible)
        self.assertTrue(assessment.has_stairs)
        self.assertFalse(assessment.has_elevator)
        self.assertTrue(any("stairs" in w.lower() for w in assessment.warnings))

    def test_ramp_availability(self) -> None:
        """Verify ramp presence identification and assistance classification."""
        # Standard accessible ramp: LOC_01 -> LOC_02
        assessment = self.engine.check_path_accessibility("LOC_01", "LOC_02")
        self.assertTrue(assessment.has_ramp)
        self.assertEqual(
            assessment.classification, AccessibilityClassification.FULLY_ACCESSIBLE.value
        )
        self.assertEqual(assessment.score, 100.0)

        # Ramp with assistance required (e.g. steep incline or manual assistance flag)
        synthetic_ramp_data = {
            "distance": 25.0,
            "has_ramp": True,
            "steep_incline": True,
            "wheelchair_accessible": True,
            "status": "open",
        }
        ramp_assist = self.engine.check_path_accessibility("u", "v", synthetic_ramp_data)
        self.assertEqual(
            ramp_assist.classification,
            AccessibilityClassification.ACCESSIBLE_WITH_ASSISTANCE.value,
        )
        self.assertGreaterEqual(ramp_assist.score, 75.0)

    def test_elevator_availability(self) -> None:
        """Verify elevator vertical connector recognition."""
        # Ground floor elevator (LOC_04) to Floor 1 elevator (LOC_10)
        assessment = self.engine.check_path_accessibility("LOC_04", "LOC_10")
        self.assertTrue(assessment.has_elevator)
        self.assertFalse(assessment.has_stairs)
        self.assertEqual(
            assessment.classification, AccessibilityClassification.FULLY_ACCESSIBLE.value
        )
        self.assertEqual(assessment.score, 100.0)

    def test_blocked_paths(self) -> None:
        """Verify classification and zero score for temporarily blocked connections."""
        synthetic_blocked = {
            "distance": 15.0,
            "status": "blocked",
            "wheelchair_accessible": True,
        }
        assessment = self.engine.check_path_accessibility("u", "v", synthetic_blocked)
        self.assertEqual(
            assessment.classification, AccessibilityClassification.TEMPORARILY_BLOCKED.value
        )
        self.assertEqual(assessment.score, 0.0)
        self.assertTrue(any("closed or blocked" in w.lower() for w in assessment.warnings))

    def test_unknown_accessibility(self) -> None:
        """Verify handling of pathways with missing accessibility attributes."""
        synthetic_unknown = {
            "distance": 12.0,
            "status": "open",
            # wheelchair_accessible and physical flags missing
        }
        assessment = self.engine.check_path_accessibility("u", "v", synthetic_unknown)
        self.assertEqual(
            assessment.classification, AccessibilityClassification.UNKNOWN_ACCESSIBILITY.value
        )
        self.assertEqual(assessment.score, 50.0)
        self.assertIsNone(assessment.wheelchair_accessible)
        self.assertTrue(any("missing or unverified" in w.lower() for w in assessment.warnings))

    def test_score_calculation(self) -> None:
        """Verify 0-100 scoring system and bottleneck caps."""
        # 1. 100% accessible route
        clean_route = ["LOC_01", "LOC_02", "LOC_03"]
        clean_score = self.engine.calculate_accessibility_score(clean_route)
        self.assertEqual(clean_score, 100.0)

        # 2. Route with staircase bottleneck is capped at <= 40
        stair_route = ["LOC_02", "LOC_05", "LOC_11", "LOC_14"]
        stair_score = self.engine.calculate_accessibility_score(stair_route)
        self.assertLessEqual(stair_score, 40.0)
        self.assertGreater(stair_score, 0.0)

        # 3. Single edge dictionary score
        dict_score = self.engine.calculate_accessibility_score(
            {"wheelchair_accessible": True, "status": "open", "has_ramp": True}
        )
        self.assertEqual(dict_score, 100.0)

    def test_complete_route_assessment(self) -> None:
        """Verify full evaluation of calculated routes."""
        # Step-free route via elevator
        accessible_route = self.finder.find_wheelchair_route("LOC_02", "LOC_14")
        assessment = self.engine.evaluate_route_accessibility(accessible_route)

        self.assertIsInstance(assessment, RouteAccessibilityAssessment)
        self.assertTrue(assessment.success)
        self.assertEqual(
            assessment.overall_classification, AccessibilityClassification.FULLY_ACCESSIBLE.value
        )
        self.assertEqual(assessment.accessibility_score, 100.0)
        self.assertTrue(assessment.has_elevator)
        self.assertFalse(assessment.has_ramp)
        self.assertEqual(assessment.num_inaccessible_connections, 0)
        self.assertGreater(assessment.total_distance, 0.0)
        self.assertGreater(assessment.estimated_travel_time, 0.0)

        # Inaccessible route via stairs
        stair_route = self.finder.find_shortest_distance(
            "LOC_02", "LOC_14", wheelchair_accessible=False
        )
        stair_assessment = self.engine.evaluate_route_accessibility(stair_route)
        self.assertEqual(
            stair_assessment.overall_classification,
            AccessibilityClassification.NOT_WHEELCHAIR_ACCESSIBLE.value,
        )
        self.assertLessEqual(stair_assessment.accessibility_score, 40.0)
        self.assertGreater(stair_assessment.num_inaccessible_connections, 0)
        self.assertTrue(any("stairs" in w.lower() for w in stair_assessment.warnings))

    def test_invalid_locations(self) -> None:
        """Verify graceful error reporting when inspecting non-existent locations."""
        assessment = self.engine.check_location_accessibility("NON_EXISTENT_LOCATION")
        self.assertIsInstance(assessment, LocationAccessibilityAssessment)
        self.assertFalse(assessment.success)
        self.assertEqual(
            assessment.classification, AccessibilityClassification.UNKNOWN_ACCESSIBILITY.value
        )
        self.assertEqual(assessment.score, 0.0)
        self.assertIn("not exist", assessment.error_message.lower())

    def test_campus_accessibility_summary(self) -> None:
        """Verify aggregation of network-wide accessibility statistics."""
        summary = self.engine.get_accessibility_summary()
        self.assertEqual(summary["total_locations"], 15)
        self.assertEqual(summary["total_pathways"], 17)
        self.assertIn(
            AccessibilityClassification.FULLY_ACCESSIBLE.value, summary["classification_counts"]
        )
        self.assertEqual(summary["elevator_pathways"], 1)
        self.assertEqual(summary["stairs_pathways"], 1)
        self.assertEqual(summary["ramp_pathways"], 3)
        self.assertGreater(summary["network_accessibility_percentage"], 80.0)
        self.assertIn("heuristic", summary["disclaimer"].lower())


if __name__ == "__main__":
    unittest.main()
