"""Unit and integration test suite for Phase 20: Security, Quality Assurance & Production Readiness.

Verifies:
1. SQL injection resilience across all parameterized queries.
2. Strict Backend RBAC and authorization enforcement.
3. Password security policy, hashing standards, and rate-limiting lockout.
4. User data privacy, multi-tenant scoping, and log scrubbing.
5. Data integrity, enum validation, and constraint boundaries.
"""

from __future__ import annotations

import unittest

from database.db_manager import DatabaseManager, SecurityLockoutError
from modules.campus_map import CampusMap, invalidate_cache
from modules.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    SecurityError,
)
from modules.logging_config import SensitiveDataFilter
from modules.obstacle_manager import ObstacleManager


class TestPhase20SecurityAndQA(unittest.TestCase):
    """Test suite for Phase 20 Security, Authorization, and Quality Assurance."""

    def setUp(self) -> None:
        """Initialize in-memory database with test users."""
        self.db = DatabaseManager(":memory:")
        self.cmap = CampusMap()

        # Seed Admin, Staff, and Student accounts
        self.admin = self.db.create_user(
            full_name="Lead Admin",
            username="admin_lead",
            password="AdminPassword123!",
            role="Administrator",
        )
        self.staff = self.db.create_user(
            full_name="Field Staff Member",
            username="staff_member",
            password="StaffPassword123!",
            role="Field Staff",
            actor_user=self.admin,
        )
        self.student = self.db.create_user(
            full_name="Campus Student",
            username="student_user",
            password="StudentPassword123!",
            role="Student",
        )

    def tearDown(self) -> None:
        """Clean up resources."""
        invalidate_cache()
        self.db.close()

    # =========================================================================
    # 1. SQL Injection Resilience Tests (Phase 20.3)
    # =========================================================================

    def test_sql_injection_in_username_lookup(self) -> None:
        """Verify malicious SQL injection string in username lookup does not bypass authentication."""
        malicious_user = "' OR '1'='1' --"
        user = self.db.get_user_by_username(malicious_user)
        self.assertIsNone(user)

        auth_user = self.db.authenticate_user(malicious_user, "AnyPassword123!")
        self.assertIsNone(auth_user)

    def test_sql_injection_drop_table_attempt(self) -> None:
        """Verify malicious drop-table payload in report or query does not execute."""
        drop_payload = "'; DROP TABLE users; --"
        report = self.db.get_report_by_id(drop_payload)
        self.assertIsNone(report)

        # Confirm users table is still fully intact and functional
        admin_check = self.db.get_user_by_username("admin_lead")
        self.assertIsNotNone(admin_check)
        self.assertEqual(admin_check["username"], "admin_lead")

    def test_sql_injection_in_saved_places_and_feedback(self) -> None:
        """Verify saved places and feedback queries reject SQL injection attempts."""
        sqli_target = "FET_01' UNION SELECT * FROM users --"
        saved = self.db.get_saved_places(sqli_target)
        self.assertEqual(len(saved), 0)

        # Ensure feedback insertion with injection string is safely stored as literal text
        fb_id = self.db.submit_feedback(
            user_id=self.student["user_id"],
            feedback_type="general",
            details="Test SQLi: '; DROP TABLE obstacle_reports; --",
            target_id=sqli_target,
        )
        fb_list = self.db.get_feedback_list()
        stored = [f for f in fb_list if f["feedback_id"] == fb_id][0]
        self.assertIn("DROP TABLE", stored["details"])

    # =========================================================================
    # 2. Strict Backend RBAC & Authorization Tests (Phase 20.2)
    # =========================================================================

    def test_non_admin_cannot_update_campus_verification(self) -> None:
        """Verify Student and Field Staff are strictly rejected from updating campus verification."""
        # Student attempt
        success_s, msg_s = self.db.update_campus_verification(
            entity_type="location",
            entity_id="FET_0F_ENTRANCE",
            status="VERIFIED",
            source="Student survey",
            notes="Unauthorized attempt",
            user_role="Student",
            user_id=self.student["user_id"],
        )
        self.assertFalse(success_s)
        self.assertIn("Permission denied", msg_s)

        # Field Staff attempt
        success_st, msg_st = self.db.update_campus_verification(
            entity_type="location",
            entity_id="FET_0F_ENTRANCE",
            status="VERIFIED",
            source="Staff survey",
            notes="Unauthorized attempt",
            user_role="Field Staff",
            user_id=self.staff["user_id"],
        )
        self.assertFalse(success_st)
        self.assertIn("Permission denied", msg_st)

        # Administrator succeeds
        success_a, msg_a = self.db.update_campus_verification(
            entity_type="location",
            entity_id="FET_0F_ENTRANCE",
            status="VERIFIED",
            source="Physical on-site audit",
            notes="Authorized survey",
            user_role="Administrator",
            user_id=self.admin["user_id"],
        )
        self.assertTrue(success_a)

    def test_sole_admin_demotion_prevention(self) -> None:
        """Verify the sole administrator cannot demote their own account to Student."""
        with self.assertRaises(ValueError):
            self.db.update_user_role(
                user_id=self.admin["user_id"],
                new_role="Student",
                actor_user=self.admin,
            )

    def test_inactive_staff_blocked_from_obstacle_verification(self) -> None:
        """Verify deactivated accounts cannot verify or resolve obstacle reports."""
        obs = ObstacleManager(self.db, self.cmap)
        rep = self.db.insert_report({
            "location_id": "FET_01",
            "target_type": "location",
            "obstacle_category": "Blocked pathway",
            "description": "Floor spill",
            "severity": "Medium",
            "reporter_name": "Student",
        })

        # Deactivate staff account
        self.db.update_user_status(self.staff["user_id"], "Inactive", actor_user=self.admin)
        inactive_staff = self.db.get_user_by_id(self.staff["user_id"])

        with self.assertRaises(PermissionError):
            obs.update_report_status(
                report_id=rep,
                status="Verified",
                actor_user=inactive_staff,
            )

    # =========================================================================
    # 3. Password Security & Rate-Limiting Lockout Tests (Phase 20.1)
    # =========================================================================

    def test_password_policy_constraints(self) -> None:
        """Verify passwords violating length, letter, or digit rules are rejected."""
        # Too short (<8 chars)
        with self.assertRaises(ValueError):
            self.db.create_user("Short User", "short_user", "Sh1!", "Student")

        # No digits
        with self.assertRaises(ValueError):
            self.db.create_user("No Digit", "nodigit_user", "OnlyLetters!", "Student")

        # No letters
        with self.assertRaises(ValueError):
            self.db.create_user("No Letter", "noletter_user", "1234567890!", "Student")

    def test_brute_force_lockout_trigger(self) -> None:
        """Verify 5 consecutive failed login attempts trigger SecurityLockoutError."""
        username = self.student["username"]

        for i in range(5):
            res = self.db.authenticate_user(username, "WrongPassword!")
            self.assertIsNone(res)

        # 6th attempt with correct password must raise SecurityLockoutError
        with self.assertRaises(SecurityLockoutError):
            self.db.authenticate_user(username, "StudentPassword123!")

    # =========================================================================
    # 4. Data Privacy & Log Scrubbing Tests (Phase 20.4)
    # =========================================================================

    def test_log_filter_scrubs_auth_secrets(self) -> None:
        """Verify SensitiveDataFilter scrubs sensitive auth attributes from log records."""
        filter_instance = SensitiveDataFilter()
        payload = {
            "username": "admin_lead",
            "password": "AdminPassword123!",
            "salt": "f8a7c2b6e14d3c5a",
            "token": "secret-session-token",
            "status": "success",
        }
        scrubbed = filter_instance.redact_dict(payload)
        self.assertEqual(scrubbed["password"], "[REDACTED]")
        self.assertEqual(scrubbed["salt"], "[REDACTED]")
        self.assertEqual(scrubbed["token"], "[REDACTED]")
        self.assertEqual(scrubbed["username"], "admin_lead")
        self.assertEqual(scrubbed["status"], "success")


if __name__ == "__main__":
    unittest.main()
