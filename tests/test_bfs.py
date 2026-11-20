"""Unit tests for manual Breadth-First Search (BFS) pathfinding."""

from pathlib import Path
import unittest

from algorithms.bfs import BFSResult, bfs_shortest_path
from modules.campus_map import load_campus_map


class TestBFSAlgorithm(unittest.TestCase):
    """Test suite covering BFS routing, edge-count optimality, and accessibility filtering."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load campus graph."""
        cls.data_file = Path(__file__).resolve().parent.parent / "data" / "campus_map.json"
        cls.campus_map = load_campus_map(cls.data_file)
        cls.graph = cls.campus_map.graph

    def test_valid_route(self) -> None:
        """Test 1: Verify a valid standard route between campus locations."""
        result = bfs_shortest_path(self.graph, "LOC_01", "LOC_06")
        self.assertTrue(result.success)
        self.assertIsInstance(result, BFSResult)
        self.assertEqual(result.path[0], "LOC_01")
        self.assertEqual(result.path[-1], "LOC_06")
        # Expected minimum hop path: LOC_01 -> LOC_02 -> LOC_05 -> LOC_06 (3 hops)
        self.assertEqual(result.edge_count, 3)
        self.assertEqual(result.path, ["LOC_01", "LOC_02", "LOC_05", "LOC_06"])
        self.assertGreater(result.total_distance, 0)
        self.assertGreater(result.total_time, 0)

    def test_invalid_starting_location(self) -> None:
        """Test 2: Verify handling of non-existent starting location."""
        # Graceful failure
        res = bfs_shortest_path(self.graph, "NON_EXISTENT_START", "LOC_06")
        self.assertFalse(res.success)
        self.assertIn("not found", res.error_message.lower())

        # Exception mode
        with self.assertRaises(ValueError):
            bfs_shortest_path(self.graph, "NON_EXISTENT_START", "LOC_06", raise_on_error=True)

    def test_invalid_destination(self) -> None:
        """Test 3: Verify handling of non-existent destination location."""
        res = bfs_shortest_path(self.graph, "LOC_01", "NON_EXISTENT_DEST")
        self.assertFalse(res.success)
        self.assertIn("not found", res.error_message.lower())

        with self.assertRaises(ValueError):
            bfs_shortest_path(self.graph, "LOC_01", "NON_EXISTENT_DEST", raise_on_error=True)

    def test_unreachable_destination(self) -> None:
        """Test 4: Verify behavior when destination is completely unreachable."""
        # Block all connections to LOC_06
        blocked = {("LOC_05", "LOC_06")}
        res = bfs_shortest_path(self.graph, "LOC_01", "LOC_06", blocked_edges=blocked)
        self.assertFalse(res.success)
        self.assertEqual(res.path, [])
        self.assertIn("No accessible route found", res.error_message)

    def test_wheelchair_accessibility_restriction(self) -> None:
        """Test 5: Verify wheelchair accessibility enforces step-free routes."""
        # Route from Ground Floor (LOC_02) to Floor 1 (LOC_14)
        # Normal BFS uses stairs: LOC_02 -> LOC_05 -> LOC_11 -> LOC_14 (3 hops)
        res_normal = bfs_shortest_path(self.graph, "LOC_02", "LOC_14", wheelchair_accessible=False)
        self.assertTrue(res_normal.success)
        self.assertIn("LOC_05", res_normal.path)
        self.assertEqual(res_normal.edge_count, 3)

        # Wheelchair BFS MUST avoid stairs LOC_05 <-> LOC_11 and use elevator LOC_04 <-> LOC_10
        res_wheelchair = bfs_shortest_path(
            self.graph, "LOC_02", "LOC_14", wheelchair_accessible=True
        )
        self.assertTrue(res_wheelchair.success)
        self.assertNotIn("LOC_05", res_wheelchair.path)
        self.assertIn("LOC_04", res_wheelchair.path)
        self.assertIn("LOC_10", res_wheelchair.path)

    def test_blocked_pathway(self) -> None:
        """Test 6: Verify route dynamically detours when a pathway is blocked."""
        # Route from LOC_09 (West Ramp) to LOC_08 (Cafeteria)
        # Direct: LOC_09 -> LOC_08 (1 hop)
        res_direct = bfs_shortest_path(self.graph, "LOC_09", "LOC_08")
        self.assertEqual(res_direct.path, ["LOC_09", "LOC_08"])

        # Block direct path (LOC_09, LOC_08), should detour via LOC_03
        detour_blocked = {("LOC_09", "LOC_08")}
        res_detour = bfs_shortest_path(
            self.graph, "LOC_09", "LOC_08", blocked_edges=detour_blocked
        )
        self.assertTrue(res_detour.success)
        self.assertEqual(res_detour.path, ["LOC_09", "LOC_03", "LOC_08"])


if __name__ == "__main__":
    unittest.main()
