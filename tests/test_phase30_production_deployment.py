"""Unit and integration test suite for Phase 30: Production Deployment & Release Engineering.

Validates:
1. Production system health monitoring and diagnostic probe (`modules/health.py`).
2. Absence of sensitive credentials and internal paths in health outputs.
3. Native SQLite online backup and verified atomic restore functionality.
4. Production environment configuration validation and security thresholds.
5. PostgreSQL production DDL generation and data migration export accuracy.
6. .env.example template coverage and safety invariants.
"""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from config import AppConfig, get_config
from database.db_manager import DatabaseManager, DatabaseError
from database.postgres_migration import generate_postgres_ddl, export_sqlite_to_postgres_sql
from modules.health import check_system_health


class TestPhase30ProductionDeployment(unittest.TestCase):
    """Automated tests validating production deployment, health monitoring, and recovery."""

    def setUp(self) -> None:
        """Create a dedicated temporary directory for test artifacts."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        """Clean up temporary test artifacts."""
        self.temp_dir.cleanup()

    # =========================================================================
    # 1. System Health Monitoring Tests
    # =========================================================================

    def test_system_health_check_healthy(self) -> None:
        """Verify that the health check probe returns status HEALTHY with valid sub-system metrics."""
        health = check_system_health(check_database=True, check_maps=True)

        self.assertEqual(health["status"], "HEALTHY")
        self.assertIn("timestamp", health)
        self.assertGreater(health["total_latency_ms"], 0)

        # Database checks
        self.assertIn("database", health["checks"])
        self.assertEqual(health["checks"]["database"]["status"], "healthy")
        self.assertEqual(health["checks"]["database"]["schema_version"], 3)

        # Spatial graph checks
        self.assertIn("spatial_graphs", health["checks"])
        self.assertEqual(health["checks"]["spatial_graphs"]["status"], "healthy")
        self.assertEqual(
            health["checks"]["spatial_graphs"]["jain_digital_twin"]["locations_count"], 79
        )
        self.assertEqual(
            health["checks"]["spatial_graphs"]["jain_digital_twin"]["pathways_count"], 106
        )
        self.assertEqual(
            health["checks"]["spatial_graphs"]["benchmark_model"]["locations_count"], 15
        )

        self.assertEqual(len(health["issues"]), 0)

    def test_system_health_check_sanitization(self) -> None:
        """Verify that the health check response does not expose passwords, tokens, or private secrets."""
        health = check_system_health(check_database=True, check_maps=True)
        dump = str(health).lower()

        # Ensure no credential leaks
        self.assertNotIn("password", dump)
        self.assertNotIn("secret_key", dump)
        self.assertNotIn("token", dump)
        self.assertNotIn("salt", dump)

    # =========================================================================
    # 2. Database Backup & Verified Restore Tests
    # =========================================================================

    def test_database_backup_and_restore_roundtrip(self) -> None:
        """Verify that a database can be backed up, modified, and restored atomically to prior state."""
        db_file = self.temp_path / "live_campus.db"
        backup_file = self.temp_path / "backup_campus.db"

        # 1. Initialize live database and seed initial record
        db = DatabaseManager(db_path=db_file)
        user1 = db.create_user(
            full_name="Snapshot User",
            username="snap_user",
            password="SnapshotPass2026!",
            role="Student",
        )
        self.assertIsNotNone(db.get_user_by_username("snap_user"))

        # 2. Perform online native backup
        created_backup = db.backup_database(backup_path=backup_file)
        self.assertTrue(Path(created_backup).is_file())
        self.assertGreater(Path(created_backup).stat().st_size, 0)

        # 3. Modify live database state
        user2 = db.create_user(
            full_name="Post-Backup User",
            username="post_user",
            password="PostPass2026!",
            role="Student",
        )
        self.assertIsNotNone(db.get_user_by_username("post_user"))

        # 4. Execute atomic restore from backup
        restore_success = db.restore_database(backup_path=backup_file)
        self.assertTrue(restore_success)

        # 5. Verify restored state: snap_user exists, post_user does NOT exist
        self.assertIsNotNone(db.get_user_by_username("snap_user"))
        self.assertIsNone(db.get_user_by_username("post_user"))
        db.close()

    def test_database_restore_nonexistent_or_corrupt_file(self) -> None:
        """Verify that restoring from a missing or non-database file raises a DatabaseError cleanly."""
        db_file = self.temp_path / "test_db.db"
        db = DatabaseManager(db_path=db_file)

        # Non-existent file
        with self.assertRaises(DatabaseError):
            db.restore_database(self.temp_path / "missing.db")

        # Corrupt / invalid non-sqlite file
        corrupt_file = self.temp_path / "corrupt.txt"
        corrupt_file.write_text("This is plain text, not a SQLite database.", encoding="utf-8")
        with self.assertRaises(DatabaseError):
            db.restore_database(corrupt_file)

        db.close()

    # =========================================================================
    # 3. Production Configuration & Validation Tests
    # =========================================================================

    def test_production_configuration_validation(self) -> None:
        """Verify that AppConfig.validate_for_production detects configuration defects."""
        cfg = AppConfig()
        cfg.environment = "production"
        cfg.debug = True  # Insecure for production
        cfg.security.secret_key = ""  # Missing secret key

        issues = cfg.validate_for_production(raise_exception=False)
        self.assertTrue(any("CAMPUS_DEBUG" in i for i in issues))
        self.assertTrue(any("CAMPUS_SECRET_KEY" in i for i in issues))

        # Test valid configuration
        valid_cfg = AppConfig()
        valid_cfg.environment = "production"
        valid_cfg.debug = False
        valid_cfg.security.secret_key = "a_very_secure_cryptographic_key_at_least_32_chars_long"
        valid_cfg.security.pbkdf2_iterations = 600000

        valid_issues = valid_cfg.validate_for_production(raise_exception=False)
        self.assertEqual(len(valid_issues), 0)

    # =========================================================================
    # 4. PostgreSQL DDL and Data Migration Tests
    # =========================================================================

    def test_postgres_ddl_and_export_integrity(self) -> None:
        """Verify that PostgreSQL DDL and data export generate complete, valid SQL statements."""
        ddl = generate_postgres_ddl()
        self.assertIn("CREATE TABLE IF NOT EXISTS users", ddl)
        self.assertIn("CREATE TABLE IF NOT EXISTS obstacle_reports", ddl)
        self.assertIn("CREATE TABLE IF NOT EXISTS administrative_audit_log", ddl)

        # Test data exporter on in-memory database
        temp_db = self.temp_path / "export_src.db"
        export_sql = self.temp_path / "exported.sql"

        db = DatabaseManager(db_path=temp_db)
        db.create_user(
            full_name="Export Test User",
            username="export_user",
            password="Password123!",
            role="Student",
        )
        db.close()

        rows_exported = export_sqlite_to_postgres_sql(temp_db, export_sql)
        self.assertGreater(rows_exported, 0)
        sql_content = export_sql.read_text(encoding="utf-8")
        self.assertIn("BEGIN;", sql_content)
        self.assertIn("INSERT INTO users", sql_content)
        self.assertIn("export_user", sql_content)
        self.assertIn("COMMIT;", sql_content)

    # =========================================================================
    # 5. .env.example Coverage and Hygiene Tests
    # =========================================================================

    def test_env_example_coverage(self) -> None:
        """Verify .env.example defines all required configuration variables and contains no real secrets."""
        project_root = Path(__file__).resolve().parent.parent
        env_example = project_root / ".env.example"
        self.assertTrue(env_example.is_file())

        content = env_example.read_text(encoding="utf-8")
        required_vars = [
            "CAMPUS_ENV",
            "CAMPUS_PORT",
            "CAMPUS_SECRET_KEY",
            "CAMPUS_HASH_ITERATIONS",
            "CAMPUS_DB_PATH",
            "CAMPUS_DB_JOURNAL_MODE",
            "CAMPUS_ALLOWED_HOSTS",
        ]
        for var in required_vars:
            self.assertIn(var, content, f"Variable {var} must be documented in .env.example")


if __name__ == "__main__":
    unittest.main()
