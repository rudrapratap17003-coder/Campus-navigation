"""Verify full demonstration rehearsal workflow across routing, accessibility, obstacles, and 3D."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db_manager import DatabaseManager
from modules.jain_digital_twin import load_jain_campus_map
from algorithms.dijkstra import dijkstra_shortest_path
from algorithms.bfs import bfs_shortest_path
from modules.accessibility import AccessibilityEngine
from modules.obstacle_manager import ObstacleManager
from modules.three_d_map import build_3d_scene_payload

def run_rehearsal():
    print("--- FINAL STAGE 12 REHEARSAL VERIFICATION ---")
    
    # 1. Dataset loading
    jain_map = load_jain_campus_map()
    print(f"1. JAIN Campus Map: {len(jain_map.graph.nodes)} nodes, {len(jain_map.graph.edges)} edges.")
    assert len(jain_map.graph.nodes) == 79
    assert len(jain_map.graph.edges) == 106

    # 2. Routing: Main Gate to 2nd Floor AI Research Lab
    src = "OUT_GATE_MAIN"
    dst = "FET_2F_AI_RESEARCH"
    route_dijkstra = dijkstra_shortest_path(jain_map.graph, src, dst, weight="distance")
    route_bfs = bfs_shortest_path(jain_map.graph, src, dst)
    print(f"2. Dijkstra path: {len(route_dijkstra.path)} nodes, distance: {route_dijkstra.total_distance:.1f}m")
    print(f"3. BFS path: {len(route_bfs.path)} nodes, distance: {route_bfs.total_distance:.1f}m")
    assert route_dijkstra.success
    assert route_bfs.success

    # 3. Wheelchair routing: ensure step-free elevator and ramp navigation
    route_wheelchair = dijkstra_shortest_path(jain_map.graph, src, dst, weight="distance", wheelchair_accessible=True)
    print(f"4. Wheelchair route success: {route_wheelchair.success}, path length: {len(route_wheelchair.path)} nodes")
    assert route_wheelchair.success
    assert "OUT_FET_WEST_RAMP" in route_wheelchair.path
    assert "FET_0F_ELEVATOR" in route_wheelchair.path
    assert "FET_2F_ELEVATOR" in route_wheelchair.path

    # Accessibility evaluation
    acc_engine = AccessibilityEngine(jain_map)
    assessment = acc_engine.evaluate_route_accessibility(route_wheelchair.path)
    print(f"5. Route Assessment: classification={assessment.overall_classification}, score={assessment.accessibility_score}")
    assert assessment.success

    # 4. Obstacle Lifecycle & Graph mutation
    db = DatabaseManager()
    obs = ObstacleManager(db_manager=db, campus_map=jain_map)
    rep = obs.submit_report(
        obstacle_category="Blocked pathway",
        severity="High",
        description="Stage 12 Rehearsal Obstacle",
        source_location_id="FET_G_ENTRANCE_FOYER",
        destination_location_id="FET_0F_STAIRS_SOUTH",
        reporter_name="Student Presenter"
    )
    rep_id = rep["report_id"]
    print(f"6. Created obstacle report #{rep_id}")
    assert rep_id is not None

    # Verify obstacle as Administrator / Field Staff
    ver_res = obs.verify_report(rep_id, actor_user={"username": "admin_demo", "role": "Administrator", "account_status": "Active"})
    print(f"7. Verified obstacle: status={ver_res.get('status')}")
    assert ver_res.get("status") == "Verified"

    # Check edge is blocked
    edge_data = jain_map.graph.get_edge_data("FET_G_ENTRANCE_FOYER", "FET_0F_STAIRS_SOUTH")
    print(f"8. Blocked edge status: is_blocked={edge_data.get('is_blocked')}, status={edge_data.get('status')}")
    assert edge_data.get("is_blocked") is True or edge_data.get("status") == "blocked"

    # Resolve obstacle
    res_res = obs.resolve_report(rep_id, resolution_notes="Cleaned by facilities staff", actor_user={"username": "admin_demo", "role": "Administrator", "account_status": "Active"})
    print(f"9. Resolved obstacle: status={res_res.get('status')}")
    assert res_res.get("status") == "Resolved"
    edge_data_restored = jain_map.graph.get_edge_data("FET_G_ENTRANCE_FOYER", "FET_0F_STAIRS_SOUTH")
    print(f"10. Restored edge status: is_blocked={edge_data_restored.get('is_blocked')}")
    assert not edge_data_restored.get("is_blocked", False)

    # Clean up test row from DB
    with db.get_connection() as conn:
        conn.execute("DELETE FROM obstacle_reports WHERE report_id = ?", (rep_id,))
        conn.commit()

    # 5. 3D Scene Payload Serialization
    payload = build_3d_scene_payload(jain_map, start_id=src, dest_id=dst, algorithm="dijkstra")
    print(f"11. 3D scene payload: {len(payload['locations'])} locations, {len(payload['pathways'])} pathways, active route: {bool(payload.get('active_route'))}")
    assert len(payload["locations"]) == 79
    assert len(payload["pathways"]) == 106

    print("--- ALL REHEARSAL VERIFICATION CHECKS PASSED PERFECTLY ---")

if __name__ == "__main__":
    run_rehearsal()
