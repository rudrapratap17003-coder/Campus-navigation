"""Unit tests for indoor campus map engine, floor filtering, and schematic visualizer."""

import copy
from pathlib import Path
import unittest

from database.db_manager import DatabaseManager
from modules.campus_map import CampusMap, load_campus_map
from modules.indoor_map import (
    calculate_display_coordinates,
    create_indoor_map_figure,
    detect_cross_floor_transitions,
    get_connections_for_floor,
    get_floors_in_campus,
    get_locations_for_floor,
)
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder


class TestIndoorMapSystem(unittest.TestCase):
    """Test suite covering indoor mapping, floor filtering, cross-floor transit, and visual overlays."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load campus graph and initialize RouteFinder."""
        cls.data_file = Path(__file__).resolve().parent.parent / "data" / "campus_map.json"
        cls.campus_map = load_campus_map(cls.data_file)
        cls.route_finder = RouteFinder(cls.campus_map)

    def test_floor_filtering(self) -> None:
        """Verify floor detection and filtering for nodes and pathways."""
        floors = get_floors_in_campus(self.campus_map)
        self.assertEqual(floors, [0, 1])

        # Floor 0 nodes (9 locations)
        fl0_nodes = get_locations_for_floor(self.campus_map, floor=0)
        self.assertEqual(len(fl0_nodes), 9)
        self.assertTrue(all(loc["floor"] == 0 for loc in fl0_nodes))

        # Floor 1 nodes (6 locations)
        fl1_nodes = get_locations_for_floor(self.campus_map, floor=1)
        self.assertEqual(len(fl1_nodes), 6)
        self.assertTrue(all(loc["floor"] == 1 for loc in fl1_nodes))

        # All floors
        all_nodes = get_locations_for_floor(self.campus_map, floor=None)
        self.assertEqual(len(all_nodes), 15)

        # Floor 0 intra-floor connections
        fl0_edges = get_connections_for_floor(self.campus_map, floor=0)
        self.assertEqual(len(fl0_edges), 9)

        # All connections (17 edges including 2 inter-floor)
        all_edges = get_connections_for_floor(self.campus_map, floor=None)
        self.assertEqual(len(all_edges), 17)
        cross_edges = [e for e in all_edges if e.get("is_cross_floor")]
        self.assertEqual(len(cross_edges), 2)  # Elevator and Stairs

    def test_cross_floor_route_transitions(self) -> None:
        """Verify detection of vertical elevator and staircase transitions along routes."""
        # 1. Step-free route via Elevator
        res_wheelchair = self.route_finder.find_wheelchair_route("LOC_02", "LOC_14")
        transitions_elevator = detect_cross_floor_transitions(res_wheelchair.path, self.campus_map)

        self.assertEqual(len(transitions_elevator), 1)
        trans1 = transitions_elevator[0]
        self.assertEqual(trans1["from_id"], "LOC_04")
        self.assertEqual(trans1["to_id"], "LOC_10")
        self.assertEqual(trans1["from_floor"], 0)
        self.assertEqual(trans1["to_floor"], 1)
        self.assertEqual(trans1["connector_type"], "Elevator")
        self.assertTrue(trans1["wheelchair_accessible"])
        self.assertIn("elevator", trans1["guidance"].lower())

        # 2. Standard route via Stairs
        res_stairs = self.route_finder.find_shortest_distance("LOC_02", "LOC_14", wheelchair_accessible=False)
        transitions_stairs = detect_cross_floor_transitions(res_stairs.path, self.campus_map)

        self.assertEqual(len(transitions_stairs), 1)
        trans2 = transitions_stairs[0]
        self.assertEqual(trans2["from_id"], "LOC_05")
        self.assertEqual(trans2["to_id"], "LOC_11")
        self.assertEqual(trans2["connector_type"], "Stairway")
        self.assertFalse(trans2["wheelchair_accessible"])
        self.assertIn("stairs", trans2["guidance"].lower())

    def test_route_highlighting_figure_generation(self) -> None:
        """Verify Plotly map generation with active route highlighting and origin/dest pins."""
        res = self.route_finder.find_shortest_distance("LOC_01", "LOC_06")
        fig = create_indoor_map_figure(
            campus_map=self.campus_map,
            floor_filter=0,
            highlight_route=res.path,
            selected_location_id="LOC_02",
        )

        trace_names = [trace.name for trace in fig.data if hasattr(trace, "name") and trace.name]
        self.assertIn("Active Navigation Route", trace_names)
        self.assertIn("Route Origin", trace_names)
        self.assertIn("Route Destination", trace_names)
        self.assertIn("Selected Location", trace_names)

    def test_multi_floor_side_by_side_coordinates(self) -> None:
        """Verify side-by-side coordinate plate offset when viewing All Floors."""
        coords_all = calculate_display_coordinates(self.campus_map, floor_filter=None)
        coords_fl0 = calculate_display_coordinates(self.campus_map, floor_filter=0)

        # Floor 0 node LOC_01 remains unchanged
        self.assertEqual(coords_all["LOC_01"][0], coords_fl0["LOC_01"][0])

        # Floor 1 node LOC_10 is offset by +65 units in All Floors view
        raw_x_10 = self.campus_map.get_location("LOC_10")["x"]
        self.assertEqual(coords_all["LOC_10"][0], raw_x_10 + 65.0)

    def test_missing_coordinate_handling(self) -> None:
        """Verify deterministic fallback coordinates when a location is missing (X, Y)."""
        bad_map = copy.deepcopy(self.campus_map)
        bad_map.locations["LOC_01"]["x"] = None
        bad_map.locations["LOC_01"]["y"] = None

        coords = calculate_display_coordinates(bad_map, floor_filter=0)
        self.assertIn("LOC_01", coords)
        x, y = coords["LOC_01"]
        self.assertIsInstance(x, float)
        self.assertIsInstance(y, float)

        # Verify figure still builds without error
        fig = create_indoor_map_figure(campus_map=bad_map, floor_filter=0)
        self.assertIsNotNone(fig)

    def test_obstacle_map_visualization_and_restoration(self) -> None:
        """Verify map edge updates to red blocked and restores to green upon obstacle resolution."""
        db = DatabaseManager(":memory:")
        fresh_map = load_campus_map(self.data_file)
        obs_mgr = ObstacleManager(db_manager=db, campus_map=fresh_map)

        # 1. Initially edge LOC_09 <-> LOC_08 is open (Green line)
        fig_initial = create_indoor_map_figure(fresh_map, floor_filter=0)
        edge_traces_initial = [
            t for t in fig_initial.data
            if t.mode == "lines" and hasattr(t, "hovertext") and t.hovertext and "LOC_09" in str(t.hovertext) and "LOC_08" in str(t.hovertext)
        ]
        self.assertTrue(any("Accessible" in str(t.hovertext) for t in edge_traces_initial))

        # 2. Submit & Verify obstacle -> edge status becomes 'blocked' (Red line)
        rep = obs_mgr.submit_report(
            obstacle_category="Blocked pathway",
            severity="Critical",
            description="Deep trench",
            source_location_id="LOC_09",
            destination_location_id="LOC_08",
        )
        obs_mgr.verify_report(rep["report_id"])

        fig_blocked = create_indoor_map_figure(fresh_map, floor_filter=0)
        edge_traces_blocked = [
            t for t in fig_blocked.data
            if t.mode == "lines" and hasattr(t, "hovertext") and t.hovertext and "LOC_09" in str(t.hovertext) and "LOC_08" in str(t.hovertext)
        ]
        self.assertTrue(any("Blocked Pathway" in str(t.hovertext) for t in edge_traces_blocked))

        # 3. Resolve obstacle -> edge restored to 'open'
        obs_mgr.resolve_report(rep["report_id"], "Trench filled")
        fig_restored = create_indoor_map_figure(fresh_map, floor_filter=0)
        edge_traces_restored = [
            t for t in fig_restored.data
            if t.mode == "lines" and hasattr(t, "hovertext") and t.hovertext and "LOC_09" in str(t.hovertext) and "LOC_08" in str(t.hovertext)
        ]
        self.assertTrue(any("Accessible" in str(t.hovertext) for t in edge_traces_restored))

        db.close()


if __name__ == "__main__":
    unittest.main()
