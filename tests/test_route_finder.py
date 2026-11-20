"""Unit tests for RouteFinder class, multi-modal routing, and alternative routes."""

from pathlib import Path
import unittest

from modules.campus_map import load_campus_map
from modules.route_finder import RouteFinder, RouteResult


class TestRouteFinder(unittest.TestCase):
    """Test suite covering the integrated RouteFinder engine."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load campus graph and initialize RouteFinder."""
        cls.data_file = Path(__file__).resolve().parent.parent / "data" / "campus_map.json"
        cls.campus_map = load_campus_map(cls.data_file)
        cls.finder = RouteFinder(cls.campus_map)

    def test_case_1_valid_route(self) -> None:
        """Requirement 1: Valid route generation with turn-by-turn steps."""
        res = self.finder.find_route("LOC_01", "LOC_03")
        self.assertTrue(res.success)
        self.assertIsInstance(res, RouteResult)
        self.assertEqual(res.path, ["LOC_01", "LOC_02", "LOC_03"])
        self.assertEqual(res.total_distance, 38.0)
        self.assertEqual(res.total_time, 29.0)
        self.assertEqual(res.edge_count, 2)
        self.assertEqual(len(res.steps), 2)

        # Check step details
        step1 = res.steps[0]
        self.assertEqual(step1.from_name, "Main Campus Entrance")
        self.assertEqual(step1.to_name, "Central Reception & Info Desk")
        self.assertTrue(step1.has_ramp)
        self.assertIn("ramp", step1.instruction.lower())

    def test_case_2_invalid_starting_location(self) -> None:
        """Requirement 2: Handle invalid starting location."""
        res = self.finder.find_route("UNKNOWN_LOC_XYZ", "LOC_03")
        self.assertFalse(res.success)
        self.assertEqual(res.path, [])
        self.assertIn("not found", res.error_message.lower())

    def test_case_3_invalid_destination(self) -> None:
        """Requirement 3: Handle invalid destination location."""
        res = self.finder.find_route("LOC_01", "UNKNOWN_DEST_ABC")
        self.assertFalse(res.success)
        self.assertEqual(res.path, [])
        self.assertIn("not found", res.error_message.lower())

    def test_case_4_unreachable_destination(self) -> None:
        """Requirement 4: Handle unreachable destination when paths are severed."""
        blocked = {("LOC_05", "LOC_06")}
        res = self.finder.find_route("LOC_01", "LOC_06", blocked_edges=blocked)
        self.assertFalse(res.success)
        self.assertEqual(res.path, [])
        self.assertIn("No accessible route found", res.error_message)

    def test_case_5_wheelchair_accessibility_restriction(self) -> None:
        """Requirement 5: Enforce wheelchair accessibility constraints (avoid stairs, use elevator)."""
        # Normal route uses stairs (LOC_05 -> LOC_11)
        res_normal = self.finder.find_route(
            "LOC_02", "LOC_14", wheelchair_accessible=False
        )
        self.assertTrue(res_normal.success)
        self.assertEqual(res_normal.path, ["LOC_02", "LOC_05", "LOC_11", "LOC_14"])
        self.assertFalse(res_normal.is_accessible)

        # Wheelchair route uses elevator (LOC_04 -> LOC_10)
        res_wheelchair = self.finder.find_wheelchair_route("LOC_02", "LOC_14")
        self.assertTrue(res_wheelchair.success)
        self.assertEqual(
            res_wheelchair.path, ["LOC_02", "LOC_04", "LOC_10", "LOC_11", "LOC_14"]
        )
        self.assertTrue(res_wheelchair.is_accessible)
        self.assertTrue(any(step.has_elevator for step in res_wheelchair.steps))
        self.assertFalse(any(step.has_stairs for step in res_wheelchair.steps))

    def test_case_6_blocked_pathway(self) -> None:
        """Requirement 6: Detour around actively blocked pathway."""
        # Direct path from LOC_09 to LOC_08
        res_direct = self.finder.find_route("LOC_09", "LOC_08")
        self.assertEqual(res_direct.path, ["LOC_09", "LOC_08"])

        # Block the direct edge
        res_detour = self.finder.find_route(
            "LOC_09", "LOC_08", blocked_edges={("LOC_09", "LOC_08")}
        )
        self.assertTrue(res_detour.success)
        self.assertEqual(res_detour.path, ["LOC_09", "LOC_03", "LOC_08"])
        self.assertEqual(res_detour.total_distance, 33.0)

    def test_case_7_shortest_distance_route(self) -> None:
        """Requirement 7: Verify shortest distance routing."""
        res = self.finder.find_shortest_distance("LOC_04", "LOC_11")
        self.assertTrue(res.success)
        self.assertEqual(res.path, ["LOC_04", "LOC_10", "LOC_11"])
        self.assertEqual(res.total_distance, 16.5)

    def test_case_8_fastest_time_route(self) -> None:
        """Requirement 8: Verify fastest time routing."""
        res = self.finder.find_fastest_time("LOC_04", "LOC_11")
        self.assertTrue(res.success)
        self.assertEqual(res.path, ["LOC_04", "LOC_10", "LOC_11"])
        self.assertEqual(res.total_time, 40.0)

    def test_case_9_alternative_route(self) -> None:
        """Requirement 9: Compute distinct alternative routes."""
        # Route between LOC_10 and LOC_12
        # Primary: LOC_10 -> LOC_12 (15.0m)
        # Alternative: LOC_10 -> LOC_13 -> LOC_12 (42.0m)
        alternatives = self.finder.find_alternative_routes("LOC_10", "LOC_12", max_alternatives=2)
        self.assertGreaterEqual(len(alternatives), 1)

        alt1 = alternatives[0]
        self.assertTrue(alt1.success)
        self.assertEqual(alt1.path, ["LOC_10", "LOC_13", "LOC_12"])
        self.assertEqual(alt1.total_distance, 42.0)
        self.assertNotEqual(alt1.path, ["LOC_10", "LOC_12"])

    def test_bfs_integration(self) -> None:
        """Verify BFS routing through RouteFinder."""
        res = self.finder.find_bfs_route("LOC_01", "LOC_06")
        self.assertTrue(res.success)
        self.assertEqual(res.algorithm_used, "bfs")
        self.assertEqual(res.edge_count, 3)
        self.assertEqual(res.path, ["LOC_01", "LOC_02", "LOC_05", "LOC_06"])


if __name__ == "__main__":
    unittest.main()
