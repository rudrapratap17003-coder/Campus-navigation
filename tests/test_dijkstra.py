"""Unit tests for manual Dijkstra shortest-path algorithm."""

from pathlib import Path
import unittest

from algorithms.dijkstra import DijkstraResult, dijkstra_shortest_path
from modules.campus_map import load_campus_map


class TestDijkstraAlgorithm(unittest.TestCase):
    """Test suite covering Dijkstra routing, distance/time optimization, and accessibility."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load campus graph."""
        cls.data_file = Path(__file__).resolve().parent.parent / "data" / "campus_map.json"
        cls.campus_map = load_campus_map(cls.data_file)
        cls.graph = cls.campus_map.graph

    def test_valid_route(self) -> None:
        """Test 1: Verify a valid Dijkstra route with exact metrics."""
        result = dijkstra_shortest_path(self.graph, "LOC_01", "LOC_03")
        self.assertTrue(result.success)
        self.assertIsInstance(result, DijkstraResult)
        # Expected path: LOC_01 -> LOC_02 (20m, 15s) -> LOC_03 (18m, 14s)
        self.assertEqual(result.path, ["LOC_01", "LOC_02", "LOC_03"])
        self.assertEqual(result.total_distance, 38.0)
        self.assertEqual(result.total_time, 29.0)
        self.assertEqual(result.cost, 38.0)

    def test_invalid_starting_location(self) -> None:
        """Test 2: Verify handling of invalid starting location."""
        res = dijkstra_shortest_path(self.graph, "MISSING_SOURCE", "LOC_03")
        self.assertFalse(res.success)
        self.assertIn("not found", res.error_message.lower())

        with self.assertRaises(ValueError):
            dijkstra_shortest_path(
                self.graph, "MISSING_SOURCE", "LOC_03", raise_on_error=True
            )

    def test_invalid_destination(self) -> None:
        """Test 3: Verify handling of invalid destination location."""
        res = dijkstra_shortest_path(self.graph, "LOC_01", "MISSING_DEST")
        self.assertFalse(res.success)
        self.assertIn("not found", res.error_message.lower())

        with self.assertRaises(ValueError):
            dijkstra_shortest_path(
                self.graph, "LOC_01", "MISSING_DEST", raise_on_error=True
            )

    def test_unreachable_destination(self) -> None:
        """Test 4: Verify behavior when destination cannot be reached."""
        blocked = {("LOC_02", "LOC_03"), ("LOC_09", "LOC_03"), ("LOC_08", "LOC_03")}
        res = dijkstra_shortest_path(self.graph, "LOC_01", "LOC_03", blocked_edges=blocked)
        self.assertFalse(res.success)
        self.assertEqual(res.path, [])
        self.assertIn("No accessible route found", res.error_message)

    def test_wheelchair_accessibility_restriction(self) -> None:
        """Test 5: Verify wheelchair route avoids stairs and uses elevator."""
        # Route from LOC_02 (Ground Floor) to LOC_14 (First Floor)
        # Standard Dijkstra: LOC_02 -> LOC_05 -> LOC_11 (stairs) -> LOC_14
        # Distance: 16 + 7 + 14 = 37.0 m
        res_standard = dijkstra_shortest_path(
            self.graph, "LOC_02", "LOC_14", wheelchair_accessible=False
        )
        self.assertTrue(res_standard.success)
        self.assertEqual(res_standard.path, ["LOC_02", "LOC_05", "LOC_11", "LOC_14"])
        self.assertEqual(res_standard.total_distance, 37.0)

        # Wheelchair Dijkstra: stairs disallowed. Must use elevator LOC_04 <-> LOC_10
        # LOC_02 -> LOC_04 -> LOC_10 -> LOC_11 -> LOC_14
        # Distance: 15 + 4.5 + 12 + 14 = 45.5 m
        res_wheelchair = dijkstra_shortest_path(
            self.graph, "LOC_02", "LOC_14", wheelchair_accessible=True
        )
        self.assertTrue(res_wheelchair.success)
        self.assertEqual(res_wheelchair.path, ["LOC_02", "LOC_04", "LOC_10", "LOC_11", "LOC_14"])
        self.assertEqual(res_wheelchair.total_distance, 45.5)
        self.assertNotIn("LOC_05", res_wheelchair.path)

    def test_blocked_pathway(self) -> None:
        """Test 6: Verify detours around blocked pathways."""
        # Route between LOC_09 and LOC_08
        res_open = dijkstra_shortest_path(self.graph, "LOC_09", "LOC_08")
        self.assertEqual(res_open.path, ["LOC_09", "LOC_08"])
        self.assertEqual(res_open.total_distance, 14.0)

        # Block direct path LOC_09 <-> LOC_08
        res_detour = dijkstra_shortest_path(
            self.graph, "LOC_09", "LOC_08", blocked_edges={("LOC_09", "LOC_08")}
        )
        self.assertTrue(res_detour.success)
        self.assertEqual(res_detour.path, ["LOC_09", "LOC_03", "LOC_08"])
        # Detour distance: 16 (LOC_09->LOC_03) + 17 (LOC_03->LOC_08) = 33.0 m
        self.assertEqual(res_detour.total_distance, 33.0)

    def test_shortest_distance_optimization(self) -> None:
        """Test 7: Verify shortest distance optimization."""
        res = dijkstra_shortest_path(self.graph, "LOC_04", "LOC_11", weight="distance")
        self.assertTrue(res.success)
        # Optimal distance is via elevator: LOC_04 -> LOC_10 (4.5m) -> LOC_11 (12.0m) = 16.5m
        self.assertEqual(res.path, ["LOC_04", "LOC_10", "LOC_11"])
        self.assertEqual(res.total_distance, 16.5)
        self.assertEqual(res.cost, 16.5)

    def test_fastest_time_optimization(self) -> None:
        """Test 8: Verify fastest time optimization."""
        res = dijkstra_shortest_path(self.graph, "LOC_04", "LOC_11", weight="estimated_time")
        self.assertTrue(res.success)
        # Time via elevator: 30s + 10s = 40.0s (vs via stairs 12s + 13s + 25s = 50s)
        self.assertEqual(res.path, ["LOC_04", "LOC_10", "LOC_11"])
        self.assertEqual(res.total_time, 40.0)
        self.assertEqual(res.cost, 40.0)


if __name__ == "__main__":
    unittest.main()
