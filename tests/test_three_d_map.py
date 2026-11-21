"""Unit and integration tests for Three.js 3D Campus Navigation Engine."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from database.db_manager import DatabaseManager
from modules.campus_map import CampusMap, load_campus_map
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder
from modules.three_d_map import (
    EXPLODED_FLOOR_Y,
    FIRST_FLOOR_Y,
    GROUND_FLOOR_Y,
    PALETTE,
    build_3d_scene_payload,
    get_3d_locations_data,
    get_3d_pathways_data,
    get_3d_route_data,
    normalize_3d_coordinates,
    render_three_d_scene_html,
)


class TestThreeDMapEngine(unittest.TestCase):
    """Test suite covering 3D spatial mapping, route serialization, obstacle sync, and HTML generation."""

    @classmethod
    def setUpClass(cls) -> None:
        """Initialize campus map and route finder from canonical dataset."""
        cls.data_file = Path(__file__).resolve().parent.parent / "data" / "campus_map.json"
        cls.campus_map = load_campus_map(cls.data_file)
        cls.route_finder = RouteFinder(cls.campus_map)

    def setUp(self) -> None:
        """Create isolated temporary database for obstacle testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_3d_obstacles.db"
        self.db_manager = DatabaseManager(self.db_path)
        # Deepcopy campus map so graph mutations do not leak between tests
        self.test_campus_map = copy.deepcopy(self.campus_map)
        self.obstacle_manager = ObstacleManager(
            db_manager=self.db_manager,
            campus_map=self.test_campus_map,
        )
        self.test_route_finder = RouteFinder(self.test_campus_map)

    def tearDown(self) -> None:
        """Cleanup temporary database."""
        self.temp_dir.cleanup()

    def test_3d_coordinates_normalization_and_floors(self) -> None:
        """Verify 3D coordinate normalization and floor vertical separation."""
        coords = normalize_3d_coordinates(self.campus_map)
        self.assertEqual(len(coords), 15)

        # Ground floor locations (LOC_01 - LOC_09)
        for i in range(1, 10):
            loc_id = f"LOC_0{i}"
            self.assertIn(loc_id, coords)
            self.assertEqual(coords[loc_id]["floor"], 0)
            self.assertEqual(coords[loc_id]["y"], GROUND_FLOOR_Y)
            self.assertIsInstance(coords[loc_id]["x"], float)
            self.assertIsInstance(coords[loc_id]["z"], float)

        # First floor locations (LOC_10 - LOC_15)
        for i in range(10, 16):
            loc_id = f"LOC_{i}"
            self.assertIn(loc_id, coords)
            self.assertEqual(coords[loc_id]["floor"], 1)
            self.assertEqual(coords[loc_id]["y"], FIRST_FLOOR_Y)
            self.assertIsInstance(coords[loc_id]["x"], float)
            self.assertIsInstance(coords[loc_id]["z"], float)

    def test_missing_and_invalid_coordinates_handling(self) -> None:
        """Verify robust fallback coordinates when nodes lack valid X or Y values."""
        # Create a mock map copy with missing coordinates
        mock_map = copy.deepcopy(self.campus_map)
        mock_map.locations["LOC_01"]["x"] = None
        mock_map.locations["LOC_01"]["y"] = None
        mock_map.locations["LOC_02"]["x"] = "invalid_string"

        coords = normalize_3d_coordinates(mock_map)
        self.assertIn("LOC_01", coords)
        self.assertIsInstance(coords["LOC_01"]["x"], float)
        self.assertIsInstance(coords["LOC_01"]["z"], float)
        self.assertEqual(coords["LOC_01"]["y"], GROUND_FLOOR_Y)

        self.assertIn("LOC_02", coords)
        self.assertIsInstance(coords["LOC_02"]["x"], float)
        self.assertIsInstance(coords["LOC_02"]["z"], float)

    def test_all_15_locations_metadata_mapping(self) -> None:
        """Verify structured 3D spatial metadata for all 15 campus locations."""
        locations = get_3d_locations_data(self.campus_map)
        self.assertEqual(len(locations), 15)

        loc_ids = {loc["id"] for loc in locations}
        expected_ids = {f"LOC_{i:02d}" for i in range(1, 16)}
        self.assertEqual(loc_ids, expected_ids)

        for loc in locations:
            self.assertIn("name", loc)
            self.assertIn("floor", loc)
            self.assertIn("category", loc)
            self.assertIn("pos", loc)
            self.assertIn("dimensions", loc)
            self.assertIn("amenities", loc)
            self.assertIn("connected_locations", loc)
            self.assertIsInstance(loc["amenities"], list)
            self.assertGreater(len(loc["amenities"]), 0)

            # Dimensions should be positive
            dim = loc["dimensions"]
            self.assertGreater(dim["width"], 0)
            self.assertGreater(dim["height"], 0)
            self.assertGreater(dim["depth"], 0)

    def test_all_17_pathways_mapping(self) -> None:
        """Verify structured 3D geometry and metadata for all 17 campus pathways."""
        pathways = get_3d_pathways_data(self.campus_map)
        self.assertEqual(len(pathways), 17)

        # Inter-floor vertical connectors
        cross_edges = [p for p in pathways if p["is_cross_floor"]]
        self.assertEqual(len(cross_edges), 2)

        # Elevator connection (LOC_04 <-> LOC_10)
        elevator = next((p for p in cross_edges if p["has_elevator"]), None)
        self.assertIsNotNone(elevator)
        self.assertEqual(elevator["pathway_type"], "elevator")
        self.assertEqual(set([elevator["source"], elevator["destination"]]), {"LOC_04", "LOC_10"})
        self.assertTrue(elevator["wheelchair_accessible"])
        self.assertEqual(elevator["color"], PALETTE["elevator_blue"])

        # Staircase connection (LOC_05 <-> LOC_11)
        stairs = next((p for p in cross_edges if p["has_stairs"]), None)
        self.assertIsNotNone(stairs)
        self.assertEqual(stairs["pathway_type"], "stairs")
        self.assertEqual(set([stairs["source"], stairs["destination"]]), {"LOC_05", "LOC_11"})
        self.assertFalse(stairs["wheelchair_accessible"])
        self.assertEqual(stairs["color"], PALETTE["stairs_amber"])

        # Ramp connections
        ramp_edges = [p for p in pathways if p["has_ramp"]]
        self.assertGreaterEqual(len(ramp_edges), 3)  # LOC_01-LOC_02, LOC_08-LOC_09, LOC_03-LOC_09

    def test_route_data_serialization_dijkstra_and_bfs(self) -> None:
        """Verify 3D route spline waypoint generation for Dijkstra and BFS algorithms."""
        # 1. Dijkstra Route
        dijkstra_route = get_3d_route_data(
            campus_map=self.campus_map,
            route_finder=self.route_finder,
            start_id="LOC_01",
            dest_id="LOC_12",
            algorithm="dijkstra",
            wheelchair_accessible=False,
        )
        self.assertTrue(dijkstra_route["success"])
        self.assertIn("LOC_01", dijkstra_route["path"])
        self.assertIn("LOC_12", dijkstra_route["path"])
        self.assertGreater(len(dijkstra_route["waypoints"]), len(dijkstra_route["path"]))
        self.assertGreater(dijkstra_route["total_distance"], 0.0)
        self.assertGreater(len(dijkstra_route["steps"]), 0)

        # 2. BFS Route
        bfs_route = get_3d_route_data(
            campus_map=self.campus_map,
            route_finder=self.route_finder,
            start_id="LOC_01",
            dest_id="LOC_06",
            algorithm="bfs",
            wheelchair_accessible=False,
        )
        self.assertTrue(bfs_route["success"])
        self.assertEqual(bfs_route["path"][0], "LOC_01")
        self.assertEqual(bfs_route["path"][-1], "LOC_06")
        self.assertEqual(bfs_route["algorithm_used"], "BFS")

    def test_wheelchair_route_visualization_data(self) -> None:
        """Verify that wheelchair-constrained 3D route avoids staircase and uses elevator."""
        wc_route = get_3d_route_data(
            campus_map=self.campus_map,
            route_finder=self.route_finder,
            start_id="LOC_02",
            dest_id="LOC_14",
            algorithm="dijkstra",
            wheelchair_accessible=True,
        )
        self.assertTrue(wc_route["success"])
        self.assertTrue(wc_route["is_accessible"])

        # Must traverse Elevator (LOC_04 -> LOC_10) and avoid staircase edge (LOC_05 -> LOC_11)
        path = wc_route["path"]
        self.assertIn("LOC_04", path)
        self.assertIn("LOC_10", path)
        self.assertNotIn("LOC_05", path)  # Avoid ground staircase entry

        # Verify no segment uses the stairs connection
        for i in range(len(path) - 1):
            segment = {path[i], path[i + 1]}
            self.assertNotEqual(segment, {"LOC_05", "LOC_11"}, "Wheelchair route must not traverse stairs")

        # Verify vertical transition metadata
        transitions = wc_route["cross_floor_transitions"]
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0]["connector_type"], "Elevator")
        self.assertTrue(transitions[0]["wheelchair_accessible"])

    def test_verified_obstacle_synchronization(self) -> None:
        """Verify that verified obstacle blocks pathway in 3D data and forces rerouting."""
        # Report obstacle on LOC_02 - LOC_04 (Elevator access from reception)
        report = self.obstacle_manager.submit_report(
            source_location_id="LOC_02",
            destination_location_id="LOC_04",
            obstacle_category="Blocked pathway",
            severity="High",
            description="Corridor undergoing ceiling maintenance",
            reporter_name="Student User",
        )
        # Verify the report to activate blocked state
        self.obstacle_manager.verify_report(report["report_id"])

        # Check 3D pathways data
        pathways = get_3d_pathways_data(self.test_campus_map, obstacle_manager=self.obstacle_manager)
        blocked_edge = next((p for p in pathways if set([p["source"], p["destination"]]) == {"LOC_02", "LOC_04"}), None)
        self.assertIsNotNone(blocked_edge)
        self.assertTrue(blocked_edge["is_blocked"])
        self.assertEqual(blocked_edge["color"], PALETTE["blocked_red"])

        # Check that RouteFinder now avoids LOC_02 - LOC_04
        route = get_3d_route_data(
            campus_map=self.test_campus_map,
            route_finder=self.test_route_finder,
            start_id="LOC_01",
            dest_id="LOC_07",
            algorithm="dijkstra",
            wheelchair_accessible=False,
        )
        self.assertTrue(route["success"])
        # Should NOT contain direct transition LOC_02 -> LOC_04
        for i in range(len(route["path"]) - 1):
            pair = {route["path"][i], route["path"][i + 1]}
            self.assertNotEqual(pair, {"LOC_02", "LOC_04"})

    def test_pending_obstacle_behavior(self) -> None:
        """Verify that pending obstacle does NOT block pathways in 3D scene."""
        # Submit a pending report without verifying it
        self.obstacle_manager.submit_report(
            source_location_id="LOC_02",
            destination_location_id="LOC_04",
            obstacle_category="Temporary obstruction",
            severity="Low",
            description="Cleaning equipment left in hallway",
            reporter_name="Student User",
        )

        pathways = get_3d_pathways_data(self.test_campus_map, obstacle_manager=self.obstacle_manager)
        edge = next((p for p in pathways if set([p["source"], p["destination"]]) == {"LOC_02", "LOC_04"}), None)
        self.assertIsNotNone(edge)
        self.assertFalse(edge["is_blocked"])
        self.assertTrue(edge["is_pending"])

        # Pathway remains usable in route calculation
        route = get_3d_route_data(
            campus_map=self.test_campus_map,
            route_finder=self.test_route_finder,
            start_id="LOC_02",
            dest_id="LOC_04",
            algorithm="dijkstra",
        )
        self.assertTrue(route["success"])
        self.assertEqual(route["path"], ["LOC_02", "LOC_04"])

    def test_resolved_obstacle_restoration(self) -> None:
        """Verify that resolving an obstacle restores original operational status in 3D scene."""
        report = self.obstacle_manager.submit_report(
            source_location_id="LOC_02",
            destination_location_id="LOC_04",
            obstacle_category="Blocked pathway",
            severity="Critical",
            description="Water leak",
            reporter_name="Student User",
        )
        self.obstacle_manager.verify_report(report["report_id"])
        blocked_set = self.obstacle_manager.get_active_blocked_edges()
        self.assertTrue(("LOC_02", "LOC_04") in blocked_set or ("LOC_04", "LOC_02") in blocked_set)

        # Resolve the obstacle
        self.obstacle_manager.resolve_report(
            report["report_id"],
            resolution_notes="Water leak repaired and floor dried",
        )
        blocked_set_after = self.obstacle_manager.get_active_blocked_edges()
        self.assertFalse(("LOC_02", "LOC_04") in blocked_set_after or ("LOC_04", "LOC_02") in blocked_set_after)

        # In 3D pathways data, edge is no longer blocked
        pathways = get_3d_pathways_data(self.test_campus_map, obstacle_manager=self.obstacle_manager)
        edge = next((p for p in pathways if set([p["source"], p["destination"]]) == {"LOC_02", "LOC_04"}), None)
        self.assertIsNotNone(edge)
        self.assertFalse(edge["is_blocked"])
        self.assertEqual(edge["color"], PALETTE["accessible_green"])

    def test_invalid_location_handling(self) -> None:
        """Verify graceful error reporting when querying route between non-existent locations."""
        route = get_3d_route_data(
            campus_map=self.campus_map,
            route_finder=self.route_finder,
            start_id="LOC_INVALID_99",
            dest_id="LOC_01",
        )
        self.assertFalse(route["success"])
        self.assertIsNotNone(route["error_message"])
        self.assertEqual(route["path"], [])
        self.assertEqual(route["waypoints"], [])

    def test_scene_payload_json_serializability(self) -> None:
        """Verify that build_3d_scene_payload produces clean, valid JSON without serialization errors."""
        payload = build_3d_scene_payload(
            campus_map=self.campus_map,
            route_finder=self.route_finder,
            obstacle_manager=self.obstacle_manager,
            start_id="LOC_01",
            dest_id="LOC_12",
            algorithm="dijkstra",
            wheelchair_accessible=True,
            selected_location_id="LOC_02",
            view_mode="combined",
        )

        # Must serialize cleanly to string
        json_str = json.dumps(payload, ensure_ascii=False)
        self.assertIsInstance(json_str, str)
        self.assertGreater(len(json_str), 1000)

        # Deserialize back to verify structure
        deserialized = json.loads(json_str)
        self.assertIn("metadata", deserialized)
        self.assertIn("locations", deserialized)
        self.assertIn("pathways", deserialized)
        self.assertIn("active_route", deserialized)
        self.assertEqual(len(deserialized["locations"]), 15)
        self.assertEqual(len(deserialized["pathways"]), 17)
        self.assertTrue(deserialized["active_route"]["success"])

    def test_html_rendering_output(self) -> None:
        """Verify that render_three_d_scene_html produces valid HTML with Three.js and scene data."""
        payload = build_3d_scene_payload(
            campus_map=self.campus_map,
            route_finder=self.route_finder,
            start_id="LOC_01",
            dest_id="LOC_06",
        )
        html = render_three_d_scene_html(payload, height=720)

        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("three.min.js", html)
        self.assertIn("OrbitControls.js", html)
        self.assertIn("webgl-canvas", html)
        self.assertIn("hud-bar-top", html)
        self.assertIn("btn-iso", html)
        self.assertIn("btn-top", html)
        self.assertIn("btn-floor-exploded", html)
        self.assertIn("LOC_01", html)
        self.assertIn("LOC_06", html)


if __name__ == "__main__":
    unittest.main()
