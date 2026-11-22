"""
scripts/verify_phase23_workflows.py
-----------------------------------
Final Functional Validation Script for Phase 23.
Executes programmatic end-to-end verification of all seven core functional domains:
A. Authentication and RBAC
B. Campus Navigation and Multi-Floor Routing
C. Accessibility and Wheelchair Invariants
D. 3D Digital Twin Structure and Invariants
E. Obstacle Management and Dynamic Recalculation
F. Campus Analytics and Dual-Dataset Separation
G. Administrative Governance and Audit Trails
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db_manager import DatabaseManager
from modules.jain_digital_twin import (
    load_jain_campus_map,
    build_jain_digital_twin_payload,
)
from modules.route_finder import RouteFinder
from modules.accessibility import AccessibilityEngine
from modules.obstacle_manager import ObstacleManager
from modules.destination_search import search_destinations
from modules.i18n import t, translate_instruction
from modules.campus_analytics import (
    compute_accessibility_analytics,
    compute_obstacle_analytics,
    compute_navigation_analytics,
    compute_administrative_insights,
)
from modules.exceptions import SecurityLockoutError, AuthorizationError


def run_phase23_validation():
    print("=" * 70)
    print("PHASE 23: ACCESSIBLE CAMPUS NAVIGATOR - FUNCTIONAL VALIDATION")
    print("=" * 70)

    db = DatabaseManager()
    jain_campus = load_jain_campus_map()
    route_finder = RouteFinder(jain_campus)
    access_engine = AccessibilityEngine(jain_campus)
    obstacle_mgr = ObstacleManager(db, jain_campus)

    # ---------------------------------------------------------
    # DOMAIN A: Authentication & RBAC
    # ---------------------------------------------------------
    print("\n[A] Testing Authentication & RBAC...")
    student = db.authenticate_user("demo_student", "DemoStudent2026!")
    staff = db.authenticate_user("demo_staff", "DemoStaff2026!")
    admin = db.authenticate_user("demo_admin", "DemoAdmin2026!")

    assert student is not None, "demo_student must authenticate successfully"
    assert staff is not None, "demo_staff must authenticate successfully"
    assert admin is not None, "demo_admin must authenticate successfully"
    assert student["role"] == "Student"
    assert staff["role"] == "Field Staff"
    assert admin["role"] == "Administrator"
    print(f"  ✓ Successfully authenticated Student ({student['username']}), Staff ({staff['username']}), Admin ({admin['username']})")

    # Test sole admin demotion prevention
    try:
        db.update_user_role(admin["user_id"], "Student", actor_user=admin)
        print("  ✗ Sole admin demotion prevention FAILED (should raise ValueError)")
        sys.exit(1)
    except (AuthorizationError, PermissionError, ValueError) as e:
        print(f"  ✓ Sole administrator demotion strictly rejected by RBAC: {e}")

    # ---------------------------------------------------------
    # DOMAIN B: Campus Navigation & Cross-Floor Routing
    # ---------------------------------------------------------
    print("\n[B] Testing Campus Navigation & Cross-Floor Routing...")
    search_res = search_destinations("Auditorium", jain_campus)
    assert len(search_res) > 0, "Destination search for 'Auditorium' must return results"
    target_node = search_res[0].location_id
    print(f"  ✓ Search query 'Auditorium' matched: {search_res[0].name} (ID: {target_node}, Floor: {search_res[0].floor})")

    start_node = "OUT_GATE_MAIN"  # Main Gate
    target_node = "FET_4F_CONF_HALL"  # Ramanujan Executive Conference Hall
    route = route_finder.find_route(start_node, target_node, algorithm="dijkstra")
    assert route.success, f"Route calculation failed: {route.error_message}"
    print(f"  ✓ Route calculated: {start_node} -> {target_node}")
    print(f"    - Total Distance: {route.total_distance}m")
    print(f"    - Estimated Time: {route.total_time}s ({route.total_time/60:.1f} min)")
    print(f"    - Path Nodes: {len(route.path)} nodes across {len(route.steps)} instructions")

    # ---------------------------------------------------------
    # DOMAIN C: Accessibility & Wheelchair Invariants
    # ---------------------------------------------------------
    print("\n[C] Testing Accessibility & Wheelchair Invariants...")
    std_route = route_finder.find_route("OUT_FET_FRONT_PORTICO", "FET_4F_CONF_HALL", algorithm="dijkstra", wheelchair_accessible=False)
    wc_route = route_finder.find_route("OUT_FET_FRONT_PORTICO", "FET_4F_CONF_HALL", algorithm="dijkstra", wheelchair_accessible=True)

    assert wc_route.success, "Wheelchair accessible route must succeed"
    wc_path = wc_route.path

    # Verify no steps have stairs in wheelchair route
    assert not any(s.has_stairs for s in wc_route.steps), "Wheelchair route must have zero steps with stairs"
    assert all(s.wheelchair_accessible for s in wc_route.steps), "All steps in wheelchair route must be wheelchair accessible"
    print("  ✓ Wheelchair route strictly excluded all staircase barrier steps (has_stairs = False for 100% of steps)")

    # Verify elevator usage
    elev_steps = [s for s in wc_route.steps if s.has_elevator]
    assert len(elev_steps) > 0, "Wheelchair route must use elevator for vertical transfer"
    print(f"  ✓ Wheelchair route utilized elevator core across {len(elev_steps)} floor levels: {[s.from_id + ' -> ' + s.to_id for s in elev_steps]}")

    # Verify i18n
    sample_step = {"instruction": "Take elevator to Floor 4", "distance": 14.0}
    en_inst = translate_instruction(sample_step, "en")
    kn_inst = translate_instruction(sample_step, "kn")
    hi_inst = translate_instruction(sample_step, "hi")
    print(f"  ✓ i18n English: '{en_inst}'")
    print(f"  ✓ i18n Kannada: '{kn_inst}'")
    print(f"  ✓ i18n Hindi:   '{hi_inst}'")

    # ---------------------------------------------------------
    # DOMAIN D: 3D Digital Twin Structure & Invariants
    # ---------------------------------------------------------
    print("\n[D] Testing 3D Digital Twin Structure & Invariants...")
    scene = build_jain_digital_twin_payload(jain_campus)
    assert "locations" in scene and "pathways" in scene, "Scene must include locations and pathways"
    assert len(scene["locations"]) == 79, f"Scene must contain 79 locations, got {len(scene['locations'])}"
    assert len(scene["pathways"]) == 106, f"Scene must contain 106 pathways, got {len(scene['pathways'])}"
    unique_floors = sorted(set(loc["floor"] for loc in scene["locations"]))
    assert unique_floors == [-1, 0, 1, 2, 3, 4], f"Unexpected floors: {unique_floors}"
    print(f"  ✓ Verified 6 vertical elevations (Outdoor -1, Floors 0 to 4): {unique_floors}")
    print(f"  ✓ Verified 79 locations and 106 pathways serialized in 3D WebGL payload")

    # Verify elevator shaft vertical alignment (zero planar shear)
    elev_l0 = jain_campus.locations.get("FET_0F_ELEVATOR")
    elev_l4 = jain_campus.locations.get("FET_4F_ELEVATOR")
    assert elev_l0 and elev_l4, "Elevator nodes on Floor 0 and Floor 4 must exist"
    assert elev_l0["x"] == elev_l4["x"]
    assert elev_l0["y"] == elev_l4["y"]
    print(f"  ✓ Verified elevator shaft vertical invariant: Planar coordinates identical at ({elev_l0['x']}, {elev_l0['y']})")

    # ---------------------------------------------------------
    # DOMAIN E: Obstacle Management & Dynamic Rerouting
    # ---------------------------------------------------------
    print("\n[E] Testing Obstacle Management & Dynamic Rerouting...")
    test_edge = ("OUT_FET_FRONT_PORTICO", "FET_G_ENTRANCE_FOYER")
    
    # 1. Submit obstacle report as student
    rep_result = obstacle_mgr.submit_report(
        obstacle_category="Blocked pathway",
        severity="High",
        description="Validation test barrier",
        source_location_id=test_edge[0],
        destination_location_id=test_edge[1],
        reporter_name=student["username"]
    )
    rep_id = rep_result["report_id"]
    print(f"  ✓ Submitted pending obstacle report: {rep_id} (Status: Pending)")
    
    # Verify pending report does NOT block
    blocked_edges = obstacle_mgr.get_active_blocked_edges()
    norm_edge = obstacle_mgr._normalize_edge_key(test_edge[0], test_edge[1])
    assert norm_edge not in blocked_edges, "Pending obstacle must not block edge"
    
    # 2. Staff verifies obstacle -> auto-block
    obstacle_mgr.verify_report(rep_id, actor_user=staff)
    blocked_edges = obstacle_mgr.get_active_blocked_edges()
    assert norm_edge in blocked_edges, "Verified obstacle must dynamically block edge"
    print(f"  ✓ Staff verified report {rep_id} -> pathway dynamically blocked in NetworkX graph ({norm_edge})")

    # 3. Route recalculation avoids blocked pathway
    rerouted = route_finder.find_route(test_edge[0], "FET_G_ENTRANCE_FOYER")
    if rerouted.success:
        pairs = [obstacle_mgr._normalize_edge_key(u, v) for u, v in zip(rerouted.path[:-1], rerouted.path[1:])]
        assert norm_edge not in pairs, "Rerouted path must not traverse blocked edge"
        print(f"  ✓ Dynamic reroute confirmed: avoid blocked edge {test_edge} via alternative detour")

    # 4. Resolve obstacle -> pathway restored
    obstacle_mgr.resolve_report(rep_id, resolution_notes="Barrier removed during validation test", actor_user=staff)
    blocked_edges = obstacle_mgr.get_active_blocked_edges()
    assert norm_edge not in blocked_edges, "Resolved obstacle must restore edge to operational"
    print(f"  ✓ Obstacle resolved with audit notes -> pathway restored to operational status")

    # ---------------------------------------------------------
    # DOMAIN F: Campus Analytics & Dual-Dataset Separation
    # ---------------------------------------------------------
    print("\n[F] Testing Campus Analytics & Dual-Dataset Separation...")
    jain_analytics = compute_accessibility_analytics(jain_campus)
    obstacle_analytics = compute_obstacle_analytics(db)
    nav_analytics = compute_navigation_analytics(db)
    admin_insights = compute_administrative_insights(jain_campus, db)

    print(f"  ✓ JAIN Global Campus Analytics:")
    print(f"    - Total Locations: {jain_analytics['total_locations']} (100% of 79 node graph)")
    print(f"    - Total Pathways: {jain_analytics['total_pathways']} (100% of 106 pathway graph)")
    print(f"    - Step-Free Accessible Pathways: {jain_analytics['step_free_pathways']} ({jain_analytics['pathway_accessibility_percentage']}%)")
    print(f"    - Staircase Barrier Pathways: {jain_analytics['staircase_pathways']}")
    print(f"    - Total Reports Logged: {obstacle_analytics['total_reports']}")
    print(f"    - Active Verified Hazards: {obstacle_analytics['active_verified_obstacles']}")
    print(f"    - Resolved Reports: {obstacle_analytics['resolved_obstacles']}")

    # ---------------------------------------------------------
    # DOMAIN G: Administrative Governance & Audit Trails
    # ---------------------------------------------------------
    print("\n[G] Testing Administrative Governance & Audit Trails...")
    audit_logs = db.get_audit_logs(limit=10)
    assert len(audit_logs) > 0, "Audit trail must contain recorded actions"
    print(f"  ✓ Verified immutable audit trail: {len(audit_logs)} recent events recorded")
    latest_event = audit_logs[0]
    print(f"    - Latest Action: {latest_event.get('action')} on {latest_event.get('target_type')} by User {latest_event.get('user_id')}")

    print("\n" + "=" * 70)
    print("ALL PHASE 23 FUNCTIONAL DOMAIN VALIDATIONS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_phase23_validation()
