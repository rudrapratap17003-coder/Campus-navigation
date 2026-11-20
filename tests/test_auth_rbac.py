"""Comprehensive unit test suite for user authentication, role-based access control, and administrative management."""

from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

import networkx as nx

from database.db_manager import DatabaseError, DatabaseManager
from modules.campus_map import CampusMap, load_campus_map
from modules.obstacle_manager import ObstacleManager


class TestAuthenticationAndRBAC(unittest.TestCase):
    """Test suite verifying PBKDF2 authentication, RBAC enforcement, audit logging, and schema migration."""

    def setUp(self) -> None:
        """Create isolated in-memory database and test campus graph for each test."""
        self.db = DatabaseManager(":memory:")
        self.campus_map = load_campus_map()
        self.obs_manager = ObstacleManager(db_manager=self.db, campus_map=self.campus_map)

    def tearDown(self) -> None:
        """Clean up in-memory database."""
        self.db.close()

    # =========================================================================
    # 1. PASSWORD HASHING AND VERIFICATION
    # =========================================================================

    def test_password_hashing_and_salting(self) -> None:
        """Verify PBKDF2-HMAC-SHA256 password hashing generates salted non-plaintext hashes."""
        pwd = "SecretPassword123!"
        hash1, salt1 = self.db.hash_password(pwd)
        hash2, salt2 = self.db.hash_password(pwd)

        # Unique salts per generation
        self.assertNotEqual(salt1, salt2)
        # Unique hashes due to salting
        self.assertNotEqual(hash1, hash2)
        # Plaintext password is never in the hash or salt
        self.assertNotIn(pwd, hash1)
        self.assertNotIn(pwd, salt1)

        # Verification
        self.assertTrue(self.db.verify_password(pwd, hash1, salt1))
        self.assertTrue(self.db.verify_password(pwd, hash2, salt2))
        self.assertFalse(self.db.verify_password("WrongPassword", hash1, salt1))
        self.assertFalse(self.db.verify_password("", hash1, salt1))

    # =========================================================================
    # 2. USER REGISTRATION & INITIAL BOOTSTRAP
    # =========================================================================

    def test_initial_administrator_bootstrap(self) -> None:
        """Verify the first administrator account can be created when no admin exists."""
        self.assertFalse(self.db.has_admin_user())
        admin = self.db.create_user(
            full_name="Lead Admin",
            username="admin_lead",
            password="MasterPassword2026!",
            role="Administrator",
        )
        self.assertEqual(admin["username"], "admin_lead")
        self.assertEqual(admin["role"], "Administrator")
        self.assertTrue(self.db.has_admin_user())

        # Plaintext secrets must not be exposed in user dict
        self.assertNotIn("password_hash", admin)
        self.assertNotIn("salt", admin)

    def test_student_self_registration(self) -> None:
        """Verify standard student registration creates active student accounts."""
        student = self.db.create_user(
            full_name="Jane Doe",
            username="jane_doe",
            password="StudentPass123",
            role="Student",
        )
        self.assertEqual(student["role"], "Student")
        self.assertEqual(student["account_status"], "Active")

        # Confirm retrieval
        fetched = self.db.get_user_by_username("jane_doe")
        self.assertIsNotNone(fetched)
        assert fetched is not None
        self.assertEqual(fetched["full_name"], "Jane Doe")
        self.assertNotIn("password_hash", fetched)

    def test_unauthorized_role_self_elevation_blocked(self) -> None:
        """Verify an ordinary user cannot register as Field Staff or Administrator once an admin exists."""
        # Create initial admin
        self.db.create_user(
            full_name="System Admin",
            username="sys_admin",
            password="AdminPassword123",
            role="Administrator",
        )

        # Attempt to create an unauthorized admin without actor_user
        with self.assertRaises(PermissionError):
            self.db.create_user(
                full_name="Malicious Actor",
                username="fake_admin",
                password="AttackerPass123",
                role="Administrator",
            )

        # Attempt to create an unauthorized Field Staff by a student
        student = self.db.create_user(
            full_name="Alice Student",
            username="alice_s",
            password="StudentPass123",
            role="Student",
        )
        with self.assertRaises(PermissionError):
            self.db.create_user(
                full_name="Staff Bob",
                username="bob_staff",
                password="StaffPass123",
                role="Field Staff",
                actor_user=student,
            )

    def test_username_uniqueness_and_validation(self) -> None:
        """Verify case-insensitive username collision prevention and validation constraints."""
        self.db.create_user("User One", "campus_user", "ValidPass123")
        # Duplicate case-insensitive
        with self.assertRaises(ValueError):
            self.db.create_user("User Duplicate", "CAMPUS_USER", "ValidPass123")

        # Invalid username formats
        with self.assertRaises(ValueError):
            self.db.create_user("Short", "ab", "ValidPass123")
        with self.assertRaises(ValueError):
            self.db.create_user("Spaces", "user name", "ValidPass123")
        # Short password
        with self.assertRaises(ValueError):
            self.db.create_user("Weak Pass", "valid_user", "12345")

    # =========================================================================
    # 3. AUTHENTICATION & LOGIN WORKFLOW
    # =========================================================================

    def test_successful_authentication(self) -> None:
        """Verify valid credentials authenticate successfully with case-insensitive username."""
        self.db.create_user("Test User", "test_login", "MySecurePass123")

        auth_user = self.db.authenticate_user("test_login", "MySecurePass123")
        self.assertIsNotNone(auth_user)
        assert auth_user is not None
        self.assertEqual(auth_user["username"], "test_login")

        # Case-insensitive login
        auth_upper = self.db.authenticate_user("TEST_LOGIN", "MySecurePass123")
        self.assertIsNotNone(auth_upper)

    def test_authentication_failures(self) -> None:
        """Verify incorrect password or non-existent usernames return None."""
        self.db.create_user("Test User", "test_user_fail", "RealPassword123")

        # Incorrect password
        self.assertIsNone(self.db.authenticate_user("test_user_fail", "WrongPassword"))
        # Non-existent user
        self.assertIsNone(self.db.authenticate_user("ghost_user", "SomePassword"))

    # =========================================================================
    # 4. RBAC OBSTACLE WORKFLOW ENFORCEMENT
    # =========================================================================

    def test_student_cannot_verify_or_resolve_report(self) -> None:
        """Verify Student users cannot verify, reject, or resolve obstacle reports."""
        student = self.db.create_user("Sam Student", "sam_student", "StudentPass123", role="Student")

        report = self.obs_manager.submit_report(
            obstacle_category="Blocked pathway",
            severity="High",
            description="Fallen tree across path",
            source_location_id="LOC_01",
            destination_location_id="LOC_02",
            reporter_name="Sam Student",
        )
        rep_id = report["report_id"]

        # Student cannot verify
        with self.assertRaises(PermissionError):
            self.obs_manager.verify_report(rep_id, actor_user=student)

        # Student cannot reject
        with self.assertRaises(PermissionError):
            self.obs_manager.reject_report(rep_id, rejection_reason="No issue", actor_user=student)

        # Student cannot resolve
        with self.assertRaises(PermissionError):
            self.obs_manager.resolve_report(rep_id, resolution_notes="Cleaned up", actor_user=student)

    def test_field_staff_and_admin_authorized_workflow(self) -> None:
        """Verify Field Staff and Administrators can verify, block routes, and resolve obstacles."""
        admin = self.db.create_user("Admin User", "admin_ops", "AdminPass123", role="Administrator")
        staff = self.db.create_user(
            "Staff Member", "staff_mike", "StaffPass123", role="Field Staff", actor_user=admin
        )

        report = self.obs_manager.submit_report(
            obstacle_category="Damaged flooring",
            severity="Critical",
            description="Loose tiles causing trip hazard",
            source_location_id="LOC_01",
            destination_location_id="LOC_02",
        )
        rep_id = report["report_id"]

        # 1. Staff verifies report -> Pathway becomes blocked
        updated_rep = self.obs_manager.verify_report(rep_id, actor_user=staff)
        self.assertEqual(updated_rep["status"], "Verified")
        self.assertEqual(self.campus_map.graph["LOC_01"]["LOC_02"]["status"], "blocked")

        # 2. Staff resolves report with mandatory notes -> Pathway restored
        resolved_rep = self.obs_manager.resolve_report(
            rep_id, resolution_notes="Tiles replaced and inspected.", actor_user=staff
        )
        self.assertEqual(resolved_rep["status"], "Resolved")
        self.assertEqual(self.campus_map.graph["LOC_01"]["LOC_02"]["status"], "open")

    def test_resolution_notes_mandatory(self) -> None:
        """Verify resolving an obstacle report requires non-empty resolution notes."""
        admin = self.db.create_user("Admin User", "admin_res", "AdminPass123", role="Administrator")
        rep = self.obs_manager.submit_report(
            obstacle_category="Construction work",
            severity="Medium",
            description="Painting wall",
            location_id="LOC_01",
        )
        self.obs_manager.verify_report(rep["report_id"], actor_user=admin)

        with self.assertRaises(ValueError):
            self.obs_manager.resolve_report(rep["report_id"], resolution_notes="", actor_user=admin)

    def test_inactive_account_restrictions(self) -> None:
        """Verify deactivated staff accounts are blocked from performing modifications."""
        admin = self.db.create_user("Master Admin", "admin_master", "MasterPass123", role="Administrator")
        staff = self.db.create_user(
            "Inactive Staff", "staff_inactive", "StaffPass123", role="Field Staff", actor_user=admin
        )
        # Deactivate staff
        self.db.update_user_status(staff["user_id"], "Inactive", actor_user=admin)
        staff_record = self.db.get_user_by_id(staff["user_id"])
        assert staff_record is not None
        self.assertEqual(staff_record["account_status"], "Inactive")

        report = self.obs_manager.submit_report(
            obstacle_category="Temporary obstruction",
            severity="Low",
            description="Boxes in hallway",
            location_id="LOC_02",
        )

        with self.assertRaises(PermissionError):
            self.obs_manager.verify_report(report["report_id"], actor_user=staff_record)

    # =========================================================================
    # 5. AUDIT LOGGING
    # =========================================================================

    def test_administrative_audit_trail_recorded(self) -> None:
        """Verify administrative actions and obstacle lifecycle transitions write audit logs."""
        admin = self.db.create_user("Auditor Admin", "admin_audit", "AdminPass123", role="Administrator")
        staff = self.db.create_user("Worker", "worker_1", "WorkerPass123", role="Field Staff", actor_user=admin)

        report = self.obs_manager.submit_report(
            obstacle_category="Broken ramp",
            severity="High",
            description="Handrail broken",
            source_location_id="LOC_01",
            destination_location_id="LOC_02",
        )
        self.obs_manager.verify_report(report["report_id"], actor_user=staff)
        self.obs_manager.resolve_report(
            report["report_id"], resolution_notes="Handrail repaired", actor_user=staff
        )

        audit_logs = self.db.get_audit_logs(limit=20)
        self.assertGreaterEqual(len(audit_logs), 4)

        actions = [a["action"] for a in audit_logs]
        self.assertIn("CREATE_USER", actions)
        self.assertIn("VERIFY_OBSTACLE", actions)
        self.assertIn("RESOLVE_OBSTACLE", actions)

    # =========================================================================
    # 6. DUPLICATE DETECTION
    # =========================================================================

    def test_duplicate_detection(self) -> None:
        """Verify duplicate detection identifies existing active/pending reports on the same target."""
        self.obs_manager.submit_report(
            obstacle_category="Blocked pathway",
            severity="Medium",
            description="Spill on path",
            source_location_id="LOC_01",
            destination_location_id="LOC_02",
        )

        # Check duplicates on same pathway (both directions)
        dups_forward = self.obs_manager.detect_potential_duplicates(
            source_location_id="LOC_01", destination_location_id="LOC_02"
        )
        dups_reverse = self.obs_manager.detect_potential_duplicates(
            source_location_id="LOC_02", destination_location_id="LOC_01"
        )
        self.assertEqual(len(dups_forward), 1)
        self.assertEqual(len(dups_reverse), 1)

        # Check different pathway -> no duplicates
        no_dups = self.obs_manager.detect_potential_duplicates(
            source_location_id="LOC_02", destination_location_id="LOC_04"
        )
        self.assertEqual(len(no_dups), 0)

    # =========================================================================
    # 7. SAFE SCHEMA MIGRATION & DATA PRESERVATION
    # =========================================================================

    def test_safe_schema_migration_preserves_existing_data(self) -> None:
        """Verify calling initialize_schema on an existing database preserves reports and data."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_file = Path(tf.name)

        try:
            # 1. Initialize first instance and write a report
            db1 = DatabaseManager(db_file)
            rep_id = db1.insert_report({
                "report_id": "REP-PRESERVE-001",
                "target_type": "location",
                "location_id": "LOC_01",
                "obstacle_category": "Blocked pathway",
                "description": "Preserved test obstacle",
                "severity": "High",
                "reporter_name": "Auditor",
                "status": "Verified",
            })
            admin = db1.create_user("Persist Admin", "persist_admin", "PersistPass123", role="Administrator")
            db1.close()

            # 2. Re-open database with a new DatabaseManager instance (triggers schema initialization)
            db2 = DatabaseManager(db_file)
            fetched_rep = db2.get_report_by_id(rep_id)
            self.assertIsNotNone(fetched_rep)
            assert fetched_rep is not None
            self.assertEqual(fetched_rep["description"], "Preserved test obstacle")

            fetched_admin = db2.get_user_by_username("persist_admin")
            self.assertIsNotNone(fetched_admin)
            assert fetched_admin is not None
            self.assertEqual(fetched_admin["role"], "Administrator")

            stats = db2.get_user_statistics()
            self.assertEqual(stats["total_users"], 1)
            self.assertEqual(stats["active_users"], 1)
            db2.close()

        finally:
            if db_file.exists():
                try:
                    db_file.unlink()
                except OSError:
                    pass


    # =========================================================================
    # 8. ADMINISTRATIVE USER GOVERNANCE & SAFEGUARD TESTS
    # =========================================================================

    def test_report_rejection_workflow(self) -> None:
        """Verify authorized report rejection updates status and does not block graph."""
        admin = self.db.create_user("Admin User", "admin_rej", "AdminPass123", role="Administrator")
        staff = self.db.create_user("Staff Member", "staff_rej", "StaffPass123", role="Field Staff", actor_user=admin)

        report = self.obs_manager.submit_report(
            obstacle_category="Temporary obstruction",
            severity="Low",
            description="Litter in corridor",
            location_id="LOC_02",
        )
        rejected = self.obs_manager.reject_report(
            report["report_id"],
            rejection_reason="Already swept by custodial staff.",
            actor_user=staff,
        )
        self.assertEqual(rejected["status"], "Rejected")
        self.assertEqual(rejected["resolution_notes"], "Already swept by custodial staff.")
        self.assertEqual(self.campus_map.graph.nodes["LOC_02"].get("status", "open"), "open")

    def test_admin_user_role_assignment_and_demotion_prevention(self) -> None:
        """Verify role updates by Administrator and prevention of sole admin demotion."""
        admin1 = self.db.create_user("Admin One", "admin_1", "MasterPass123", role="Administrator")
        student = self.db.create_user("Student Joe", "joe_student", "StudentPass123", role="Student")

        # Admin can promote student to Field Staff
        success = self.db.update_user_role(student["user_id"], "Field Staff", actor_user=admin1)
        self.assertTrue(success)
        updated_student = self.db.get_user_by_id(student["user_id"])
        assert updated_student is not None
        self.assertEqual(updated_student["role"], "Field Staff")

        # Admin cannot demote themselves if they are the only Administrator
        with self.assertRaises(ValueError):
            self.db.update_user_role(admin1["user_id"], "Student", actor_user=admin1)

        # Admin cannot deactivate themselves if they are the only active Administrator
        with self.assertRaises(ValueError):
            self.db.update_user_status(admin1["user_id"], "Inactive", actor_user=admin1)

        # After creating a second Administrator, demoting the first is allowed
        admin2 = self.db.create_user("Admin Two", "admin_2", "MasterPass456", role="Administrator", actor_user=admin1)
        success_demote = self.db.update_user_role(admin1["user_id"], "Field Staff", actor_user=admin2)
        self.assertTrue(success_demote)
        self.assertEqual(self.db.get_user_by_id(admin1["user_id"])["role"], "Field Staff")


if __name__ == "__main__":
    unittest.main()
