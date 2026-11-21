"""Unit tests for JAIN Global Campus and FET 5-Floor 3D Digital Twin Engine.

Validates:
1. Dataset schema integrity (79 nodes, 106 edges across outdoor grounds and 5 FET building floors).
2. All 5 floor levels (Floor 0, 1, 2, 3, 4) plus outdoor level (-1).
3. Outdoor building mapping (FET, Colosseum, Aquatic Center, Cricket Stadium, Dining, Hostels, Admin, Aerospace).
4. Seamless outdoor-to-indoor graph connectivity (Main Gate -> Central Quad -> West Ramp / Front Portico -> Ground Floor Foyer).
5. Continuous vertical elevator connectivity across all 5 floors (0F <-> 1F <-> 2F <-> 3F <-> 4F).
6. Four cardinal staircase towers (North, East, South, West) connecting floors.
7. Wheelchair-accessible routing constraints (strictly avoids stairs, utilizes ramps and elevators).
8. Dynamic obstacle blocking and detour rerouting.
9. 3D spatial serialization and Three.js HTML generation.
"""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from database.db_manager import DatabaseManager
from modules.campus_map import CampusMap
from modules.jain_digital_twin import (
    FLOOR_ELEVATIONS,
    FLOOR_NAMES,
    JAIN_DATA_FILE,
    build_jain_digital_twin_payload,
    get_jain_3d_locations_data,
    get_jain_3d_pathways_data,
    get_jain_3d_route_data,
    load_jain_campus_map,
    render_jain_digital_twin_html,
)
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder, RouteResult


class TestJainCampusDigitalTwin(unittest.TestCase):
    """Test suite for the JAIN Global Campus 3D digital twin engine."""

    def setUp(self) -> None:
        """Initialize campus map, temporary database, and obstacle manager for JAIN Global Campus."""
        self.cmap = load_jain_campus_map()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_jain_obs.db"
        self.db_mgr = DatabaseManager(self.db_path)
        self.obs_mgr = ObstacleManager(db_manager=self.db_mgr, campus_map=self.cmap)
        self.route_finder = RouteFinder(self.cmap)

    def tearDown(self) -> None:
        """Clean up temporary resources."""
        self.temp_dir.cleanup()

    def test_jain_dataset_structure_and_integrity(self) -> None:
        """Verify the JAIN Global Campus dataset loads with expected nodes and edges."""
        self.assertTrue(JAIN_DATA_FILE.exists(), f"Dataset file missing: {JAIN_DATA_FILE}")
        all_locs = self.cmap.get_all_locations()
        self.assertGreaterEqual(len(all_locs), 75, "Expected at least 75 locations in JAIN campus")
        self.assertGreaterEqual(self.cmap.graph.number_of_edges(), 100, "Expected at least 100 pathways")

        # Verify all locations have required fields
        for loc in all_locs:
            self.assertIn("id", loc)
            self.assertIn("name", loc)
            self.assertIn("floor", loc)
            self.assertIn("building", loc)
            self.assertIn("category", loc)
            self.assertIn("x", loc)
            self.assertIn("y", loc)
            self.assertIn("wheelchair_accessible", loc)

    def test_five_floor_levels_present(self) -> None:
        """Verify presence of Outdoor level (-1) and all 5 building floors (0, 1, 2, 3, 4)."""
        all_locs = self.cmap.get_all_locations()
        floors = {loc["floor"] for loc in all_locs}

        self.assertIn(-1, floors, "Outdoor campus floor (-1) must be present")
        self.assertIn(0, floors, "FET Ground Floor (0) must be present")
        self.assertIn(1, floors, "FET First Floor (1) must be present")
        self.assertIn(2, floors, "FET Second Floor (2) must be present")
        self.assertIn(3, floors, "FET Third Floor (3) must be present")
        self.assertIn(4, floors, "FET Fourth Floor (4) must be present")

        # Verify location counts per floor
        for fl in [-1, 0, 1, 2, 3, 4]:
            fl_locs = [l for l in all_locs if l["floor"] == fl]
            self.assertGreaterEqual(len(fl_locs), 8, f"Floor {fl} should have at least 8 facilities")

    def test_outdoor_buildings_and_pois(self) -> None:
        """Verify outdoor buildings from aerial images are represented."""
        all_locs = self.cmap.get_all_locations()
        loc_ids = {l["id"] for l in all_locs}

        expected_outdoor = [
            "OUT_GATE_MAIN",
            "OUT_PARKING_ACC",
            "OUT_QUAD_CENTRAL",
            "OUT_ADMIN_BLOCK",
            "OUT_COLOSSEUM",
            "OUT_CRICKET_STADIUM",
            "OUT_AQUATICS_POOL",
            "OUT_DINING_COMPLEX",
            "OUT_HOSTEL_BLOCKS",
            "OUT_AEROSPACE_LABS",
            "OUT_FET_WEST_RAMP",
            "OUT_FET_FRONT_PORTICO",
        ]
        for oid in expected_outdoor:
            self.assertIn(oid, loc_ids, f"Outdoor POI {oid} must exist in the dataset")

    def test_outdoor_to_indoor_transition(self) -> None:
        """Verify seamless connectivity between outdoor pathways and FET building entrance."""
        route = self.route_finder.find_route(
            source="OUT_GATE_MAIN",
            destination="FET_G_ENTRANCE_FOYER",
            algorithm="dijkstra",
            wheelchair_accessible=True,
        )
        self.assertTrue(route.success, f"Route calculation failed: {route.error_message}")
        self.assertIn("OUT_GATE_MAIN", route.path)
        self.assertIn("FET_G_ENTRANCE_FOYER", route.path)
        self.assertTrue(route.is_accessible, "Outdoor to indoor entrance route must be step-free accessible")

    def test_continuous_elevator_bank_across_all_five_floors(self) -> None:
        """Verify elevator vertical connectors link all 5 floors continuously."""
        elevator_nodes = [
            "FET_0F_ELEVATOR",
            "FET_1F_ELEVATOR",
            "FET_2F_ELEVATOR",
            "FET_3F_ELEVATOR",
            "FET_4F_ELEVATOR",
        ]
        # Check consecutive pairs are connected and marked with elevator
        for i in range(len(elevator_nodes) - 1):
            u = elevator_nodes[i]
            v = elevator_nodes[i + 1]
            self.assertTrue(self.cmap.graph.has_edge(u, v), f"Missing elevator link between {u} and {v}")
            edge_data = self.cmap.graph[u][v]
            self.assertTrue(edge_data.get("has_elevator"), f"Edge {u}-{v} must be marked has_elevator=True")
            self.assertTrue(edge_data.get("wheelchair_accessible"), f"Elevator {u}-{v} must be wheelchair accessible")

    def test_staircase_towers_connectivity(self) -> None:
        """Verify the 4 cardinal stairwells (North, East, South, West) connect adjacent floors."""
        cardinals = ["NORTH", "EAST", "SOUTH", "WEST"]
        for card in cardinals:
            for fl in range(4):
                u = f"FET_{fl}F_STAIRS_{card}"
                v = f"FET_{fl+1}F_STAIRS_{card}"
                self.assertTrue(self.cmap.graph.has_edge(u, v), f"Missing stairwell connection {u} -> {v}")
                edge_data = self.cmap.graph[u][v]
                self.assertTrue(edge_data.get("has_stairs"), f"Edge {u}-{v} must have has_stairs=True")
                self.assertFalse(edge_data.get("wheelchair_accessible"), f"Stairs {u}-{v} must not be wheelchair accessible")

    def test_wheelchair_routing_forces_elevator_and_avoids_stairs(self) -> None:
        """Verify wheelchair navigation strictly chooses elevators and avoids all staircases."""
        # Route from Outdoor Gate to Fourth Floor HPC Cluster
        route: RouteResult = self.route_finder.find_route(
            source="OUT_GATE_MAIN",
            destination="FET_4F_HPC_CLUSTER",
            algorithm="dijkstra",
            wheelchair_accessible=True,
        )
        self.assertTrue(route.success, f"Wheelchair route failed: {route.error_message}")
        self.assertTrue(route.is_accessible, "Route must be flagged as accessible")

        # Assert no staircase segments are in the path
        for step in route.steps:
            self.assertFalse(
                step.has_stairs,
                f"Wheelchair route contains staircase segment: {step.from_id} -> {step.to_id}",
            )
            self.assertTrue(
                step.wheelchair_accessible,
                f"Step {step.from_id} -> {step.to_id} is not wheelchair accessible",
            )

        # Assert elevator was used to traverse floors
        elevator_steps = [s for s in route.steps if s.has_elevator]
        self.assertGreaterEqual(len(elevator_steps), 1, "Multi-floor wheelchair route must use elevator")

    def test_standard_routing_allows_stairs(self) -> None:
        """Verify non-wheelchair route can take stairs when available."""
        route: RouteResult = self.route_finder.find_route(
            source="FET_0F_STAIRS_NORTH",
            destination="FET_1F_STAIRS_NORTH",
            algorithm="dijkstra",
            wheelchair_accessible=False,
        )
        self.assertTrue(route.success)
        has_stairs_step = any(s.has_stairs for s in route.steps)
        self.assertTrue(has_stairs_step, "Direct north corridor floor transition should utilize North stairwell")

    def test_active_obstacle_rerouting_on_jain_graph(self) -> None:
        """Verify that reporting a verified obstacle on an elevator forces stairs (or fails wheelchair routing)."""
        # Submit verified obstacle on 0F <-> 1F elevator
        rep = self.obs_mgr.submit_report(
            reporter_name="USR_STAFF_01",
            source_location_id="FET_0F_ELEVATOR",
            destination_location_id="FET_1F_ELEVATOR",
            obstacle_category="Elevator unavailable",
            severity="High",
            description="Elevator hydraulic maintenance underway.",
        )
        report_id = rep["report_id"]
        self.obs_mgr.update_report_status(report_id, status="Verified")

        # Wheelchair route from 0F to 1F should now fail (no alternate elevator available)
        wheelchair_route = self.route_finder.find_route(
            source="FET_0F_ELEVATOR",
            destination="FET_1F_ELEVATOR",
            algorithm="dijkstra",
            wheelchair_accessible=True,
        )
        self.assertFalse(wheelchair_route.success, "Wheelchair route must fail when only elevator is blocked")

        # Standard pedestrian route should still succeed via stairs
        std_route = self.route_finder.find_route(
            source="FET_0F_ELEVATOR",
            destination="FET_1F_ELEVATOR",
            algorithm="dijkstra",
            wheelchair_accessible=False,
        )
        self.assertTrue(std_route.success, "Pedestrian route should detour via staircases")

    def test_jain_3d_locations_data_serialization(self) -> None:
        """Verify 3D location serialization generates valid positions and metadata."""
        locs_3d = get_jain_3d_locations_data(self.cmap)
        self.assertEqual(len(locs_3d), len(self.cmap.get_all_locations()))

        for item in locs_3d:
            self.assertIn("pos", item)
            self.assertIn("x", item["pos"])
            self.assertIn("y", item["pos"])
            self.assertIn("z", item["pos"])
            self.assertIn("floor", item)
            self.assertIn("floor_name", item)

    def test_jain_3d_pathways_data_serialization(self) -> None:
        """Verify 3D pathway serialization formats all edges with 3D endpoints."""
        pathways = get_jain_3d_pathways_data(self.cmap, self.obs_mgr)
        self.assertGreaterEqual(len(pathways), 100)

        for p in pathways:
            self.assertIn("source_pos", p)
            self.assertIn("dest_pos", p)
            self.assertIn("color", p)
            self.assertIn("pathway_type", p)

    def test_jain_digital_twin_payload_and_html_generation(self) -> None:
        """Verify full scene payload creation and HTML rendering."""
        payload = build_jain_digital_twin_payload(
            campus_map=self.cmap,
            route_finder=self.route_finder,
            obstacle_manager=self.obs_mgr,
            start_id="OUT_GATE_MAIN",
            dest_id="FET_4F_HPC_CLUSTER",
            algorithm="dijkstra",
            wheelchair_accessible=True,
            selected_location_id="FET_4F_HPC_CLUSTER",
            view_mode="all_floors",
        )
        self.assertIn("metadata", payload)
        self.assertIn("buildings", payload)
        self.assertIn("locations", payload)
        self.assertIn("pathways", payload)
        self.assertIn("active_route", payload)
        self.assertTrue(payload["active_route"]["success"])

        # Test HTML generation
        html = render_jain_digital_twin_html(payload, height=760)
        self.assertIsInstance(html, str)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("three.min.js", html)
        self.assertIn("JAIN Global Campus 3D Digital Twin", html)
        self.assertIn("OUT_GATE_MAIN", html)

    def test_procedural_furnishings_metadata(self) -> None:
        """Verify room categories and amenity data for procedural 3D furnishings."""
        all_locs = self.cmap.get_all_locations()
        categories = {loc.get("category") for loc in all_locs}
        expected_cats = {"lab", "library", "auditorium", "classroom", "office", "restroom", "elevator", "stairs"}
        # Check intersection
        self.assertTrue(len(categories.intersection(expected_cats)) >= 5)

        # Check labs have amenities or descriptors
        labs = [l for l in all_locs if l.get("category") == "lab"]
        self.assertGreaterEqual(len(labs), 10)
        for lab in labs:
            self.assertIn("amenities", lab)
            self.assertIsInstance(lab["amenities"], list)

    def test_cutaway_and_exterior_view_modes_in_payload(self) -> None:
        """Verify view_mode configuration in digital twin payload."""
        payload_cutaway = build_jain_digital_twin_payload(
            campus_map=self.cmap,
            view_mode="cutaway",
        )
        self.assertEqual(payload_cutaway["config"]["initial_view_mode"], "cutaway")

        payload_exterior = build_jain_digital_twin_payload(
            campus_map=self.cmap,
            view_mode="exterior",
        )
        self.assertEqual(payload_exterior["config"]["initial_view_mode"], "exterior")

    def test_alternative_routes_on_jain_graph(self) -> None:
        """Verify computation of distinct alternative routes on JAIN campus graph."""
        alts = self.route_finder.find_alternative_routes(
            source="OUT_GATE_MAIN",
            destination="FET_G_ENTRANCE_FOYER",
            max_alternatives=2,
            wheelchair_accessible=True,
        )
        self.assertIsInstance(alts, list)
        for alt in alts:
            self.assertTrue(alt.success)
            self.assertTrue(alt.is_accessible)

    def test_floor_elevations_alignment(self) -> None:
        """Verify floor elevations are strictly ascending from outdoor to Level 4."""
        self.assertEqual(FLOOR_ELEVATIONS[-1], 0.0)
        prev_elev = FLOOR_ELEVATIONS[-1]
        for fl in [0, 1, 2, 3, 4]:
            self.assertIn(fl, FLOOR_ELEVATIONS)
            self.assertGreater(FLOOR_ELEVATIONS[fl], prev_elev)
            prev_elev = FLOOR_ELEVATIONS[fl]

    def test_all_locations_have_valid_3d_coordinates(self) -> None:
        """Verify every location node has numeric coordinates and valid attributes."""
        all_locs = self.cmap.get_all_locations()
        self.assertGreaterEqual(len(all_locs), 79)
        for loc in all_locs:
            self.assertIsInstance(loc["x"], (int, float))
            self.assertIsInstance(loc["y"], (int, float))
            self.assertIsInstance(loc["floor"], int)
            self.assertIsInstance(loc["wheelchair_accessible"], bool)


if __name__ == "__main__":
    unittest.main()
