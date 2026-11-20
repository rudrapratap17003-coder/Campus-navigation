"""Unit tests for CampusMap and graph engine data validation."""

import copy
import json
from pathlib import Path
import unittest

from modules.campus_map import CampusDataValidationError, CampusMap, load_campus_map


class TestCampusMapEngine(unittest.TestCase):
    """Test suite for campus map loading, graph generation, and data validation."""

    @classmethod
    def setUpClass(cls) -> None:
        """Locate sample campus data file."""
        cls.data_file = Path(__file__).resolve().parent.parent / "data" / "campus_map.json"
        with open(cls.data_file, "r", encoding="utf-8") as f:
            cls.raw_data = json.load(f)

    def test_json_loading(self) -> None:
        """Verify successful JSON loading from disk."""
        cmap = load_campus_map(self.data_file)
        self.assertIsNotNone(cmap)
        self.assertIsInstance(cmap, CampusMap)
        self.assertEqual(len(cmap.locations), 15)

    def test_graph_creation_and_counts(self) -> None:
        """Verify graph node count (15) and edge count (17)."""
        cmap = load_campus_map(self.data_file)
        graph = cmap.graph

        self.assertIsNotNone(graph)
        self.assertEqual(graph.number_of_nodes(), 15, "Expected exactly 15 sample location nodes")
        self.assertEqual(graph.number_of_edges(), 17, "Expected exactly 17 sample connection edges")

        # Test node attributes
        node_01 = graph.nodes["LOC_01"]
        self.assertEqual(node_01["name"], "Main Campus Entrance")
        self.assertEqual(node_01["floor"], 0)
        self.assertEqual(node_01["building"], "Sample Academic Complex")
        self.assertEqual(node_01["category"], "entrance")
        self.assertEqual(node_01["coordinates"], (10.0, 10.0))

        # Test edge attributes
        edge_data = cmap.get_edge_data("LOC_01", "LOC_02")
        self.assertIsNotNone(edge_data)
        self.assertEqual(edge_data["distance"], 20.0)
        self.assertEqual(edge_data["weight"], 20.0)
        self.assertTrue(edge_data["wheelchair_accessible"])
        self.assertTrue(edge_data["has_ramp"])
        self.assertFalse(edge_data["has_stairs"])

    def test_location_retrieval(self) -> None:
        """Verify retrieval of locations and connected paths."""
        cmap = load_campus_map(self.data_file)

        # Retrieve valid location
        loc = cmap.get_location("LOC_04")
        self.assertIsNotNone(loc)
        self.assertEqual(loc["name"], "Elevator Lobby - Ground Floor")
        self.assertEqual(loc["floor"], 0)

        # Retrieve invalid location
        invalid_loc = cmap.get_location("LOC_NON_EXISTENT")
        self.assertIsNone(invalid_loc)

        # Retrieve all locations
        all_locs = cmap.get_all_locations()
        self.assertEqual(len(all_locs), 15)

        # Retrieve connected paths
        paths_from_loc02 = cmap.get_connected_paths("LOC_02")
        # LOC_02 connects to LOC_01, LOC_03, LOC_04, LOC_05 (4 connections)
        self.assertEqual(len(paths_from_loc02), 4)

        connected_destinations = {p["to_location_id"] for p in paths_from_loc02}
        self.assertEqual(connected_destinations, {"LOC_01", "LOC_03", "LOC_04", "LOC_05"})

        # Retrieve paths for non-existent node
        self.assertEqual(cmap.get_connected_paths("LOC_999"), [])

    def test_validation_duplicate_location_id(self) -> None:
        """Verify detection of duplicate location IDs."""
        bad_data = copy.deepcopy(self.raw_data)
        duplicate_node = copy.deepcopy(bad_data["locations"][0])
        duplicate_node["name"] = "Conflicting Duplicate Entrance"
        bad_data["locations"].append(duplicate_node)

        cmap = CampusMap()
        with self.assertRaises(CampusDataValidationError) as ctx:
            cmap.load_from_dict(bad_data)

        self.assertTrue(any("Duplicate location ID detected" in err for err in ctx.exception.errors))

    def test_validation_missing_location_field(self) -> None:
        """Verify detection of missing required location fields."""
        bad_data = copy.deepcopy(self.raw_data)
        del bad_data["locations"][0]["floor"]

        cmap = CampusMap()
        with self.assertRaises(CampusDataValidationError) as ctx:
            cmap.load_from_dict(bad_data)

        self.assertTrue(any("missing required field 'floor'" in err for err in ctx.exception.errors))

    def test_validation_invalid_distance(self) -> None:
        """Verify rejection of zero, negative, or non-numeric edge distances."""
        # Non-positive distance
        bad_data_neg = copy.deepcopy(self.raw_data)
        bad_data_neg["connections"][0]["distance"] = -5.0

        cmap = CampusMap()
        with self.assertRaises(CampusDataValidationError) as ctx:
            cmap.load_from_dict(bad_data_neg)
        self.assertTrue(any("non-positive distance" in err for err in ctx.exception.errors))

        # String distance
        bad_data_str = copy.deepcopy(self.raw_data)
        bad_data_str["connections"][0]["distance"] = "ten_meters"
        with self.assertRaises(CampusDataValidationError) as ctx:
            cmap.load_from_dict(bad_data_str)
        self.assertTrue(any("non-numeric distance" in err for err in ctx.exception.errors))

    def test_validation_nonexistent_connection_location(self) -> None:
        """Verify detection of connections referencing non-existent locations."""
        bad_data = copy.deepcopy(self.raw_data)
        bad_data["connections"].append(
            {
                "source": "LOC_01",
                "destination": "LOC_GHOST_999",
                "distance": 10.0,
                "wheelchair_accessible": True,
            }
        )

        cmap = CampusMap()
        with self.assertRaises(CampusDataValidationError) as ctx:
            cmap.load_from_dict(bad_data)

        self.assertTrue(
            any("non-existent destination location ID" in err for err in ctx.exception.errors)
        )

    def test_validation_invalid_accessibility_values(self) -> None:
        """Verify rejection of non-boolean accessibility fields."""
        bad_data = copy.deepcopy(self.raw_data)
        bad_data["connections"][0]["wheelchair_accessible"] = "yes_maybe"

        cmap = CampusMap()
        with self.assertRaises(CampusDataValidationError) as ctx:
            cmap.load_from_dict(bad_data)

        self.assertTrue(
            any(
                "invalid accessibility value for 'wheelchair_accessible'" in err
                for err in ctx.exception.errors
            )
        )

    def test_graph_summary(self) -> None:
        """Verify summary metrics calculation."""
        cmap = load_campus_map(self.data_file)
        summary = cmap.get_graph_summary()

        self.assertEqual(summary["num_nodes"], 15)
        self.assertEqual(summary["num_edges"], 17)
        self.assertTrue(summary["is_connected"])
        self.assertGreater(summary["density"], 0.0)


if __name__ == "__main__":
    unittest.main()
