"""Comprehensive graph integrity, navigation accuracy, and system validation test suite.

Validates Phase 14 requirements:
1. Full campus graph integrity: uniqueness of all 79 node IDs, valid names, floor mappings, coordinates.
2. Pathway integrity: all 106 edges have valid positive distances, non-negative times, and valid attributes.
3. Graph connectivity: single connected component in both standard and wheelchair step-free subgraphs.
4. All-pairs reachability: verifies complete pairwise connectivity across all 79 nodes.
5. Five-floor FET room-to-room navigation: Ground Floor to Floors 1, 2, 3, 4 and reverse.
6. Multi-route trade-off comparison: Dijkstra (distance) vs BFS (hops) vs Detour Alternative.
7. Multiple concurrent obstacles on a single pathway: resolving one leaves the edge blocked until all are resolved.
8. Audit trail logging on verification and resolution.
9. Graceful error handling for severed wheelchair routes.
"""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import networkx as nx

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
    get_jain_multi_route_comparison,
    load_jain_campus_map,
    render_jain_digital_twin_html,
)
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder, RouteResult


class TestCampusGraphIntegrityAndValidation(unittest.TestCase):
    """Test suite covering Phase 14 graph validation, multi-route intelligence, and obstacle concurrency."""

    def setUp(self) -> None:
        """Initialize campus map, temporary database, and obstacle manager."""
        self.cmap = load_jain_campus_map()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_p14_graph.db"
        self.db_mgr = DatabaseManager(self.db_path)
        self.obs_mgr = ObstacleManager(db_manager=self.db_mgr, campus_map=self.cmap)
        self.route_finder = RouteFinder(self.cmap)

    def tearDown(self) -> None:
        """Clean up temporary test resources."""
        self.temp_dir.cleanup()

    def test_all_79_locations_unique_and_valid(self) -> None:
        """Verify that all 79 locations have unique IDs, non-empty names, and valid attributes."""
        all_locs = self.cmap.get_all_locations()
        self.assertEqual(len(all_locs), 79, "Expected exactly 79 locations in JAIN Global Campus dataset")

        ids = [loc["id"] for loc in all_locs]
        self.assertEqual(len(ids), len(set(ids)), "All location IDs must be strictly unique")

        valid_floors = {-1, 0, 1, 2, 3, 4}
        for loc in all_locs:
            self.assertTrue(loc["id"].strip(), "Location ID cannot be empty")
            self.assertTrue(loc["name"].strip(), "Location name cannot be empty")
            self.assertIn(loc["floor"], valid_floors, f"Invalid floor assignment {loc['floor']} for {loc['id']}")
            self.assertIsInstance(loc["x"], (int, float), f"Invalid x coordinate for {loc['id']}")
            self.assertIsInstance(loc["y"], (int, float), f"Invalid y coordinate for {loc['id']}")
            self.assertIsInstance(loc["wheelchair_accessible"], bool)
            self.assertTrue(loc["building"].strip(), f"Building name cannot be empty for {loc['id']}")

    def test_all_106_pathways_attributes_and_positive_weights(self) -> None:
        """Verify that all 106 pathways have positive distances, valid times, and correct endpoints."""
        self.assertEqual(self.cmap.graph.number_of_edges(), 106, "Expected exactly 106 pathways")

        for u, v, data in self.cmap.graph.edges(data=True):
            self.assertNotEqual(u, v, f"Self-loop detected: {u} -> {v}")
            self.assertGreater(data.get("distance", 0.0), 0.0, f"Edge ({u}, {v}) must have positive distance")
            self.assertGreater(data.get("estimated_time", 0.0), 0.0, f"Edge ({u}, {v}) must have positive travel time")
            self.assertIn("wheelchair_accessible", data)
            self.assertIn("has_stairs", data)
            self.assertIn("has_ramp", data)
            self.assertIn("has_elevator", data)

    def test_graph_single_connected_component(self) -> None:
        """Verify that the campus graph consists of exactly 1 connected component (no isolated nodes)."""
        num_components = nx.number_connected_components(self.cmap.graph)
        self.assertEqual(num_components, 1, f"Expected 1 connected component, found {num_components}")

    def test_wheelchair_subgraph_connected_component(self) -> None:
        """Verify that the wheelchair-accessible subgraph (step-free edges only) connects all 79 nodes."""
        acc_edges = [
            (u, v) for u, v, d in self.cmap.graph.edges(data=True)
            if d.get("wheelchair_accessible") and not d.get("has_stairs")
        ]
        self.assertEqual(len(acc_edges), 88, f"Expected 88 step-free edges, found {len(acc_edges)}")

        g_acc = nx.Graph()
        for loc in self.cmap.get_all_locations():
            g_acc.add_node(loc["id"])
        g_acc.add_edges_from(acc_edges)

        num_acc_components = nx.number_connected_components(g_acc)
        self.assertEqual(num_acc_components, 1, "Wheelchair step-free graph must be fully connected across all 79 nodes")

    def test_five_floor_vertical_circulation_alignment(self) -> None:
        """Verify continuous vertical alignment of elevator bank and 4 cardinal stairwell towers."""
        # Elevator connects 0F -> 1F -> 2F -> 3F -> 4F
        for fl in range(4):
            u_elev = f"FET_{fl}F_ELEVATOR"
            v_elev = f"FET_{fl+1}F_ELEVATOR"
            self.assertTrue(self.cmap.graph.has_edge(u_elev, v_elev), f"Missing elevator link {u_elev} -> {v_elev}")
            edata = self.cmap.graph[u_elev][v_elev]
            self.assertTrue(edata.get("has_elevator"))
            self.assertTrue(edata.get("wheelchair_accessible"))

        # Stairwells connect 0F -> 1F -> 2F -> 3F -> 4F
        for card in ["NORTH", "EAST", "SOUTH", "WEST"]:
            for fl in range(4):
                u_stair = f"FET_{fl}F_STAIRS_{card}"
                v_stair = f"FET_{fl+1}F_STAIRS_{card}"
                self.assertTrue(self.cmap.graph.has_edge(u_stair, v_stair), f"Missing stairwell link {u_stair} -> {v_stair}")
                sdata = self.cmap.graph[u_stair][v_stair]
                self.assertTrue(sdata.get("has_stairs"))
                self.assertFalse(sdata.get("wheelchair_accessible"))

    def test_room_to_room_five_floor_navigation(self) -> None:
        """Verify route calculation from Ground Floor entrance to destinations on all 4 upper floors."""
        destinations = [
            ("FET_1F_LIBRARY", 1),
            ("FET_2F_AI_RESEARCH", 2),
            ("FET_3F_AVIONICS_LAB", 3),
            ("FET_4F_HPC_CLUSTER", 4),
        ]
        for dest_id, target_floor in destinations:
            # Test in standard pedestrian mode
            route_std = self.route_finder.find_route(
                source="FET_G_ENTRANCE_FOYER",
                destination=dest_id,
                algorithm="dijkstra",
                wheelchair_accessible=False,
            )
            self.assertTrue(route_std.success, f"Route to {dest_id} failed in standard mode")
            self.assertGreater(route_std.total_distance, 0.0)

            # Test in wheelchair mode (must strictly enforce elevator and 0 stairs)
            route_acc = self.route_finder.find_route(
                source="FET_G_ENTRANCE_FOYER",
                destination=dest_id,
                algorithm="dijkstra",
                wheelchair_accessible=True,
            )
            self.assertTrue(route_acc.success, f"Route to {dest_id} failed in wheelchair mode")
            self.assertTrue(route_acc.is_accessible)
            self.assertTrue(any(s.has_elevator for s in route_acc.steps), "Multi-floor wheelchair route must use elevator")
            self.assertFalse(any(s.has_stairs for s in route_acc.steps), "Wheelchair route must avoid all staircases")

            # Verify symmetric reverse route
            route_rev = self.route_finder.find_route(
                source=dest_id,
                destination="FET_G_ENTRANCE_FOYER",
                algorithm="dijkstra",
                wheelchair_accessible=True,
            )
            self.assertTrue(route_rev.success, f"Reverse route from {dest_id} failed")
            self.assertEqual(route_acc.total_distance, route_rev.total_distance, "Distance must be symmetric")

    def test_intelligent_multi_route_comparison(self) -> None:
        """Verify intelligent route trade-off comparison between Dijkstra and BFS algorithms."""
        comparison = get_jain_multi_route_comparison(
            campus_map=self.cmap,
            route_finder=self.route_finder,
            start_id="OUT_GATE_MAIN",
            dest_id="FET_4F_HPC_CLUSTER",
            wheelchair_accessible=True,
        )
        self.assertIn("dijkstra", comparison)
        self.assertIn("bfs", comparison)

        dijkstra_info = comparison["dijkstra"]
        bfs_info = comparison["bfs"]

        self.assertIsNotNone(dijkstra_info)
        self.assertIsNotNone(bfs_info)

        # Dijkstra must have equal or shorter physical distance than BFS
        self.assertLessEqual(dijkstra_info["total_distance"], bfs_info["total_distance"] + 0.1)
        # BFS must have equal or fewer steps than Dijkstra
        self.assertLessEqual(bfs_info["edge_count"], dijkstra_info["edge_count"])

        self.assertIn("rationale", dijkstra_info)
        self.assertIn("floor_transitions", dijkstra_info)
        self.assertEqual(dijkstra_info["floor_transitions"], 5)

    def test_multi_obstacle_concurrency_resolution(self) -> None:
        """Verify that when multiple obstacles block an edge, resolving one keeps the edge blocked until all are resolved."""
        edge_u = "FET_0F_ELEVATOR"
        edge_v = "FET_1F_ELEVATOR"

        # Initially edge is open
        self.assertEqual(self.cmap.graph[edge_u][edge_v].get("status"), "open")

        # 1. Submit first report & verify it
        rep1 = self.obs_mgr.submit_report(
            reporter_name="Inspector 1",
            source_location_id=edge_u,
            destination_location_id=edge_v,
            obstacle_category="Elevator unavailable",
            severity="High",
            description="Motor servicing",
        )
        r1_id = rep1["report_id"]
        self.obs_mgr.update_report_status(r1_id, "Verified")
        self.assertEqual(self.cmap.graph[edge_u][edge_v].get("status"), "blocked")

        # 2. Submit second report on SAME edge & verify it
        rep2 = self.obs_mgr.submit_report(
            reporter_name="Inspector 2",
            source_location_id=edge_u,
            destination_location_id=edge_v,
            obstacle_category="Construction work",
            severity="Medium",
            description="Shaft electrical rewiring",
        )
        r2_id = rep2["report_id"]
        self.obs_mgr.update_report_status(r2_id, "Verified")
        self.assertEqual(self.cmap.graph[edge_u][edge_v].get("status"), "blocked")

        # 3. Resolve ONLY first report with resolution notes
        self.obs_mgr.update_report_status(r1_id, "Resolved", resolution_notes="Motor servicing completed.")

        # CRITICAL ASSERTION: Edge must STILL be blocked because report 2 is still active!
        self.assertEqual(
            self.cmap.graph[edge_u][edge_v].get("status"),
            "blocked",
            "Pathway must remain blocked while secondary verified obstacle remains active",
        )

        # 4. Resolve second report
        self.obs_mgr.update_report_status(r2_id, "Resolved", resolution_notes="Electrical rewiring signed off.")

        # Now that both are resolved, edge must return to open status
        self.assertEqual(
            self.cmap.graph[edge_u][edge_v].get("status"),
            "open",
            "Pathway must return to open status once all verified obstacles are resolved",
        )

    def test_audit_trail_recorded_on_status_change(self) -> None:
        """Verify that verifying and resolving an obstacle writes immutable records in the database audit log."""
        rep = self.obs_mgr.submit_report(
            reporter_name="Tester",
            source_location_id="OUT_GATE_MAIN",
            destination_location_id="OUT_QUAD_CENTRAL",
            obstacle_category="Blocked pathway",
            severity="Medium",
            description="Temporary campus event barricades",
        )
        r_id = rep["report_id"]

        # Verify report
        self.obs_mgr.update_report_status(r_id, "Verified")
        logs = self.db_mgr.get_audit_logs(limit=10)
        verify_logs = [
            l for l in logs
            if "VERIFY" in str(l.get("action")).upper() or l.get("new_status") == "Verified"
        ]
        self.assertGreaterEqual(len(verify_logs), 1, "Expected audit log record for obstacle verification")

        # Resolve report
        self.obs_mgr.update_report_status(r_id, "Resolved", resolution_notes="Barricades dismantled.")
        logs_after = self.db_mgr.get_audit_logs(limit=10)
        resolve_logs = [
            l for l in logs_after
            if "RESOLVE" in str(l.get("action")).upper() or l.get("new_status") == "Resolved"
        ]
        self.assertGreaterEqual(len(resolve_logs), 1, "Expected audit log record for obstacle resolution")

    def test_unreachable_destination_reporting(self) -> None:
        """Verify that when all vertical elevators are blocked, wheelchair routing reports unreachable destination."""
        # Block elevator 0F -> 1F
        rep = self.obs_mgr.submit_report(
            reporter_name="Admin",
            source_location_id="FET_0F_ELEVATOR",
            destination_location_id="FET_1F_ELEVATOR",
            obstacle_category="Elevator unavailable",
            severity="Critical",
            description="Shaft out of order",
        )
        self.obs_mgr.update_report_status(rep["report_id"], "Verified")

        # Wheelchair route from Ground Floor to Level 4 must fail gracefully
        res_acc = self.route_finder.find_route(
            source="FET_G_ENTRANCE_FOYER",
            destination="FET_4F_HPC_CLUSTER",
            algorithm="dijkstra",
            wheelchair_accessible=True,
        )
        self.assertFalse(res_acc.success, "Wheelchair route must fail when elevator core is blocked")
        self.assertIn("No accessible route found", res_acc.error_message)

        # Standard route must still succeed via staircase detour
        res_std = self.route_finder.find_route(
            source="FET_G_ENTRANCE_FOYER",
            destination="FET_4F_HPC_CLUSTER",
            algorithm="dijkstra",
            wheelchair_accessible=False,
        )
        self.assertTrue(res_std.success, "Standard pedestrian route should succeed via stairwells")
        self.assertTrue(any(s.has_stairs for s in res_std.steps), "Detour should traverse staircases")


if __name__ == "__main__":
    unittest.main()
