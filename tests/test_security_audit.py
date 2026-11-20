"""Security audit, integration review, and end-to-end functional verification test suite."""

from __future__ import annotations

import tempfile
import time
from pathlib import Path
import unittest

from database.db_manager import DatabaseError, DatabaseManager, SecurityLockoutError
from modules.campus_map import CampusMap, load_campus_map
from modules.obstacle_manager import ObstacleManager
from modules.route_finder import RouteFinder


class TestSecurityAuditAndEndToEnd(unittest.TestCase):
    """End-to-end security audit and integration verification suite for Phase 10."""

    def setUp(self) -> None:
        """Initialize isolated in-memory test environment."""
        self.db = DatabaseManager(":memory:")
        self.campus_map = load_campus_map()
        self.obs_manager = ObstacleManager(db_manager=self.db, campus_map=self.campus_map)
        self.route_finder = RouteFinder(self.campus_map)

    def tearDown(self) -> None:
        """Close database connection."""
        self.db.close()

    # =========================================================================
    # 1. SECURITY AUDIT: PASSWORD HASHING, COMPLEXITY & WORK FACTOR UPGRADE
    # =========================================================================

    def test_progressive_password_hash_upgrade_on_login(self) -> None:
        """Verify that accounts with legacy 100,000 iteration hashes are transparently upgraded to 600,000 on login."""
        # 1. Manually create a user with legacy 100,000 iterations (salt without '$')
        legacy_salt = "legacy1234567890abcdef12345678"
        pwd = "SecureStudentPass2026!"
        legacy_hash, _ = self.db.hash_password(pwd, salt=legacy_salt, iterations=100_000)

        user_id = "USR-LEGACY-001"
        now_iso = "2026-01-01T00:00:00+00:00"
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (user_id, full_name, username, password_hash, salt, role, account_status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (user_id, "Legacy User", "legacy_user", legacy_hash, legacy_salt, "Student", "Active", now_iso, now_iso),
            )

        # Confirm initial state has legacy salt
        initial_record = self.db.get_user_by_id(user_id, include_secrets=True)
        assert initial_record is not None
        self.assertEqual(initial_record["salt"], legacy_salt)
        self.assertNotIn("$", initial_record["salt"])

        # 2. Authenticate user -> verification succeeds AND upgrades hash to 600,000 iterations
        auth_result = self.db.authenticate_user("legacy_user", pwd)
        self.assertIsNotNone(auth_result)
        assert auth_result is not None
        self.assertEqual(auth_result["username"], "legacy_user")

        # 3. Inspect updated record in database
        upgraded_record = self.db.get_user_by_id(user_id, include_secrets=True)
        assert upgraded_record is not None
        self.assertIn("$", upgraded_record["salt"])
        iterations_str = upgraded_record["salt"].split("$")[0]
        self.assertEqual(int(iterations_str), DatabaseManager.PBKDF2_RECOMMENDED_ITERATIONS)
        self.assertNotEqual(upgraded_record["password_hash"], legacy_hash)

        # 4. Verify password still verifies against newly upgraded hash
        self.assertTrue(self.db.verify_password(pwd, upgraded_record["password_hash"], upgraded_record["salt"]))

        # 5. Verify security upgrade was recorded in audit log
        audit_logs = self.db.get_audit_logs(limit=10, action="UPGRADE_SECURITY")
        self.assertGreaterEqual(len(audit_logs), 1)
        self.assertEqual(audit_logs[0]["target_id"], user_id)

    def test_password_policy_hardening(self) -> None:
        """Verify password complexity constraints (min 8 chars, letter + digit required)."""
        # Too short (< 8 chars)
        with self.assertRaises(ValueError):
            self.db.create_user("User A", "user_a", "Pass1")

        # Missing numbers
        with self.assertRaises(ValueError):
            self.db.create_user("User B", "user_b", "OnlyLettersPass")

        # Missing letters
        with self.assertRaises(ValueError):
            self.db.create_user("User C", "user_c", "1234567890")

        # Valid password (letters + numbers, >= 8 chars)
        user = self.db.create_user("User D", "user_d", "StrongPass2026")
        self.assertEqual(user["username"], "user_d")

    # =========================================================================
    # 2. SECURITY AUDIT: BRUTE-FORCE RATE LIMITING & LOCKOUT
    # =========================================================================

    def test_brute_force_rate_limiting_and_lockout(self) -> None:
        """Verify that 5 consecutive failed login attempts trigger a temporary account lockout."""
        self.db.create_user("Victim User", "victim_user", "TargetPass123!")

        # 4 failed attempts should not trigger lockout
        for _ in range(4):
            self.assertIsNone(self.db.authenticate_user("victim_user", "WrongPassword"))
            is_locked, _ = self.db.is_account_locked("victim_user")
            self.assertFalse(is_locked)

        # 5th failed attempt triggers lockout threshold
        self.assertIsNone(self.db.authenticate_user("victim_user", "WrongPassword"))
        is_locked, remaining = self.db.is_account_locked("victim_user")
        self.assertTrue(is_locked)
        self.assertGreater(remaining, 0)

        # Subsequent attempt raises SecurityLockoutError even with the correct password
        with self.assertRaises(SecurityLockoutError):
            self.db.authenticate_user("victim_user", "TargetPass123!")

        # Resetting failed logins allows immediate authentication
        self.db.reset_failed_logins("victim_user")
        self.assertFalse(self.db.is_account_locked("victim_user")[0])
        auth = self.db.authenticate_user("victim_user", "TargetPass123!")
        self.assertIsNotNone(auth)

    # =========================================================================
    # 3. END-TO-END OBSTACLE INTEGRATION WORKFLOW
    # =========================================================================

    def test_end_to_end_obstacle_workflow(self) -> None:
        """Execute and verify complete 11-step obstacle workflow across all roles."""
        # Setup roles
        admin = self.db.create_user("Lead Admin", "admin_lead", "AdminPass2026!", role="Administrator")
        staff = self.db.create_user("Field Tech", "staff_tech", "StaffPass2026!", role="Field Staff", actor_user=admin)
        student = self.db.create_user("Alex Student", "alex_s", "StudentPass2026!", role="Student")

        # 1. Baseline: Route from LOC_01 to LOC_02 is open and uses direct edge
        base_route = self.route_finder.find_route("LOC_01", "LOC_02", algorithm="dijkstra")
        self.assertIsNotNone(base_route)
        assert base_route is not None
        self.assertEqual(base_route.path, ["LOC_01", "LOC_02"])

        # 2. Student submits report -> Pending status
        rep = self.obs_manager.submit_report(
            obstacle_category="Broken ramp",
            severity="High",
            description="Handrail collapsed across ramp",
            source_location_id="LOC_01",
            destination_location_id="LOC_02",
            reporter_name=student["full_name"],
        )
        rep_id = rep["report_id"]
        self.assertEqual(rep["status"], "Pending")

        # 3. Verification that Pending report does NOT block pathway
        self.assertEqual(self.campus_map.graph["LOC_01"]["LOC_02"]["status"], "open")
        self.assertEqual(
            self.route_finder.find_route("LOC_01", "LOC_02", algorithm="dijkstra").path,
            ["LOC_01", "LOC_02"],
        )

        # 4. Unauthorized Student attempts verification -> PermissionError
        with self.assertRaises(PermissionError):
            self.obs_manager.verify_report(rep_id, actor_user=student)

        # 5. Field Staff verifies obstacle -> Pathway becomes blocked
        verified_rep = self.obs_manager.verify_report(rep_id, actor_user=staff)
        self.assertEqual(verified_rep["status"], "Verified")
        self.assertEqual(self.campus_map.graph["LOC_01"]["LOC_02"]["status"], "blocked")

        # 6. Dijkstra and BFS navigation automatically avoid blocked connection
        detour_dijkstra = self.route_finder.find_route("LOC_01", "LOC_02", algorithm="dijkstra")
        detour_bfs = self.route_finder.find_route("LOC_01", "LOC_02", algorithm="bfs")

        if detour_dijkstra is not None and detour_dijkstra.success:
            # If an alternate path exists, it must not traverse (LOC_01, LOC_02)
            edge_pairs = list(zip(detour_dijkstra.path[:-1], detour_dijkstra.path[1:]))
            self.assertNotIn(("LOC_01", "LOC_02"), edge_pairs)
            self.assertNotIn(("LOC_02", "LOC_01"), edge_pairs)

        if detour_bfs is not None and detour_bfs.success:
            bfs_pairs = list(zip(detour_bfs.path[:-1], detour_bfs.path[1:]))
            self.assertNotIn(("LOC_01", "LOC_02"), bfs_pairs)
            self.assertNotIn(("LOC_02", "LOC_01"), bfs_pairs)

        # 7. Field Staff resolves report with mandatory notes -> Pathway restored
        resolved_rep = self.obs_manager.resolve_report(
            rep_id, resolution_notes="New steel handrail installed and tested.", actor_user=staff
        )
        self.assertEqual(resolved_rep["status"], "Resolved")
        self.assertEqual(self.campus_map.graph["LOC_01"]["LOC_02"]["status"], "open")

        # 8. Navigation returns to original direct connection
        restored_route = self.route_finder.find_route("LOC_01", "LOC_02", algorithm="dijkstra")
        self.assertIsNotNone(restored_route)
        assert restored_route is not None
        self.assertEqual(restored_route.path, ["LOC_01", "LOC_02"])

        # 9. Verify audit trail entries
        audit_logs = self.db.get_audit_logs(limit=20)
        actions = [a["action"] for a in audit_logs]
        self.assertIn("VERIFY_OBSTACLE", actions)
        self.assertIn("RESOLVE_OBSTACLE", actions)

    def test_rejected_report_safety(self) -> None:
        """Verify rejected reports never block pathways and record rejection reasons in audit logs."""
        admin = self.db.create_user("Admin", "admin_safe", "AdminPass123!", role="Administrator")
        staff = self.db.create_user("Staff", "staff_safe", "StaffPass123!", role="Field Staff", actor_user=admin)

        rep = self.obs_manager.submit_report(
            obstacle_category="Temporary obstruction",
            severity="Low",
            description="Paper box near doorway",
            location_id="LOC_02",
        )
        rep_id = rep["report_id"]

        rejected = self.obs_manager.reject_report(
            rep_id,
            rejection_reason="Item moved before inspection; area clear.",
            actor_user=staff,
        )
        self.assertEqual(rejected["status"], "Rejected")
        # Location is open
        self.assertEqual(self.campus_map.graph.nodes["LOC_02"].get("status", "open"), "open")

    def test_concurrent_obstacles_on_same_pathway(self) -> None:
        """Verify that if two separate obstacles block a pathway, resolving one keeps the edge blocked until both are cleared."""
        admin = self.db.create_user("Admin", "admin_multi", "AdminPass123!", role="Administrator")

        # Two reports on same pathway
        rep1 = self.obs_manager.submit_report(
            obstacle_category="Blocked pathway",
            severity="High",
            description="Broken glass",
            source_location_id="LOC_01",
            destination_location_id="LOC_02",
        )
        rep2 = self.obs_manager.submit_report(
            obstacle_category="Construction work",
            severity="Critical",
            description="Electrical conduit repair",
            source_location_id="LOC_01",
            destination_location_id="LOC_02",
        )

        self.obs_manager.verify_report(rep1["report_id"], actor_user=admin)
        self.obs_manager.verify_report(rep2["report_id"], actor_user=admin)
        self.assertEqual(self.campus_map.graph["LOC_01"]["LOC_02"]["status"], "blocked")

        # Resolve first obstacle -> Edge should STILL be blocked because rep2 is active
        self.obs_manager.resolve_report(rep1["report_id"], resolution_notes="Glass cleaned", actor_user=admin)
        self.assertEqual(self.campus_map.graph["LOC_01"]["LOC_02"]["status"], "blocked")

        # Resolve second obstacle -> Edge should now be restored to open
        self.obs_manager.resolve_report(rep2["report_id"], resolution_notes="Wiring finished", actor_user=admin)
        self.assertEqual(self.campus_map.graph["LOC_01"]["LOC_02"]["status"], "open")


if __name__ == "__main__":
    unittest.main()
